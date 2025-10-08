from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, BooleanField
from wtforms.validators import DataRequired, Email, Length, Optional, EqualTo

class AddUserForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=255)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=6, max=128)])
    password2 = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo('password')])
    role = SelectField("Role", choices=[('user', 'User'), ('admin', 'Admin')], default='user')
    language = SelectField("Language", choices=[('en', 'English'), ('de', 'Deutsch')], default='en')
    is_active = BooleanField("Active", default=True)
    is_confirmed = BooleanField("Email Confirmed", default=True)
    submit = SubmitField("Create User")

class UserForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=255)])
    role = SelectField("Role", choices=[('user', 'User'), ('admin', 'Admin')])
    language = SelectField("Language", choices=[('en', 'English'), ('de', 'Deutsch')])
    is_active = BooleanField("Active")
    is_confirmed = BooleanField("Email Confirmed")
    new_password = PasswordField("New Password (leave blank to keep current)", validators=[Optional(), Length(min=6, max=128)])
    new_password2 = PasswordField("Confirm New Password", validators=[EqualTo('new_password')])
    submit = SubmitField("Update User")

class AdminBillingForm(FlaskForm):
    full_name = StringField("Full name", validators=[Optional(), Length(max=255)])
    company = StringField("Company", validators=[Optional(), Length(max=255)])
    address1 = StringField("Address line 1", validators=[Optional(), Length(max=255)])
    address2 = StringField("Address line 2", validators=[Optional(), Length(max=255)])
    city = StringField("City", validators=[Optional(), Length(max=128)])
    state = StringField("State/Region", validators=[Optional(), Length(max=128)])
    postal_code = StringField("Postal code", validators=[Optional(), Length(max=64)])
    country = StringField("Country (ISO-2, e.g., DE)", validators=[Optional(), Length(max=2)])
    tax_id = StringField("Tax/VAT ID", validators=[Optional(), Length(max=64)])
    submit = SubmitField("Save Billing Details")
