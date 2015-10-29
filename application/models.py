# Set up database
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from flask.ext.login import UserMixin

Base = declarative_base()

class User(Base, UserMixin):
    __tablename__ = 'users'
    
    id = Column(String(50), unique=True, primary_key = True)
    password = Column(String(120))

    def __init__(self, id=None, password=None):
        self.id = id
        self.password = password
        
    def __repr__(self):
        return '<User %r>' % (self.name)
        