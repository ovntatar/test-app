from flask import jsonify, request, abort
from ...extensions import db
from ...models import User
from . import bp

@bp.get("/v1/ping")
def ping():
    return jsonify({"pong": True})

@bp.get("/v1/users")
def list_users():
    users = User.query.order_by(User.id.desc()).all()
    return jsonify([{"id": u.id, "email": u.email} for u in users])

@bp.post("/v1/users")
def create_user():
    data = request.get_json(silent=True) or {}
    email = data.get("email")
    if not email:
        abort(400, description="Missing 'email'")
    if User.query.filter_by(email=email).first():
        abort(409, description="Email already exists")
    user = User(email=email, password_hash="!")
    db.session.add(user)
    db.session.commit()
    return jsonify({"id": user.id, "email": user.email}), 201
