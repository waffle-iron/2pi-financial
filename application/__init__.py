#TODO: put these inits and other hardcoded text in separate config files (JSON?)

from flask import Flask, url_for
from flask_sqlalchemy import SQLAlchemy
from flask.ext.assets import Environment, Bundle
from flask.ext.login import LoginManager, UserMixin, login_required
from flask.ext.navigation import Navigation
import os

import logging

# Configure our app and database from the file
app = Flask(__name__)
app.config.from_object('config')
app.secret_key = app.config['SECRET_KEY']

# Set up logging
file_handler = logging.FileHandler('app.log')
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)

app.logger.info('Enviornment: %s' %app.config['ENV'])

# Function to easily find your assets
# In your template use <link rel=stylesheet href="{{ static('filename') }}">
app.jinja_env.globals['static'] = (
    lambda filename: url_for('static', filename = filename)
)

# setup assets
assets = Environment(app)
assets.url_expire = False
assets.debug = app.config['ENV'] == 'development'
assets.load_path = ['%s/static' % app.config.root_path]

assets.register('css',
    Bundle(
      'css/vendor/*.css',
      'css/*.css',
        # Bundle( 'css/*.scss', filters='pyscss', output='css/app.%(version)s.css'),
      output='css/app.%(version)s.css'))

# Bundle these in a specific order for dependency reasons
assets.register('js', Bundle(
    'js/vendor/jquery/jquery.js',
    'js/vendor/d3/d3.min.js',
    'js/vendor/nvd3/nv.d3.min.js',
    'js/vendor/*.js',
    'js/*.js',
    output='js/app.%(version)s.js'))
    
# Load up the database
db = SQLAlchemy(app)

app.logger.info('SQL Alchemy loaded')

# For the navigation bar
nav = Navigation(app)

from application import views, models, auth

# Initialize the login manager
from auth import login_manager
login_manager.init_app(app)

# Initialization of the application
from models import User, Asset, AssetPosition, AccountCategory, Account, UserAccount, create_new_demo_asset

