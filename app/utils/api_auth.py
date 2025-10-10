from functools import wraps
from flask import request, jsonify, g
from ..models import User, APIKey

def require_api_key(f):
    """
    Decorator to require API key authentication
    Usage:
        @bp.route('/api/v1/protected')
        @require_api_key
        def protected_route():
            # g.current_user is available here
            return jsonify({'user': g.current_user.email})
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get API key from header
        auth_header = request.headers.get('Authorization', '')
        
        if not auth_header:
            return jsonify({
                'error': 'Missing API key',
                'message': 'Include your API key in the Authorization header: Bearer sk_live_...'
            }), 401
        
        # Extract key from "Bearer sk_live_..." format
        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            return jsonify({
                'error': 'Invalid authorization format',
                'message': 'Use: Authorization: Bearer sk_live_...'
            }), 401
        
        api_key_value = parts[1]
        
        # Validate key format
        if not api_key_value.startswith('sk_live_'):
            return jsonify({
                'error': 'Invalid API key format',
                'message': 'API keys must start with sk_live_'
            }), 401
        
        # Get key prefix for lookup
        key_prefix = api_key_value[:12]
        
        # Find all keys with this prefix
        potential_keys = APIKey.query.filter_by(key_prefix=key_prefix).all()
        
        # Verify the key
        valid_key = None
        for key in potential_keys:
            if APIKey.verify_key(key.key_hash, api_key_value):
                valid_key = key
                break
        
        if not valid_key:
            return jsonify({
                'error': 'Invalid API key',
                'message': 'The provided API key is invalid'
            }), 401
        
        # Check if key is active
        if not valid_key.is_active:
            return jsonify({
                'error': 'API key disabled',
                'message': 'This API key has been disabled'
            }), 401
        
        # Check if key has expired
        if valid_key.is_expired:
            return jsonify({
                'error': 'API key expired',
                'message': 'This API key has expired'
            }), 401
        
        # Check if user is active
        if not valid_key.user.is_active:
            return jsonify({
                'error': 'Account disabled',
                'message': 'Your account has been disabled'
            }), 403
        
        # Update last used timestamp
        valid_key.mark_used()
        
        # Store user in g for use in route
        g.current_user = valid_key.user
        g.api_key = valid_key
        
        return f(*args, **kwargs)
    
    return decorated_function

def optional_api_key(f):
    """
    Decorator that allows both API key and regular authentication
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Try API key first
        auth_header = request.headers.get('Authorization', '')
        
        if auth_header:
            # Has authorization header, try API key
            parts = auth_header.split()
            if len(parts) == 2 and parts[0].lower() == 'bearer':
                api_key_value = parts[1]
                key_prefix = api_key_value[:12]
                
                potential_keys = APIKey.query.filter_by(key_prefix=key_prefix).all()
                
                for key in potential_keys:
                    if APIKey.verify_key(key.key_hash, api_key_value):
                        if key.is_active and not key.is_expired and key.user.is_active:
                            key.mark_used()
                            g.current_user = key.user
                            g.api_key = key
                            return f(*args, **kwargs)
        
        # If no valid API key, continue (may have session auth)
        return f(*args, **kwargs)
    
    return decorated_function
