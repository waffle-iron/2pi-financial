from flask import render_template, request, url_for, redirect, current_app, jsonify, flash, session, g
from flask.ext.login import login_user, logout_user, current_user, login_required
from application import app, nav, db, login_manager

from sqlalchemy import func

from .forms import LoginForm, RegistrationForm

from .models import User, CustomDemoIP, Asset, AssetPosition, AccountCategory, Account, UserAccount, create_new_demo_asset

import re


# TODO: sort accounts
# TODO: optimize queries

# NOTE: how do we deal with negative values in the pie


# Navigation bars
nav.Bar('loggedin', [
    nav.Item('Home', 'home'),
    nav.Item('Demo', 'demo'),
    nav.Item('Logout', 'logout')
])

nav.Bar('loggedout', [
    nav.Item('Demo', 'demo'),
    nav.Item('Login', 'login'),
    nav.Item('Register', 'register')
])


#
# DATA ACCESS FUNCTIONS
#
    
def query_result_to_dict(q_result):
    """
    Take the result of a query through SqlAlchemy 
    and convert it into a dictionary
    """
    return [dict(zip(row.keys(), row)) for row in q_result]
   

# USER ACCESS

def get_user_by_id(user_id):
    return User.query.get(user_id)
   
   
def get_user_by_email(email):
    return User.query.filter(User.email == email).first()
    
    
def get_default_custom_demo_user():
    return get_user_by_email('custom@demo.com')
    
    
# DEMO ACCOUNTS
 
def make_custom_demo_user(form_dict, ip_addr):
    """
    Given input from the demo side bar form, create a custom new demo account
    with the specified assets, etc.
    """
    if form_dict is None:
        raise Exception("Missing form data") #TODO: change this
        
    # Get the information that will need to be filled in
    account_cats = get_demo_account_categories()
    default_assets = get_demo_account_default_assets()

    # Add a new custom user
    custom_demo_ip = CustomDemoIP(ip_addr)
    db.session.add(custom_demo_ip)
    db.session.commit()
    
    app.logger.info('Custom user ID added: %s' %str(custom_demo_ip.id))
    
    # Get the default positions for a custom user
    default_custom_user = get_default_custom_demo_user()
    
    default_custom_user_positions = get_user_positions(default_custom_user)
    
    new_custom_id = custom_demo_ip.id
    # TODO: remove these hardcodes
    new_custom_user = User('custom%s@customdemo.com' %str(new_custom_id), 
                                                'demo123', 'Custom', is_demo=True, is_custom=True)
                                                
    # Load up the positions for this new user
    account_keys = [key for key in form_dict if re.match("input_\d_\d", key)]
    
    user_accounts = []
    
    # Iterate through the accounts, adding positions
    for acct_key in account_keys:
        split_str = acct_key.split('_')
        account_cat_id = int(split_str[1])
        account_id = int(split_str[2])
    
        user_account = UserAccount(Account.query.get(account_id))
    
        # Convert the text in the boxes to integers
        acct_value = int(float(form_dict.get(acct_key, 0)))
        
        # Add in the positions according to the default custom user
        new_positions = []
        for def_pos in default_custom_user_positions:
            if def_pos.account_id == account_id:
                new_position = AssetPosition(def_pos.Asset, acct_value)
                new_positions.append(new_position)
                
        if len(new_positions) > 1:
            raise Exception("There were more than 1 asset assigned to an account for a custom demo user.")
        
        user_account.positions = new_positions
        
        user_accounts.append(user_account)
        
    new_custom_user.user_accounts = user_accounts   
    
    db.session.add(new_custom_user)
    db.session.commit()
        
    return new_custom_user
   
   
def get_demo_account_categories():
    """
    Return the account categories for the side bar
    """
    return ['Banking', 'Brokerage', '401(k)', 'Real Assets']
    
    
