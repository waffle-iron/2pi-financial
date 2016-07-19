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


#####
# HEROKU
#####
# miller1417@gmail.com : OiV4T3Zw$A&8

# heroku login
# # heroku create
# git push heroku master

#####
# Set up on the server:
#####
# heroku config:set FLASKENV=prod
# Server host, port?
# configure the database
# add database resource to the application

#####
# Set up for development:
#####
# git clone https://miller1417@bitbucket.org/miller1417/dashboard_app.git
# virtualenv venv
# source venv/bin/Activate
# pip install -r requirements.txt
# export FLASKENV=development
# create Postgres database
# python runserver.py

# Creating the Postgres database:
# sudo apt-get install postgres-9.3
# sudo apt-get install pgadmin3
# su - postgres
# psql
# CREATE DATABASE development;
# \l
# exit
# sudo gedit /etc/postgresql/9.3/main/postgresql.conf
### change the port to 1111

######
# git push origin master
######