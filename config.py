import os
basedir = os.path.abspath(os.path.dirname(__file__))

WTF_CSRF_ENABLED = True
SECRET_KEY = 'djIVW3S5CXt1YouGdGF5L$iB2'

ENV = os.getenv('FLASKENV', 'prod')
# ENV = os.getenv('FLASKENV', 'development')

if ENV == 'development':
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:postgres@localhost:1111/development'
elif ENV == 'development':
    SQLALCHEMY_DATABASE_URI = 'postgres://mmcogvvfdbnpor:rmXMarJXrh6Sh3mKkRO7SQpCnY@ec2-54-197-245-93.compute-1.amazonaws.com:5432/damnjigp8qp428'
else:
    raise Exception('No SQL database URI specified')
    
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

