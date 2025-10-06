from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user, logout_user
from ...extensions import db
from ...models import BillingProfile, User
from .forms import ChangePasswordForm, BillingForm, DeleteAccountForm
from . import bp

@bp.get("/")
@login_required
def overview():
    billing = current_user.billing
    return render_template("account/overview.html", billing=billing)

@bp.route("/password", methods=["GET","POST"])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if not current_user.check_password(form.current_password.data):
            flash("Current password is incorrect.", "danger")
            return render_template("account/change_password.html", form=form)
        current_user.set_password(form.new_password.data)
        db.session.commit()
        flash("Password updated.", "success")
        return redirect(url_for("account.overview"))
    return render_template("account/change_password.html", form=form)

@bp.route("/billing", methods=["GET","POST"])
@login_required
def billing():
    billing = current_user.billing or BillingProfile(user=current_user)
    form = BillingForm(obj=billing)
    if form.validate_on_submit():
        form.populate_obj(billing)
        db.session.add(billing)
        db.session.commit()
        flash("Billing details saved.", "success")
        return redirect(url_for("account.overview"))
    return render_template("account/billing.html", form=form)

@bp.route("/delete", methods=["GET","POST"])
@login_required
def delete_account():
    form = DeleteAccountForm()
    if form.validate_on_submit():
        if form.confirm.data.strip().upper() != "DELETE":
            flash("Please type DELETE to confirm.", "warning")
            return render_template("account/delete.html", form=form)
        uid = current_user.id
        logout_user()
        user = User.query.get(uid)
        db.session.delete(user)
        db.session.commit()
        flash("Your account has been deleted.", "info")
        return redirect(url_for("main.index"))
    return render_template("account/delete.html", form=form)
