from flask.ext.login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from application import db

# TODO: comments
# TODO: lazy load? optimize?

def create_new_demo_asset(asset_name, asset_class, is_demo = True):
    # TODO: make more modular / general
    new_asset = Asset(asset_name = asset_name, asset_class = asset_class, is_demo = is_demo)
    db.session.add(new_asset)
    db.session.commit()
    return new_asset
    

class AssetPosition(db.Model):
    __tablename__ = 'asset_positions'
    
    id = db.Column(db.Integer, primary_key = True)
    
    asset_id = db.Column(db.Integer, db.ForeignKey('asset.id'))
    asset = db.relationship('Asset') # Many asset positions are linked to an asset
       
    user_account_id = db.Column(db.Integer, db.ForeignKey('user_account.id'))
    
    value = db.Column(db.Float)
    
    def __repr__(self):
        return '<Asset Position %s: %d>' % (self.asset.asset_name, int(self.value))
        
    def __init__(self, asset, value):
        self.asset = asset
        self.value = value
        
class Asset(db.Model):
    __tablename__ = 'asset'
    
    id = db.Column(db.Integer, primary_key = True)
    asset_name = db.Column(db.String(32))
    asset_class = db.Column(db.String(32))
    is_demo = db.Column(db.Boolean)
    
    def __repr__(self):
        return '<Asset %s / %s>' % (self.asset_name, self.asset_class)
        
    def __init__(self, asset_name, asset_class, is_demo = False):
        self.asset_name = asset_name
        self.asset_class = asset_class
        self.is_demo = is_demo


class CustomDemoIP(db.Model):
    """
    This table is for simply counting up the custom demo ids
    """
    __tablename__ = 'custom_demo_ip'
    
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(32))
    
    def __repr__(self):
        return '<CustomDemoIP %d -- %s>' % (self.id, self.ip_address)
        
    def __init__(self, ip_addr):
        self.ip_address = ip_addr
        
                
class UserAccount(db.Model):
    __tablename__ = 'user_account'
    
    id = db.Column(db.Integer, primary_key = True)
    
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'))
    account = db.relationship('Account')    
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), index=True)
    
    # One to many mapping that is bidirectional (user has many positions / positions mapped to one user)
    positions = db.relationship('AssetPosition', backref='account', lazy='dynamic')
    
    def __repr__(self):
        return '<UserAccount %d -- %s>' % (self.user_id, self.account_id)
        
    def __init__(self, account):
        self.account = account
    
    
class Account(db.Model):
    __tablename__ = 'account'
    
    id = db.Column(db.Integer, primary_key = True)
    account_name = db.Column(db.String(255))
    
    is_taxable = db.Column(db.Boolean)
    
    account_category_id = db.Column(db.Integer, db.ForeignKey('account_category.id'))
    account_category = db.relationship('AccountCategory')
    
    def __repr__(self):
        return '<Account %s>' % (self.account_name)
        
    def __init__(self, account_name, account_category, is_taxable = True):
        self.account_name = account_name
        self.account_category = account_category
        self.is_taxable = is_taxable
        
        
class AccountCategory(db.Model):
    __tablename__ = 'account_category'
    
    id = db.Column(db.Integer, primary_key = True)
    account_category_name = db.Column(db.String(255), unique=True)
    
    def __repr__(self):
        return '<AccountCategory %s>' % (self.account_category_name)
        
    def __init__(self, account_category_name):
        self.account_category_name = account_category_name
        
        
class User(UserMixin, db.Model):
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), index=True, unique=True)
    pw_hash = db.Column(db.String(255))
    user_name = db.Column(db.String(255))
    is_demo = db.Column(db.Boolean, default=False)
    is_custom = db.Column(db.Boolean, default=False)
    
    # One to many mapping that is bidirectional (user has many positions / positions mapped to one user)
    user_accounts = db.relationship('UserAccount', backref='user', lazy='dynamic') 
    
    
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
        return '<User %r>' % (self.user_name)
        
    def set_password(self, password):
        self.pw_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.pw_hash, password)
        
    def __init__(self, email=None, password=None, user_name=None, is_demo=False, is_custom=False):
        self.email = email
        self.set_password(password)
        if user_name is None:
            self.user_name = email
        else:
            self.user_name = user_name
        self.is_demo = is_demo
        self.is_custom = is_custom
        
        