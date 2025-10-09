from datetime import datetime
from ..extensions import db

class Plan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    
    # Features/Options
    option1 = db.Column(db.String(255), nullable=True)  # e.g., "10 Projects"
    option2 = db.Column(db.String(255), nullable=True)  # e.g., "Unlimited Storage"
    option3 = db.Column(db.String(255), nullable=True)  # Additional feature
    option4 = db.Column(db.String(255), nullable=True)  # Additional feature
    option5 = db.Column(db.String(255), nullable=True)  # Additional feature
    
    # Pricing
    price = db.Column(db.Numeric(10, 2), nullable=False, default=0.00)
    currency = db.Column(db.String(3), nullable=False, default='USD')
    billing_period = db.Column(db.String(20), nullable=False, default='monthly')  # monthly, yearly, lifetime
    
    # Stripe Integration
    stripe_price_id = db.Column(db.String(255), nullable=True)  # Stripe Price ID
    stripe_product_id = db.Column(db.String(255), nullable=True)  # Stripe Product ID
    
    # Plan Settings
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_featured = db.Column(db.Boolean, default=False, nullable=False)
    sort_order = db.Column(db.Integer, default=0)  # For display ordering
    
    # Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    users = db.relationship('User', back_populates='plan', lazy='dynamic')
    
    def __repr__(self):
        return f'<Plan {self.name}>'
    
    @property
    def formatted_price(self):
        """Return formatted price string"""
        if self.price == 0:
            return 'Free'
        return f'{self.currency} {self.price:.2f}/{self.billing_period}'
    
    @property
    def features_list(self):
        """Return list of non-empty features"""
        features = []
        for i in range(1, 6):
            option = getattr(self, f'option{i}', None)
            if option:
                features.append(option)
        return features
