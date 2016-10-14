from config import SQLALCHEMY_DATABASE_URI
from sqlalchemy import create_engine
from application import db
import os.path

# if not os.path.exists(SQLALCHEMY_DATABASE_URI):
    # engine = create_engine(SQLALCHEMY_DATABASE_URI)
    
db.create_all()