@app.before_first_request
def setup():
    # TODO: move these configurations to a file(s)
    # Recreate database each time for demo
    db.drop_all() # TODO: remove
    db.create_all()
    
    demo_account_categories = ['Banking', 'Brokerage', '401(k)', 'Real Assets']
    
    demo_accounts = {
        'Banking': ['Savings'],
        'Brokerage': ['Money Market (1%)', 'AAPL'],
        '401(k)': ['SPY', 'EEM'],
        'Real Assets': ['House', 'Mortgage']
    }
    
    demo_users = [
        ('ywp@demo.com', 'demo123', 'Young working professional'),
        ('fof@demo.com', 'demo123', 'Family of 4'),
        ('nr@demo.com', 'demo123', 'Nearing retirement'),
        ('custom@demo.com', 'demo123', 'Custom')        
    ]
    
    demo_assets = {
        'savings_demo1': {'asset_name': 'savings_demo1', 'asset_class': 'Cash', 'is_demo': True},
        'moneymarket_demo1': {'asset_name': 'moneymarket_demo1', 'asset_class': 'Cash', 'is_demo': True},
        'aapl_demo1': {'asset_name': 'aapl_demo1', 'asset_class': 'US Equity', 'is_demo': True},
        'spy_demo1': {'asset_name': 'spy_demo1', 'asset_class': 'US Equity', 'is_demo': True},
        'eem_demo1': {'asset_name': 'eem_demo1', 'asset_class': 'EM Equity', 'is_demo': True},
        'house_demo1': {'asset_name': 'house_demo1', 'asset_class': 'Real Estate', 'is_demo': True},
        'mortgage_demo1': {'asset_name': 'mortgage_demo1', 'asset_class': 'Real Estate', 'is_demo': True}   
    }
    
    demo_positions = {
        'ywp@demo.com': {
            'Banking': {'Savings':  [('savings_demo1', 60000)]},
            'Brokerage': {'Money Market (1%)': [('moneymarket_demo1', 20000)], 'AAPL': [('aapl_demo1', 10000)]},
            '401(k)': {'SPY': [('spy_demo1', 20000)], 'EEM': [('eem_demo1', 5000)]},
            'Real Assets': {'House': [('house_demo1', 200000)], 'Mortgage': [('mortgage_demo1', -150000)]}
        },

        'nr@demo.com': {
            'Banking': {'Savings':  [('savings_demo1', 60001)]},
            'Brokerage': {'Money Market (1%)': [('moneymarket_demo1', 20001)], 'AAPL': [('aapl_demo1', 10001)]},
            '401(k)': {'SPY': [('spy_demo1', 20001)], 'EEM': [('eem_demo1', 5001)]},
            'Real Assets': {'House': [('house_demo1', 200001)], 'Mortgage': [('mortgage_demo1', -150001)]}
        },
        
        'fof@demo.com': {
            'Banking': {'Savings':  [('savings_demo1', 60002)]},
            'Brokerage': {'Money Market (1%)': [('moneymarket_demo1', 20002)], 'AAPL': [('aapl_demo1', 10002)]},
            '401(k)': {'SPY': [('spy_demo1', 20002)], 'EEM': [('eem_demo1', 5002)]},
            'Real Assets': {'House': [('house_demo1', 200002)], 'Mortgage': [('mortgage_demo1', -150002)]}
        },

        'custom@demo.com': {
            'Banking': {'Savings':  [('savings_demo1', 60003)]},
            'Brokerage': {'Money Market (1%)': [('moneymarket_demo1', 20003)], 'AAPL': [('aapl_demo1', 10003)]},
            '401(k)': {'SPY': [('spy_demo1', 20003)], 'EEM': [('eem_demo1', 5003)]},
            'Real Assets': {'House': [('house_demo1', 200003)], 'Mortgage': [('mortgage_demo1', -150003)]}
        }
    }
    
    
    for dac in demo_account_categories:
        account_cat = AccountCategory(dac)
        db.session.add(account_cat)
        for da in demo_accounts.get(dac):
            account = Account(da, account_cat)
            db.session.add(account)
    
    # Set up each of the demo accounts with positions, etc.
    for demo_user in demo_users:
        d_email = demo_user[0]
        app.logger.info('Adding demo user: %s' %d_email)
        user = User(d_email, demo_user[1], demo_user[2], is_demo=True)
    
        user_accounts = []
    
        positions_dict = demo_positions.get(d_email)
    
        # Iterate through the positions in all of the accounts
        for account_cat, account_cat_dict in positions_dict.iteritems():
            for account_name, position_tuples in account_cat_dict.iteritems():
                # app.logger.info('Adding demo account: %s' %account_name)
                # Create user accounts
                account = db.session.query(Account).filter(Account.account_name == account_name).first()
                user_account = UserAccount(account)
                
                account_positions = []
            
                for position_tuple in position_tuples:
                    # Add positions
                    asset_name = position_tuple[0]
                    position_value = position_tuple[1]
                    # app.logger.info('Adding position: %s' %asset_name)
        
                    # Check to see if the asset is already created, if not, create it
                    asset = db.session.query(Asset).filter(Asset.asset_name == asset_name).first()
                    if not asset:
                        # app.logger.info('Adding asset: %s' %asset_name)
                        asset_info = demo_assets.get(asset_name)
                        asset = create_new_demo_asset(**asset_info)

                    # Now that the position is properly instantiated, add it to the user account's positions
                    new_position = AssetPosition(asset, position_value)
                    db.session.add(new_position)
                    db.session.commit()
                    
                    account_positions.append(new_position)
        
                # Add the positions list to the user account
                user_account.positions = account_positions
                # Append the user account to the user now that all the positions have been added
                user_accounts.append(user_account)
                
        # Add the list of accounts to the user
        user.user_accounts = user_accounts
        
        # Add the user and everything that is attached to it (accounts, positions)
        db.session.add(user)
        db.session.commit()
        
    
    
    
    