from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from ...extensions import db
from ...models import User
from ...utils.security import generate_token, verify_token
from .forms import RegisterForm, LoginForm, ForgotForm, ResetForm
from . import bp

def _dev_show_link(link: str):
    if current_app.debug or current_app.config.get("ENV") == "development":
        print("DEV LINK:", link)
        return link
    return None

@bp.route("/register", methods=["GET","POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.profile"))
    form = RegisterForm()
    if form.validate_on_submit():
        email = form.email.data.lower().strip()
        if User.query.filter_by(email=email).first():
            flash("Email already registered.", "warning")
            return redirect(url_for(".login"))
        user = User(email=email)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        token = generate_token({"uid": user.id, "purpose": "confirm"})
        link = url_for(".confirm_email", token=token, _external=True)
        dev_link = _dev_show_link(link)
        flash("Account created. Please confirm your email via the link.", "success")
        return render_template("auth/confirm_sent.html", confirm_link=dev_link)
    return render_template("auth/register.html", form=form)

@bp.route("/confirm/<token>")
def confirm_email(token):
    ok, data = verify_token(token, max_age=60*60*24)
    if not ok or data.get("purpose") != "confirm":
        flash("Invalid or expired confirmation link.", "danger")
        return redirect(url_for(".login"))
    user = User.query.get(data.get("uid"))
    if not user:
        flash("User not found.", "danger")
        return redirect(url_for(".login"))
    if not user.is_confirmed:
        user.confirm()
        db.session.commit()
    flash("Email confirmed. You can sign in now.", "success")
    return redirect(url_for(".login"))

@bp.route("/login", methods=["GET","POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.profile"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower().strip()).first()
        if not user or not user.check_password(form.password.data):
            flash("Invalid email or password.", "danger")
            return render_template("auth/login.html", form=form)
        if not user.is_confirmed:
            flash("Please confirm your email first.", "warning")
            return redirect(url_for(".resend_confirmation", email=user.email))
        login_user(user, remember=True)
        flash("Welcome back!", "success")
        next_url = request.args.get("next") or url_for("main.profile")
        return redirect(next_url)
    return render_template("auth/login.html", form=form)

@bp.get("/resend-confirmation")
def resend_confirmation():
    email = request.args.get("email", type=str, default="")
    user = User.query.filter_by(email=email.lower().strip()).first() if email else None
    if user and not user.is_confirmed:
        token = generate_token({"uid": user.id, "purpose": "confirm"})
        link = url_for(".confirm_email", token=token, _external=True)
        dev_link = _dev_show_link(link)
        flash("Confirmation link generated.", "info")
        return render_template("auth/confirm_sent.html", confirm_link=dev_link)
    flash("If the account exists and is unconfirmed, a link was generated.", "info")
    return redirect(url_for(".login"))

@bp.route("/forgot", methods=["GET","POST"])
def forgot():
    if current_user.is_authenticated:
        return redirect(url_for("main.profile"))
    form = ForgotForm()
    if form.validate_on_submit():
        email = form.email.data.lower().strip()
        user = User.query.filter_by(email=email).first()
        if user:
            token = generate_token({"uid": user.id, "purpose": "reset"})
            link = url_for(".reset_with_token", token=token, _external=True)
            dev_link = _dev_show_link(link)
            return render_template("auth/confirm_sent.html", confirm_link=dev_link, reset=True)
        flash("If an account exists, a reset link has been generated.", "info")
        return redirect(url_for(".login"))
    return render_template("auth/forgot.html", form=form)

@bp.route("/reset/<token>", methods=["GET","POST"])
def reset_with_token(token):
    ok, data = verify_token(token, max_age=60*60*2)
    if not ok or data.get("purpose") != "reset":
        flash("Invalid or expired reset link.", "danger")
        return redirect(url_for(".forgot"))
    user = User.query.get(data.get("uid"))
    if not user:
        flash("User not found.", "danger")
        return redirect(url_for(".forgot"))
    form = ResetForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash("Password updated. Please sign in.", "success")
        return redirect(url_for(".login"))
    return render_template("auth/reset.html", form=form)

@bp.get("/logout")
@login_required
def logout():
    logout_user()
    flash("Signed out.", "info")
    return redirect(url_for("main.index"))
