from flask import jsonify, request, abort, g
from ...extensions import db
from ...models import User
from ...utils.api_auth import require_api_key
from . import bp

@bp.get("/v1/ping")
def ping():
    """Public endpoint - no authentication required"""
    return jsonify({"pong": True})

# ============ PROTECTED API ENDPOINTS ============

@bp.get("/v1/me")
@require_api_key
def get_current_user():
    """Get current authenticated user info"""
    user = g.current_user
    
    return jsonify({
        "id": user.id,
        "email": user.email,
        "role": user.role,
        "language": user.language,
        "plan": user.plan_name,
        "is_active": user.is_active,
        "is_confirmed": user.is_confirmed,
        "created_at": user.created_at.isoformat()
    })

@bp.get("/v1/profile")
@require_api_key
def get_profile():
    """Get user profile with full details"""
    user = g.current_user
    
    profile = {
        "user": {
            "id": user.id,
            "email": user.email,
            "role": user.role,
            "language": user.language,
            "is_active": user.is_active,
            "is_confirmed": user.is_confirmed,
            "created_at": user.created_at.isoformat()
        },
        "plan": {
            "name": user.plan_name,
            "subscribed_at": user.plan_subscribed_at.isoformat() if user.plan_subscribed_at else None
        }
    }
    
    # Add plan details if user has a paid plan
    if user.plan:
        profile["plan"].update({
            "price": float(user.plan.price),
            "currency": user.plan.currency,
            "billing_period": user.plan.billing_period,
            "features": user.plan.features_list
        })
    
    # Add billing if exists
    if user.billing:
        profile["billing"] = {
            "full_name": user.billing.full_name,
            "company": user.billing.company,
            "country": user.billing.country
        }
    
    return jsonify(profile)

@bp.get("/v1/api-keys")
@require_api_key
def list_api_keys():
    """List user's API keys (masked)"""
    user = g.current_user
    
    keys = []
    for key in user.api_keys.all():
        keys.append({
            "id": key.id,
            "name": key.name,
            "key_prefix": key.key_prefix,
            "masked_key": key.masked_key,
            "is_active": key.is_active,
            "created_at": key.created_at.isoformat(),
            "last_used_at": key.last_used_at.isoformat() if key.last_used_at else None
        })
    
    return jsonify({
        "api_keys": keys,
        "count": len(keys)
    })

@bp.get("/v1/stats")
@require_api_key
def get_stats():
    """Get user statistics"""
    user = g.current_user
    
    stats = {
        "account": {
            "age_days": (datetime.utcnow() - user.created_at).days,
            "api_keys_count": user.active_api_keys_count
        },
        "api": {
            "key_used": g.api_key.name,
            "last_used": g.api_key.last_used_at.isoformat() if g.api_key.last_used_at else None
        }
    }
    
    return jsonify(stats)

# ============ ADMIN API ENDPOINTS ============

@bp.get("/v1/users")
@require_api_key
def list_users():
    """List all users (admin only)"""
    user = g.current_user
    
    # Check if user is admin
    if user.role != 'admin':
        return jsonify({
            "error": "Forbidden",
            "message": "Admin access required"
        }), 403
    
    users = User.query.order_by(User.id.desc()).limit(100).all()
    
    return jsonify({
        "users": [
            {
                "id": u.id,
                "email": u.email,
                "role": u.role,
                "plan": u.plan_name,
                "is_active": u.is_active,
                "created_at": u.created_at.isoformat()
            }
            for u in users
        ],
        "count": len(users)
    })

@bp.post("/v1/users")
@require_api_key
def create_user_api():
    """Create a new user via API (admin only)"""
    user = g.current_user
    
    # Check if user is admin
    if user.role != 'admin':
        return jsonify({
            "error": "Forbidden",
            "message": "Admin access required"
        }), 403
    
    data = request.get_json(silent=True) or {}
    email = data.get("email")
    password = data.get("password")
    
    if not email or not password:
        return jsonify({
            "error": "Missing fields",
            "message": "Email and password are required"
        }), 400
    
    if User.query.filter_by(email=email).first():
        return jsonify({
            "error": "Email exists",
            "message": "Email already registered"
        }), 409
    
    new_user = User(email=email)
    new_user.set_password(password)
    new_user.confirm()  # Auto-confirm API created users
    
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({
        "id": new_user.id,
        "email": new_user.email,
        "created_at": new_user.created_at.isoformat()
    }), 201

# ============ ERROR HANDLERS ============

@bp.errorhandler(404)
def api_not_found(error):
    return jsonify({
        "error": "Not found",
        "message": "The requested endpoint does not exist"
    }), 404

@bp.errorhandler(500)
def api_server_error(error):
    return jsonify({
        "error": "Server error",
        "message": "An internal server error occurred"
    }), 500
