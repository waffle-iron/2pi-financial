from flask import render_template, request, url_for, redirect, current_app, jsonify, flash, session, g
from flask.ext.login import login_user, logout_user, current_user, login_required
from application import app, nav, db, login_manager

from sqlalchemy import func

from .forms import LoginForm, RegistrationForm

from .models import User, CustomDemoIP, Asset, AssetPosition, AccountCategory, Account, UserAccount, create_new_demo_asset

import re

# TODO: comments
# TODO: sort accounts

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


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)
    
@app.before_request
def before_request():
    g.user = current_user
    
    
@app.route('/')
def home():
    return render_template('home.html')
   

@app.route('/chart_data.json')
def chart_data():
    """
    Output the data required to make the charts
    """
    account_categories = get_demo_sample_assets(current_user)

    return jsonify(results = account_categories)
    
    
    
#
# DATA ACCESS
#
    
def get_demo_account_categories():
    return ['Banking', 'Brokerage', '401(k)', 'Real Assets']
    
def get_demo_account_default_assets():
    default_assets = {
        'Banking': ['Savings'],
        'Brokerage': ['Money Market (1%)', 'AAPL'],
        '401(k)': ['SPY', 'EEM'],
        'Real Assets': ['House', 'Mortgage']
    }
    return default_assets
    
def get_demo_accounts(include_custom = False):
    return User.query.filter(User.is_demo == True, User.is_custom == include_custom).all()
    
def get_user_by_id(user_id):
    return User.query.get(user_id)
   
def get_user_by_email(email):
    return User.query.filter(User.email == email).first()
    
def get_user_account_summary(user):
    # TODO: fix query
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
    
def get_custom_demo_asset(custom_demo_asset_name = 'Demo'):
    demo_asset = db.session.query(Asset).\
        filter(Asset.asset_name == custom_demo_asset_name, Asset.asset_class == 'Demo').\
        first()
    if not demo_asset:
        demo_asset = create_new_demo_asset(custom_demo_asset_name)
    return(demo_asset)    
    
def make_custom_demo_user(form_dict, ip_addr):
    
    account_cats = get_demo_account_categories()
    default_assets = get_demo_account_default_assets()

    if form_dict is None:
        raise Exception("Missing form data") #TODO: change this
      
    # Add a new custom user
    custom_demo_ip = CustomDemoIP(ip_addr)
    db.session.add(custom_demo_ip)
    db.session.commit()
      
    # app.logger.info('Custom user id: %s' %str(custom_demo_ip.id))
    
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
        
        # Get the generic demo asset
        demo_asset = get_custom_demo_asset()
        
        new_position = AssetPosition(demo_asset, acct_value)
        db.session.add(new_position)
        
        user_account.positions = [new_position]
        
        user_accounts.append(user_account)
        
    new_custom_user.user_accounts = user_accounts   
    
    db.session.add(new_custom_user)
    db.session.commit()
        
    return new_custom_user
    
def configure_account_category_output(user_account_summary):

    # TODO: order the accounts better

    # Get the unique categories
    account_cats = list(set([a_summary.account_category_id for a_summary in user_account_summary]))
     
    account_categories = []
    for acct_cat_id in account_cats:
    
        # Get the category name
        acct_cat_name = None
        for a_summary in user_account_summary:
            if a_summary.account_category_id == acct_cat_id:
                acct_cat_name = a_summary.account_category_name
                break
                                
        sub_accounts = [(a_summary.account_id, a_summary.account_name, a_summary.value) for a_summary in user_account_summary
                                if a_summary.account_category_id == acct_cat_id]
                                
        out_account_list = [{
                'label': acct[1],
                'id': 'input_%d_%d' %(acct_cat_id, acct[0]),
                'value':  int(acct[2])
            } for acct in sub_accounts]
            
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
    networth = 0
    for act in user_account_summary:
        networth += act.value
        
    return int(networth)
    
    
@app.route('/demo', methods = ['GET', 'POST'])
# TODO: needs much better user handling
def demo():
    # app.logger.info('demo')
    
    if request.method == 'POST':
        form_dict = request.form
    
        # app.logger.info('Select field changed: %s' % request.form['select-changed'])
        if form_dict.get('select-changed') == 'yes':
            form_user_id = form_dict.get('select-cohort')
            user = get_user_by_id(form_user_id)
        else:
            ip_addr = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
            user = make_custom_demo_user(form_dict, ip_addr)
            # Set the form's user id to a generic custom (for display purposes)
            form_user_id = get_user_by_email('custom@demo.com').id
            
    else:
        form_dict = None
        # on the demo page, default to young working professional
        user = get_user_by_email('ywp@demo.com')
        form_user_id = user.id
        
     # Log in the demo user
    login_user(user, remember=False)
    
    # Get the account assets for display
    user_accounts = get_user_account_summary(current_user)
    
    # app.logger.info('Demo user id: %s' %str(current_user.email))
    
    # Add up the net worth from the assets
    net_worth = calculate_user_networth(user_accounts)
    
    # Transform the user account summary into HTML readable fields
    account_categories = configure_account_category_output(user_accounts)
    
    demo_users =  get_demo_accounts()
    
    kwargs = {
        'account_categories': account_categories, 
        'demo_users': demo_users,
        'user_id': int(form_user_id), # This is simply used for display purposes
        'net_worth': net_worth
    }
    
    return render_template('demo.html', **kwargs)

    
@app.route('/register', methods=['GET', 'POST'])
def register():
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
    # If a user is already logged in
    if g.user is not None and g.user.is_authenticated:
        return redirect(url_for('home'))
        
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