from datetime import datetime
import secrets
from ..extensions import db

class APIKey(db.Model):
    __tablename__ = 'api_key'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    
    # The actual API key (hashed for security)
    key_hash = db.Column(db.String(255), nullable=False, unique=True, index=True)
    
    # First 8 characters to show user (for identification)
    key_prefix = db.Column(db.String(8), nullable=False)
    
    # Optional name/description
    name = db.Column(db.String(100), nullable=True)
    
    # Usage tracking
    last_used_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Expiration (optional)
    expires_at = db.Column(db.DateTime, nullable=True)
    
    # Active status
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # Relationship
    user = db.relationship('User', back_populates='api_keys')
    
    @staticmethod
    def generate_key():
        """Generate a secure random API key"""
        # Format: sk_live_32_random_characters
        random_part = secrets.token_urlsafe(32)
        return f"sk_live_{random_part}"
    
    @staticmethod
    def hash_key(key):
        """Hash an API key for storage"""
        from werkzeug.security import generate_password_hash
        return generate_password_hash(key)
    
    @staticmethod
    def verify_key(key_hash, key):
        """Verify an API key against its hash"""
        from werkzeug.security import check_password_hash
        return check_password_hash(key_hash, key)
    
    def mark_used(self):
        """Update last used timestamp"""
        self.last_used_at = datetime.utcnow()
        db.session.commit()
    
    @property
    def is_expired(self):
        """Check if key has expired"""
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at
    
    @property
    def masked_key(self):
        """Return masked key for display (sk_live_abc12345...xyz)"""
        return f"{self.key_prefix}{'*' * 32}"
    
    def __repr__(self):
        return f'<APIKey {self.key_prefix} for User {self.user_id}>'
