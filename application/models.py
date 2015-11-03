from flask.ext.login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from application import db


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), index=True, unique=True)
    pw_hash = db.Column(db.String(255))
    name = db.Column(db.String(255))
    is_demo = db.Column(db.Boolean, default=False)
    active = db.Column(db.Boolean)
    confirmed_at = db.Column(db.DateTime)
    
    def get_id(self):
        """Return the id to satisfy Flask-Login's requirements."""
        try:
            return unicode(self.id)  # python 2
        except NameError:
            return str(self.id)  # python 3
        
    @property
    def is_active(self):
        """True, as all users are active."""
        return True
        
    @property
    def is_authenticated(self):
        """Return True if the user is authenticated."""
        return True

    @property
    def is_anonymous(self):
        """False, as anonymous users aren't supported."""
        return False
        
    def __repr__(self):
        return '<User %r>' % (self.name)
        
    def set_password(self, password):
        self.pw_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.pw_hash, password)
        
    def __init__(self, email=None, password=None, name=None, is_demo=False):
        self.email = email
        self.set_password(password)
        if name is None:
            self.name = email
        else:
            self.name = name
        self.is_demo = is_demo
        
        