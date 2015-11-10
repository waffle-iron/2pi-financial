import os
basedir = os.path.abspath(os.path.dirname(__file__))

WTF_CSRF_ENABLED = True
SECRET_KEY = 'abc123'

ENV = 'development'

SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:postgres@localhost:1111/development'
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')



# HEROUKU
# miller1417@gmail.com : OiV4T3Zw$A&8

# heroku login
# heroku create
# git push heroku master`
