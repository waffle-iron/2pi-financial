from flask import Flask, url_for
from flask_sqlalchemy import SQLAlchemy
from flask.ext.assets import Environment, Bundle
from models import Base, User
import os

app = Flask(__name__)

env = os.environ.get('FLASK_ENV', 'development')
app.config['ENV'] = env

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
      'css/**/*.css',
      'css/*.css',
        # Bundle( 'css/*.scss', filters='pyscss', output='stylesheets/app.%(version)s.css'),
      output='stylesheets/all.%(version)s.css'))

assets.register('js', Bundle(
    'js/vendor/jquery/jquery.js',
    'js/**/*.js',
    'js/*.js',
    output='js/app.%(version)s.js'))

# Configure the database
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost:1111/development'
db = SQLAlchemy(app)

@app.before_first_request
def setup():
    # Recreate database each time for demo
    Base.metadata.drop_all(bind=db.engine)
    Base.metadata.create_all(bind=db.engine)
    db.session.add(User('Bob Jones', 'bob@gmail.com'))
    db.session.add(User('Joe Quimby', 'eat@joes.com'))
    db.session.commit()

    
from . import views
