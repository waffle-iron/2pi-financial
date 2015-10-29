from flask import render_template, request, url_for, redirect, current_app
from .app import app

import re
from collections import defaultdict

@app.route('/')
def home():
    return render_template('home.html')
   

def get_demo_sample_assets(user_id, form_dict = None):
    """
    TODO: query the database
    """
    account_cats = ['Banking', 'Brokerage', '401(k)', 'Real Assets']
    
    default_assets = {
        'Banking': ['Savings'],
        'Brokerage': ['Money Market (1%)', 'AAPL'],
        '401(k)': ['SPY', 'EEM'],
        'Real Assets': ['House', 'Mortgage']
    }
        
    # Determine the assets for the given user id
    if user_id == 'ywp':
        asset_values = {
            'Banking': [('Savings', 60000)],
            'Brokerage': [('Money Market (1%)', 20000), ('AAPL', 10000)],
            '401(k)': [('SPY', 20000), ('EEM', 5000)],
            'Real Assets': [('House', 200000), ('Mortgage', -150000)]
        }
        
    elif user_id == 'nr':
        asset_values = {
            'Banking': [('Savings', 600000)],
            'Brokerage': [('Money Market (1%)', 200000), ('AAPL', 100000)],
            '401(k)': [('SPY', 200000), ('EEM', 50000)],
            'Real Assets': [('House', 2000000), ('Mortgage', -1500000)]
        }
        
    elif user_id == 'fof':
        asset_values = {
            'Banking': [('Savings', 500000)],
            'Brokerage': [('Money Market (1%)', 200000), ('AAPL', 100000)],
            '401(k)': [('SPY', 200000), ('EEM', 50000)],
            'Real Assets': [('House', 2000000), ('Mortgage', -1500000)]
        }
        
    elif user_id == 'custom':
    
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
         raise Exception("Unknown user id: %s" %str(user_id)) #TODO: change this
       
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
    
   
@app.route('/demo', methods = ['GET', 'POST'])
def demo():
    # app.logger.info('demo')
    
    if request.method == 'POST':
        form_dict = request.form
    
        app.logger.info(request.form['select-changed'])
        if form_dict.get('select-changed') == 'yes':
            user_id = form_dict.get('select-cohort')
        else:
            user_id = 'custom'
            
        account_categories = get_demo_sample_assets(user_id, form_dict)
            
    else:
        user_id = 'ywp'
        account_categories = get_demo_sample_assets(user_id)
    
    # add up the net worth from the assets
    net_worth = 0
    for account_cat  in account_categories:
        for asset in account_cat.get('assets'):
            net_worth += asset.get('amount', 0)
    
    sample_accounts = {
        'ywp': 'Young working professional',
        'fof': 'Family of 4',
        'nr': 'Nearing retirement',
        'custom': 'Custom'}
    
    kwargs = {
        'account_categories': account_categories, 
        'sample_accounts': sample_accounts,
        'user_id': user_id,
        'net_worth': net_worth
    }
    
    return render_template('demo.html', **kwargs)

    
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