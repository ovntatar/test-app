from ..extensions import db

class BillingProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), unique=True, nullable=False)

    full_name = db.Column(db.String(255), nullable=True)
    company = db.Column(db.String(255), nullable=True)
    address1 = db.Column(db.String(255), nullable=True)
    address2 = db.Column(db.String(255), nullable=True)
    city = db.Column(db.String(128), nullable=True)
    state = db.Column(db.String(128), nullable=True)
    postal_code = db.Column(db.String(64), nullable=True)
    country = db.Column(db.String(2), nullable=True)  # ISO 2-letter code
    tax_id = db.Column(db.String(64), nullable=True)  # VAT/Tax number

    user = db.relationship("User", back_populates="billing")
