from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, BooleanField, TextAreaField, DecimalField, IntegerField
from wtforms.validators import DataRequired, Email, Length, Optional, EqualTo, NumberRange

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

class PlanForm(FlaskForm):
    name = StringField("Plan Name", validators=[DataRequired(), Length(max=100)])
    description = TextAreaField("Description", validators=[Optional(), Length(max=500)])
    
    # Features/Options
    option1 = StringField("Feature 1", validators=[Optional(), Length(max=255)])
    option2 = StringField("Feature 2", validators=[Optional(), Length(max=255)])
    option3 = StringField("Feature 3", validators=[Optional(), Length(max=255)])
    option4 = StringField("Feature 4", validators=[Optional(), Length(max=255)])
    option5 = StringField("Feature 5", validators=[Optional(), Length(max=255)])
    
    # Pricing
    price = DecimalField("Price", validators=[DataRequired(), NumberRange(min=0)], places=2, default=0.00)
    currency = SelectField("Currency", choices=[
        ('USD', 'USD - US Dollar'),
        ('EUR', 'EUR - Euro'),
        ('GBP', 'GBP - British Pound'),
        ('JPY', 'JPY - Japanese Yen')
    ], default='USD')
    billing_period = SelectField("Billing Period", choices=[
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
        ('lifetime', 'Lifetime')
    ], default='monthly')
    
    # Stripe Integration
    stripe_price_id = StringField("Stripe Price ID", validators=[Optional(), Length(max=255)])
    stripe_product_id = StringField("Stripe Product ID", validators=[Optional(), Length(max=255)])
    
    # Settings
    is_active = BooleanField("Active", default=True)
    is_featured = BooleanField("Featured", default=False)
    sort_order = IntegerField("Sort Order", validators=[Optional()], default=0)
    
    submit = SubmitField("Save Plan")
