from flask.ext.wtf import Form
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Email, ValidationError

from .models import User

# TODO: CSRF
# TODO: implement fully

class LoginForm(Form):
    email = StringField('email', validators=[DataRequired(), Email()])
    password = PasswordField('password', validators=[DataRequired()])
    remember_me = BooleanField('remember_me', default=False)
    
    # WTForms supports "inline" validators
    # which are methods of our `Form` subclass
    # with names in the form `validate_[fieldname]`.
    # This validator will run after all the
    # other validators have passed.
    def validate_password(form, field):
        try:
            user = User.query.filter(User.email == form.email.data).one()
        except (MultipleResultsFound, NoResultFound):
            raise ValidationError("Invalid user")
        if user is None:
            raise ValidationError("Invalid user")
        if not user.check_password(form.password.data):
            raise ValidationError("Invalid password")
            
        # Make the current user available to calling code.
        form.user = user
            
class RegistrationForm(Form):
    name = StringField("Display Name")
    email = StringField(validators=[DataRequired(), Email()])
    password = StringField(validators=[DataRequired()])

    def validate_email(form, field):
        user = User.query.filter(User.email == field.data).first()
        if user is not None:
            raise ValidationError("A user with that email already exists")
