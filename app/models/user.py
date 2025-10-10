from datetime import datetime
from typing import Optional
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from ..extensions import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    language = db.Column(db.String(5), default='en')

    role = db.Column(db.String(20), nullable=False, default='user', index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    confirmed_at = db.Column(db.DateTime, nullable=True)
    
    # Enable/disable functionality
    is_active = db.Column(db.Boolean, default=True, nullable=False, index=True)
    
    # Plan relationship
    plan_id = db.Column(db.Integer, db.ForeignKey('plan.id'), nullable=True)
    plan = db.relationship('Plan', back_populates='users')
    plan_subscribed_at = db.Column(db.DateTime, nullable=True)

    # Relationships
    billing = db.relationship("BillingProfile", uselist=False, back_populates="user", cascade="all, delete-orphan")
    api_keys = db.relationship("APIKey", back_populates="user", cascade="all, delete-orphan", lazy='dynamic')

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    @property
    def is_confirmed(self) -> bool:
        return self.confirmed_at is not None

    def confirm(self):
        self.confirmed_at = datetime.utcnow()
    
    def get_id(self):
        """Required by Flask-Login"""
        return str(self.id)
    
    @property
    def is_authenticated(self):
        """Required by Flask-Login"""
        return True
    
    @property
    def is_anonymous(self):
        """Required by Flask-Login"""
        return False
    
    @property
    def current_plan(self):
        """Get current plan or return Free plan"""
        return self.plan if self.plan else None
    
    @property
    def plan_name(self):
        """Get plan name or 'Free'"""
        return self.plan.name if self.plan else 'Free'
    
    @property
    def active_api_keys_count(self):
        """Count of active API keys"""
        return self.api_keys.filter_by(is_active=True).count()
