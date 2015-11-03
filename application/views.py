from flask import render_template, request, url_for, redirect, current_app, jsonify, flash, session, g
from flask.ext.login import login_user, logout_user, current_user, login_required
from application import app, nav, db, login_manager
from .forms import LoginForm, RegistrationForm
from .models import User, CustomDemoIP

import re
from collections import defaultdict

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
    
    
def get_demo_sample_assets(user, form_dict = None):
    """
    TODO: query the database
    """    
    account_cats = get_demo_account_categories()
    default_assets = get_demo_account_default_assets()
        
    # Determine the assets for the given user id
    if user.email == 'ywp@demo.com':
        asset_values = {
            'Banking': [('Savings', 60000)],
            'Brokerage': [('Money Market (1%)', 20000), ('AAPL', 10000)],
            '401(k)': [('SPY', 20000), ('EEM', 5000)],
            'Real Assets': [('House', 200000), ('Mortgage', -150000)]
        }
        
    elif user.email == 'nr@demo.com':
        asset_values = {
            'Banking': [('Savings', 600000)],
            'Brokerage': [('Money Market (1%)', 200000), ('AAPL', 100000)],
            '401(k)': [('SPY', 200000), ('EEM', 50000)],
            'Real Assets': [('House', 2000000), ('Mortgage', -1500000)]
        }
        
    elif user.email == 'fof@demo.com':
        asset_values = {
            'Banking': [('Savings', 500000)],
            'Brokerage': [('Money Market (1%)', 200000), ('AAPL', 100000)],
            '401(k)': [('SPY', 200000), ('EEM', 50000)],
            'Real Assets': [('House', 2000000), ('Mortgage', -1500000)]
        }
        
    elif user.email == 'custom@demo.com':
    
        if form_dict is None:
            raise Exception("Missing form data") #TODO: change this
            
        # Load in the values for each of the assets in order
        asset_keys = sorted([key for key in form_dict if re.match("input_\d_\d", key)])
        # Convert the text in the boxes to integers
        custom_assets_values = [int(form_dict.get(asset_key, 0)) for asset_key in asset_keys]
        
        # Set all assets to default assets so we know the names, etc.
        asset_values = defaultdict(list)
        for account_cat in account_cats:
            default_assets_cat = default_assets.get(account_cat)
            assets = []
            for asset_name in default_assets_cat:
                asset_values[account_cat].append( (asset_name, custom_assets_values.pop(0)) )
                
        # TODO: save these custom asset values down, so that we can examine our userbase
        
    else:
         raise Exception("Unknown user email: %s" %user.email) #TODO: change this (handle users)
       
    account_categories = []
    for acct_ndx in range(len(account_cats)):
        account_cat = account_cats[acct_ndx]
        assets = default_assets[account_cat]
    
        out_asset_list = [{
                'label': assets[asset_ndx],
                'id': 'input_%d_%d' %(acct_ndx, asset_ndx),
                'amount':  asset_values[account_cat][asset_ndx][1]
            } for asset_ndx in range(len(assets))]
        
        account_category = {
            'heading': account_cat,
            'heading_id': 'account_cat_head_%d' %acct_ndx,
            'id': 'account_cat_%d' %acct_ndx,
            'asset_sum': sum([a.get('amount') for a in out_asset_list]),
            'assets': out_asset_list
        }
        account_categories.append(account_category)
    
    return account_categories
    
def make_custom_demo_account(form_dict, ip_addr):
    
    account_cats = get_demo_account_categories()
    default_assets = get_demo_account_default_assets()

    if form_dict is None:
        raise Exception("Missing form data") #TODO: change this
        
    # Load in the values for each of the assets in order
    asset_keys = sorted([key for key in form_dict if re.match("input_\d_\d", key)])
    # Convert the text in the boxes to integers
    custom_assets_values = [int(form_dict.get(asset_key, 0)) for asset_key in asset_keys]
    
    # Set all assets to default assets so we know the names, etc.
    asset_values = defaultdict(list)
    for account_cat in account_cats:
        default_assets_cat = default_assets.get(account_cat)
        assets = []
        for asset_name in default_assets_cat:
            asset_values[account_cat].append( (asset_name, custom_assets_values.pop(0)) )
            
    custom_demo_ip = CustomDemoIP(ip_addr)
    db.session.add(custom_demo_ip)
    db.session.commit()
    
    # app.logger.info('Custom user id: %s' %str(custom_demo_ip.get_id()))
    
    new_custom_id = custom_demo_ip.get_id()
    # TODO: remove these hardcodes
    new_custom_user = User('custom%s@customdemo.com' %str(new_custom_id), 
                                                'demo123', 'Custom', is_demo=True, is_custom=True)
    
    db.session.add(new_custom_user)
    db.session.commit()
    
    return new_custom_user.get_id()
    
    
    
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
    
    
    
    
    
@app.route('/demo', methods = ['GET', 'POST'])
# TODO: needs much better user handling
def demo():
    # app.logger.info('demo')
    
    if request.method == 'POST':
        form_dict = request.form
    
        # app.logger.info('Select field changed: %s' % request.form['select-changed'])
        if form_dict.get('select-changed') == 'yes':
            user_id = form_dict.get('select-cohort')
        else:
            ip_addr = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
            user_id = make_custom_demo_account(form_dict, ip_addr)
            
    else:
        form_dict = None
        # on the demo page, default to young working professional
        user_id = get_user_by_email('ywp@demo.com').get_id()
        
     # Log in the demo user
    user = get_user_by_id(user_id)
    login_user(user, remember=False)
    
    # Get the account assets for plotting
    account_categories = get_demo_sample_assets(current_user, form_dict)
    
    # app.logger.info('Demo user id: %s' %str(current_user.email))
    
    # Add up the net worth from the assets
    net_worth = 0
    for account_cat  in account_categories:
        for asset in account_cat.get('assets'):
            net_worth += asset.get('amount', 0)
    
    demo_accounts =  get_demo_accounts()
        
    kwargs = {
        'account_categories': account_categories, 
        'demo_accounts': demo_accounts,
        'user_id': int(user_id),
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