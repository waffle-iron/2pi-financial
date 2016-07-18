import os
basedir = os.path.abspath(os.path.dirname(__file__))

WTF_CSRF_ENABLED = True
SECRET_KEY = 'djIVW3S5CXt1YouGdGF5L$iB2'

ENV = os.getenv('FLASKENV', 'prod')
# ENV = os.getenv('FLASKENV', 'development')

if ENV == 'development':
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:postgres@localhost:1111/development'
else:
    SQLALCHEMY_DATABASE_URI = 'postgres://mmcogvvfdbnpor:rmXMarJXrh6Sh3mKkRO7SQpCnY@ec2-54-197-245-93.compute-1.amazonaws.com:5432/damnjigp8qp428'

SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

# HEROKU
# miller1417@gmail.com : OiV4T3Zw$A&8

# heroku login
# # heroku create
# git push heroku master


# Set up on the server:
# heroku config:set FLASKENV=prod
# Server host, port?
# configure the database
# add database resource to the application


# Set up for development:
# git clone 
# virtualenv venv
# source venv/bin/Activate
# export FLASKENV=development
# create Postgres database development/1111
# python runserver.py

# git push origin master