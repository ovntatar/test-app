from flask import render_template
from flask_login import login_required, current_user
from . import bp
from ...models import Plan


@bp.get("/")
def index():
    # Get all active plans ordered by sort_order
    available_plans = Plan.query.filter_by(is_active=True).order_by(Plan.sort_order.asc()).all()
    return render_template("index.html", available_plans=available_plans)

@bp.get("/about")
def about():
    return render_template("about.html")

@bp.get("/profile")
@login_required
def profile():
    return render_template("profile.html", user=current_user)