def get_demo_account_default_assets():
    """
    Return the assets that are associated with each demo account
    """
    default_assets = {
        'Banking': ['Savings'],
        'Brokerage': ['Money Market (1%)', 'AAPL'],
        '401(k)': ['SPY', 'EEM'],
        'Real Assets': ['House', 'Mortgage']
    }
    return default_assets
    
    
def get_demo_accounts(include_custom = False):
    """
    Get all of the demo accounts (filtering out custom demo accounts if wanted)
    """
    return User.query.filter(User.is_demo == True, 
                                            User.is_custom == include_custom).all()
                                            
    
# USER POSITIONS       

def get_user_asset_class_summary(user):
    """
    Given a user, return a summary of his positions summarised
    across Asset Class
    @return: two columns (AssetClass, value)
    """
    app.logger.info("Getting asset class summary for: %s -- %s" %(user.email, str(user.id)))

    out = db.session.query(
        Asset.asset_class.label('asset_class'),
        func.sum(AssetPosition.value).label('value')). \
    join(AssetPosition). \
    join(UserAccount). \
    group_by(Asset.asset_class). \
    filter(UserAccount.user_id == user.id). \
    all()
    
    return out

    
def get_user_account_summary(user):
    """
    Given a user, return a summary of his positions summarised
    by User Account with other meta information
    @return: 6 columns (id, account_id, account_name, accountegory_id,
                                       account_category_name, value)
    """
    app.logger.info("Getting user account summary for: %s -- %s" %(user.email, str(user.id)))
    
    out = db.session.query(
            UserAccount.id.label('id'),
            Account.id.label('account_id'),
            Account.account_name.label('account_name'),
            AccountCategory.id.label('account_category_id'),
            AccountCategory.account_category_name.label('account_category_name'),
            func.sum(AssetPosition.value).label('value')). \
        join(AssetPosition). \
        join(Account). \
        join(AccountCategory). \
        group_by(UserAccount, Account, AccountCategory). \
        filter(UserAccount.user_id == user.id). \
        all()
        
    return out
 
 
def get_user_positions(user):
    """
    Given a user, return each of his positions
    @return: AssetPosition, Asset, account_id, user_id
    """
    app.logger.info("Getting positions for: %s -- %s" %(user.email, str(user.id)))

    out = db.session.query(
            AssetPosition,
            Asset,
            UserAccount.account_id,
            UserAccount.user_id). \
        join(Asset). \
        join(UserAccount). \
        filter(UserAccount.user_id == user.id). \
        all()
    # app.logger.info(out[0].keys())
    return out
    

# MANIPULATING DATA INTO DIGESTIBLE FORMS
   
def configure_account_category_output(user_account_summary):
    """
    Take the user account summary and output a data structure that will be 
    used by the HTML template for displaying account values
    """
    # TODO: order the accounts better

    # Get the unique account categories
    account_cats = list(set([a_summary.account_category_id for a_summary in user_account_summary]))
     
    account_categories = []
    for acct_cat_id in account_cats:
    
        # Get the category name
        acct_cat_name = None
        for a_summary in user_account_summary:
            if a_summary.account_category_id == acct_cat_id:
                acct_cat_name = a_summary.account_category_name
                break
                
        # Get all of accounts that are associated with the account category
        sub_accounts = [(a_summary.account_id, a_summary.account_name, a_summary.value) 
                                for a_summary in user_account_summary
                                if a_summary.account_category_id == acct_cat_id]
                                
        # JSON for the accounts
        out_account_list = [{
                'label': acct[1],
                'id': 'input_%d_%d' %(acct_cat_id, acct[0]),
                'value':  int(acct[2])
            } for acct in sub_accounts]
            
        # JSON for the account category
        account_category = {
            'heading': acct_cat_name,
            'heading_id': 'account_cat_head_%d' %acct_cat_id,
            'id': 'account_cat_%d' %acct_cat_id,
            'account_sum': int(sum([a.get('value') for a in out_account_list])),
            'accounts': out_account_list
        }
        account_categories.append(account_category)
        
    return account_categories
  
  
