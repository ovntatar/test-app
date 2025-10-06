from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField("Current Password", validators=[DataRequired()])
    new_password = PasswordField("New Password", validators=[DataRequired(), Length(min=6, max=128)])
    new_password2 = PasswordField("Confirm New Password", validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField("Update password")

class BillingForm(FlaskForm):
    full_name = StringField("Full name", validators=[Optional(), Length(max=255)])
    company = StringField("Company", validators=[Optional(), Length(max=255)])
    address1 = StringField("Address line 1", validators=[Optional(), Length(max=255)])
    address2 = StringField("Address line 2", validators=[Optional(), Length(max=255)])
    city = StringField("City", validators=[Optional(), Length(max=128)])
    state = StringField("State/Region", validators=[Optional(), Length(max=128)])
    postal_code = StringField("Postal code", validators=[Optional(), Length(max=64)])
    country = StringField("Country (ISO-2, e.g., DE)", validators=[Optional(), Length(max=2)])
    tax_id = StringField("Tax/VAT ID", validators=[Optional(), Length(max=64)])
    submit = SubmitField("Save billing details")

class DeleteAccountForm(FlaskForm):
    confirm = StringField("Type DELETE to confirm", validators=[DataRequired()])
    submit = SubmitField("Delete my account")
