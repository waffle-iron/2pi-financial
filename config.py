import os
basedir = os.path.abspath(os.path.dirname(__file__))

WTF_CSRF_ENABLED = True
SECRET_KEY = 'abc123'

ENV = 'development'

SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:postgres@localhost:1111/development'
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')



# https://pwmiller@pwmiller1.scm.azurewebsites.net:443/pwmiller1.git
# git remote add azure https://pwmiller@pwmiller1.scm.azurewebsites.net:443/pwmiller1.git
# git push azure master

# Data Source=tcp:c2shlbm7o1.database.windows.net,1433;Initial Catalog=pwmilleAXuLcuAf3;User Id=proddb@c2shlbm7o1;Password=qG$1tSGnYYq0;
# pwmiller1
# pwmilleAXuLcuAf3
# proddb:qG$1tSGnYYq0


# AZURE GIT
# pwmiller:VZfj0!vyh2hm