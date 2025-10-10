from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user, logout_user
from ...extensions import db
from ...models import BillingProfile, User, Plan
from .forms import ChangePasswordForm, BillingForm, DeleteAccountForm
from . import bp
from flask_babel import _
from datetime import datetime

# Add these imports at the top
from ...models import APIKey

# Add these routes to account blueprint

@bp.route('/api-keys')
@login_required
def api_keys():
    """View and manage API keys"""
    keys = current_user.api_keys.order_by(APIKey.created_at.desc()).all()
    return render_template('account/api_keys.html', keys=keys)

@bp.route('/api-keys/create', methods=['POST'])
@login_required
def create_api_key():
    """Create a new API key"""
    name = request.form.get('name', '').strip()
    
    # Check plan limits (optional)
    # Free plan: 1 key, Pro: 5 keys, Enterprise: unlimited
    max_keys = {
        'Free': 1,
        'Pro': 5,
        'Enterprise': 999
    }
    
    current_count = current_user.active_api_keys_count
    plan_limit = max_keys.get(current_user.plan_name, 1)
    
    if current_count >= plan_limit:
        flash(_('You have reached the maximum number of API keys for your plan. Upgrade to create more.'), 'warning')
        return redirect(url_for('account.api_keys'))
    
    # Generate new key
    raw_key = APIKey.generate_key()
    
    # Create API key record
    api_key = APIKey(
        user_id=current_user.id,
        key_hash=APIKey.hash_key(raw_key),
        key_prefix=raw_key[:12],  # Store first 12 chars for display
        name=name if name else f"API Key {current_count + 1}"
    )
    
    db.session.add(api_key)
    db.session.commit()
    
    # Show the key once (it will be hashed and cannot be retrieved again)
    flash(_('API key created successfully. Copy it now - you won\'t see it again!'), 'success')
    return render_template('account/api_key_created.html', api_key=raw_key, key_name=api_key.name)

@bp.route('/api-keys/<int:key_id>/delete', methods=['POST'])
@login_required
def delete_api_key(key_id):
    """Delete an API key"""
    api_key = APIKey.query.filter_by(id=key_id, user_id=current_user.id).first_or_404()
    
    key_name = api_key.name
    db.session.delete(api_key)
    db.session.commit()
    
    flash(_('API key "%(name)s" deleted successfully', name=key_name), 'success')
    return redirect(url_for('account.api_keys'))

@bp.route('/api-keys/<int:key_id>/toggle', methods=['POST'])
@login_required
def toggle_api_key(key_id):
    """Enable/disable an API key"""
    api_key = APIKey.query.filter_by(id=key_id, user_id=current_user.id).first_or_404()
    
    api_key.is_active = not api_key.is_active
    db.session.commit()
    
    status = _('enabled') if api_key.is_active else _('disabled')
    flash(_('API key "%(name)s" has been %(status)s', name=api_key.name, status=status), 'success')
    return redirect(url_for('account.api_keys'))

@bp.route('/api-keys/<int:key_id>/regenerate', methods=['POST'])
@login_required
def regenerate_api_key(key_id):
    """Regenerate an API key"""
    api_key = APIKey.query.filter_by(id=key_id, user_id=current_user.id).first_or_404()
    
    # Generate new key
    raw_key = APIKey.generate_key()
    
    # Update existing record
    api_key.key_hash = APIKey.hash_key(raw_key)
    api_key.key_prefix = raw_key[:12]
    api_key.created_at = datetime.utcnow()
    api_key.last_used_at = None
    
    db.session.commit()
    
    flash(_('API key regenerated successfully. Copy it now - you won\'t see it again!'), 'success')
    return render_template('account/api_key_created.html', api_key=raw_key, key_name=api_key.name)


@bp.route('/language', methods=['GET', 'POST'])
@login_required
def change_language():
    if request.method == 'POST':
        language = request.form.get('language')
        if language in current_app.config['BABEL_SUPPORTED_LOCALES']:
            current_user.language = language
            db.session.commit()
            flash(_('Language updated successfully'), 'success')
        return redirect(url_for('account.overview'))
    
    return render_template('account/language.html')

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
            flash(_("Current password is incorrect."), "danger")
            return render_template("account/change_password.html", form=form)
        current_user.set_password(form.new_password.data)
        db.session.commit()
        flash(_("Password updated."), "success")
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
        flash(_("Billing details saved."), "success")
        return redirect(url_for("account.overview"))
    return render_template("account/billing.html", form=form)

@bp.route("/delete", methods=["GET","POST"])
@login_required
def delete_account():
    form = DeleteAccountForm()
    if form.validate_on_submit():
        if form.confirm.data.strip().upper() != "DELETE":
            flash(_("Please type DELETE to confirm."), "warning")
            return render_template("account/delete.html", form=form)
        uid = current_user.id
        logout_user()
        user = User.query.get(uid)
        db.session.delete(user)
        db.session.commit()
        flash(_("Your account has been deleted."), "info")
        return redirect(url_for("main.index"))
    return render_template("account/delete.html", form=form)

# ============ PLAN SELECTION ROUTES ============

@bp.route('/plan')
@login_required
def view_plan():
    """View current plan and available plans"""
    current_plan = current_user.plan
    available_plans = Plan.query.filter_by(is_active=True).order_by(Plan.sort_order.asc()).all()
    
    return render_template('account/plan.html', 
                         current_plan=current_plan, 
                         available_plans=available_plans)

@bp.route('/plan/select/<int:plan_id>', methods=['POST'])
@login_required
def select_plan(plan_id):
    """Select/change plan"""
    plan = Plan.query.get_or_404(plan_id)
    
    # Check if plan is active
    if not plan.is_active:
        flash(_('This plan is not available'), 'danger')
        return redirect(url_for('account.view_plan'))
    
    # Check if already on this plan
    if current_user.plan_id == plan_id:
        flash(_('You are already on the %(plan)s plan', plan=plan.name), 'info')
        return redirect(url_for('account.view_plan'))
    
    # For paid plans, redirect to payment (implement Stripe integration later)
    if plan.price > 0:
        flash(_('Payment integration coming soon. Plan selected: %(plan)s', plan=plan.name), 'info')
        # TODO: Integrate with Stripe for payment processing
    
    # Update user's plan
    current_user.plan_id = plan.id
    current_user.plan_subscribed_at = datetime.utcnow()
    db.session.commit()
    
    flash(_('Successfully switched to %(plan)s plan', plan=plan.name), 'success')
    return redirect(url_for('account.view_plan'))

@bp.route('/plan/cancel', methods=['POST'])
@login_required
def cancel_plan():
    """Cancel current plan (revert to Free)"""
    if not current_user.plan:
        flash(_('You are not subscribed to any plan'), 'info')
        return redirect(url_for('account.view_plan'))
    
    old_plan = current_user.plan.name
    current_user.plan_id = None
    current_user.plan_subscribed_at = None
    db.session.commit()
    
    flash(_('Successfully cancelled %(plan)s plan', plan=old_plan), 'success')
    return redirect(url_for('account.view_plan'))