def calculate_user_networth(user_account_summary):
    """
    Given a user accounts' summary, calculate his networth by simply adding
    the accounts' value together
    """
    networth = 0
    for act in user_account_summary:
        networth += act.value
        
    return int(networth)
    
    
#
# VIEWS
#    

@login_manager.user_loader
def load_user(user_id):
    """
    Method required by Flask-Login
    """
    return User.query.get(user_id)
    
    
@app.before_request
def before_request():
    """
    Set the global enviornment class' user to the current user
    """
    g.user = current_user
    
    
@app.route('/')
def home():
    """
    Home page -
    """
    return render_template('home.html')

    
@app.route('/chart_data.json')
def chart_data():
    """
    Output the data required to make the charts as JSON
    """
    asset_class_summary = get_user_asset_class_summary(current_user)        
    asset_class_summary = query_result_to_dict(asset_class_summary)
        
    return jsonify(asset_class_summary = asset_class_summary)
    
    
@app.route('/demo', methods = ['GET', 'POST'])
def demo():
    """
    Render the demo page, which takes both GET and POST requests
    GET requests should return the current user's profile
    POST requests evaluate the data from the post and output the corresponding user
    """
    # app.logger.info('demo')
    
    if request.method == 'POST':
        # Load in the data in the POST request's form
        form_dict = request.form
    
        # app.logger.info('Select field changed: %s' % request.form['select-changed'])
        # If the default select list has been changed
        if form_dict.get('select-changed') == 'yes':
            form_user_id = form_dict.get('select-cohort')
            # Get the user by its ID in the database
            user = get_user_by_id(form_user_id)
        else:
            # Get the user's IP address for logging and create a new demo account
            ip_addr = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
            user = make_custom_demo_user(form_dict, ip_addr)
    else:
        try:
            # Try getting the current user
            user = get_user_by_email(current_user.email)
        except:
            # On the demo page, default to young working professional
            user = get_user_by_email('ywp@demo.com')
            
    # Log in the demo user
    login_user(user, remember=False)
    # app.logger.info('Demo user: %s' %str(current_user.email))
    
    # Get the account assets for the user for the side bar inputs
    user_accounts = get_user_account_summary(current_user)
    
    # Add up the net worth from the users account
    net_worth = calculate_user_networth(user_accounts)
    
    # Transform the user account summary into digestible fields
    account_categories = configure_account_category_output(user_accounts)
    
    # Get the default demo accounts for the select list
    demo_users =  get_demo_accounts()
    
    # Check to see if it's a custom user
    form_user_id = user.id
    if form_user_id not in [d_user.id for d_user in demo_users]:
        form_user_id = get_default_custom_demo_user().id
        
    kwargs = {
        'account_categories': account_categories, 
        'demo_users': demo_users,
        'user_id': int(form_user_id), # This is simply used for display purposes
        'net_worth': net_worth
    }
    
    return render_template('demo.html', **kwargs)

    
@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    Default registration view 
    """
    # If a user is already logged in
    if g.user is not None and g.user.is_authenticated:
        return redirect(url_for('home'))
        
    # Load in the WTF form
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User()
        form.populate_obj(user)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html', form=form)
 
 
@app.route('/login',methods=['GET','POST'])
def login():
    """
    Default login view 
    """
    # If a user is already logged in
    if g.user is not None and g.user.is_authenticated:
        return redirect(url_for('home'))
        
    # Load in the WTF form
    form = LoginForm()
    if form.validate_on_submit():
        session['remember_me'] = form.remember_me.data
        
        login_user(form.user, remember=form.remember_me.data)
        
        flash('Login successful for email="%s"' % form.email.data)
        
        return redirect(request.args.get('next') or url_for('home')) 
        
    return render_template('login.html',  form=form)
    
    
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login')) 
    
    
# @app.route('/contact')
# def about():
    # return render_template('contact_us.html')
    
    
# @app.route('/faq')
# def about():
    # return render_template('faq.html')
    
    
# @app.route('/about')
# def about():
    # return render_template('about.html')
    
    
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404