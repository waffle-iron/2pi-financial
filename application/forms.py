from flask.ext.wtf import Form
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound
from wtforms import StringField, PasswordField, BooleanField, DateField, IntegerField, SelectField
from wtforms.validators import DataRequired, Email, ValidationError, Optional

from .models import User
from application import form_field_choices

# TODO: CSRF
# TODO: implement fully

class LoginForm(Form):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    # remember_me = BooleanField("Remember me", default=False)
    
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
   
   
def unpack_choices(choices):
    # return [(choices[ndx], choices[ndx]) for ndx in xrange(len(choices))]
    return [(ndx, choices[ndx]) for ndx in xrange(len(choices))]

    
class ProfileForm(Form):

    user_name = StringField("User Name")
    birthdate = DateField("Birth Date", validators=[Optional()])
    gender_id = SelectField("Gender",
        choices = unpack_choices(form_field_choices.get('gender')), coerce = int)
    education_id = SelectField("Education",
        choices = unpack_choices(form_field_choices.get('education')), coerce = int)
    financial_advisor_id = SelectField("Financial advisor?",
        choices = unpack_choices(form_field_choices.get('financial_advisor')), coerce = int)
    occupation_id = SelectField("Occupation",
        choices = unpack_choices(form_field_choices.get('occupation')), coerce = int)
    experience_id = SelectField("Work experience", 
        choices = unpack_choices(form_field_choices.get('experience')), coerce = int)
    salary = IntegerField("Salary", validators=[Optional()])

    def populate_form(form, usr):
        form.user = usr
    
    # form.user = user


class RegistrationForm(Form):
    # name = StringField("Display Name")
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = StringField("Password", validators=[DataRequired()])

    def validate_email(form, field):
        user = User.query.filter(User.email == field.data).first()
        if user is not None:
            raise ValidationError("A user with that email already exists")
