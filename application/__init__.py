from flask import Flask, url_for
from flask_sqlalchemy import SQLAlchemy
from flask.ext.assets import Environment, Bundle
from flask.ext.login import LoginManager, UserMixin, login_required
from flask.ext.navigation import Navigation
import os

import logging

app = Flask(__name__)
app.config.from_object('config')

# Set up logging
file_handler = logging.FileHandler('app.log')
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)

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
        # Bundle( 'css/*.scss', filters='pyscss', output='stylesheets/app.%(version)s.css'),
      output='stylesheets/all.%(version)s.css'))

assets.register('js', Bundle(
    'js/vendor/jquery/jquery.js',
    'js/vendor/*.js',
    'js/*.js',
    output='js/app.%(version)s.js'))
    
# TODO: load some javascript assets at the end of the body

# Load up the database
db = SQLAlchemy(app)

# For the navigation bar
nav = Navigation(app)

# Login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


from application import views, models

from models import User

@app.before_first_request
def setup():
    # Recreate database each time for demo
    db.drop_all() # TODO: remove
    db.create_all()
    
    db.session.add(User('ywp@demo.com', 'demo123', 'Young working professional', is_demo=True))
    db.session.add(User('fof@demo.com', 'demo123', 'Family of 4', is_demo=True))
    db.session.add(User('nr@demo.com', 'demo123', 'Nearing retirement', is_demo=True))
    db.session.add(User('custom@demo.com', 'demo123', 'Custom', is_demo=True))
    
    db.session.commit()
    
    