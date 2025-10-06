from flask import render_template
from flask_login import login_required, current_user
from . import bp


@bp.get("/")
def index():
    return render_template("index.html")

@bp.get("/about")
def about():
    return render_template("about.html")

@bp.get("/profile")
@login_required
def profile():
    return render_template("profile.html", user=current_user)
