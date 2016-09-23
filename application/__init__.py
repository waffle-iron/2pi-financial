#TODO: put these inits and other hardcoded text in separate config files (JSON?)

from flask import Flask, url_for
from flask_sqlalchemy import SQLAlchemy
from flask.ext.assets import Environment, Bundle
from flask.ext.login import LoginManager, UserMixin, login_required
from flask.ext.navigation import Navigation
import os
import json

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
from models import User, Asset, AssetPosition, AccountCategory, Account, UserAccount

@app.before_first_request
def setup():
    # Recreate database each time for demo
    db.drop_all() # TODO: remove
    db.create_all()
    
    with open('json/demo_account_categories.json', 'rb') as fp:
        demo_account_categories = json.load(fp)
        
    with open('json/demo_accounts.json', 'rb') as fp:
        demo_accounts = json.load(fp)

    with open('json/demo_users.json', 'rb') as fp:
        demo_users = json.load(fp)
        
    with open('json/demo_assets.json', 'rb') as fp:
        demo_assets = json.load(fp)
        
    with open('json/demo_positions.json', 'rb') as fp:
        demo_positions = json.load(fp)
              
    for dac in demo_account_categories:
        account_cat = AccountCategory.create(account_category_name = dac)
        for da in demo_accounts.get(dac):
            account = Account.create(account_name = da, account_category = account_cat)    
    
    # Set up each of the demo accounts with positions, etc.
    for demo_user in demo_users:
        user = User.create(**demo_user)
        
        app.logger.info('Adding demo user: %s' %user)
    
        user_accounts = []
    
        positions_dict = demo_positions.get(user.email)
    
        app.logger.info(positions_dict)
        
        # Iterate through the positions in all of the accounts
        # TODO: here
        for account_cat, accounts in positions_dict.iteritems():
            for account_name, account_positions in accounts.iteritems():
                app.logger.info('Adding demo account: %s' %account_name)
                # Create user accounts
                account = db.session.query(Account).filter(Account.account_name == account_name).first()
                user_account = UserAccount(account = account)
                
                act_positions = []
                # Add positions
                for asset_name, position_value in account_positions.iteritems():
                    app.logger.info('Adding position: %s' %asset_name)
        
                    # Check to see if the asset is already created, if not, create it
                    asset = db.session.query(Asset).filter(Asset.asset_name == asset_name).first()
                    if not asset:
                        app.logger.info('Adding asset: %s' %asset_name)
                        asset_info = demo_assets.get(asset_name)
                        
                        asset = Asset.create(**asset_info)
                        
                    # Now that the position is properly instantiated, add it to the user account's positions
                    new_position = AssetPosition(asset = asset, value = position_value)
                    db.session.add(new_position)
                    db.session.commit()
                    
                    act_positions.append(new_position)
            
                # Add the positions list to the user account
                user_account.positions = act_positions
                # Append the user account to the user now that all the positions have been added
                user_accounts.append(user_account)
                
        # Add the list of accounts to the user
        user.user_accounts = user_accounts
        
        # Add the user and everything that is attached to it (accounts, positions)
        db.session.commit()
        
    
    
    
    