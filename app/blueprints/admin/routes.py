from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from ...extensions import db
from ...models import User, BillingProfile, Plan
from ...security import roles_required
from .forms import UserForm, AddUserForm
from . import bp
from flask_babel import _

@bp.route('/')
@login_required
@roles_required('admin')
def index():
    """Admin dashboard - shows user list"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # Get search query
    search = request.args.get('search', '', type=str)
    
    # Base query
    query = User.query
    
    # Apply search filter
    if search:
        query = query.filter(
            (User.email.ilike(f'%{search}%'))
        )
    
    # Paginate
    pagination = query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    users = pagination.items
    
    return render_template(
        'admin/index.html',
        users=users,
        pagination=pagination,
        search=search
    )

@bp.route('/users/add', methods=['GET', 'POST'])
@login_required
@roles_required('admin')
def add_user():
    """Add a new user"""
    form = AddUserForm()
    
    if form.validate_on_submit():
        # Check if email already exists
        if User.query.filter_by(email=form.email.data.lower().strip()).first():
            flash(_('Email already exists'), 'danger')
            return render_template('admin/add_user.html', form=form)
        
        # Create new user
        user = User(
            email=form.email.data.lower().strip(),
            role=form.role.data,
            language=form.language.data,
            is_active=form.is_active.data
        )
        user.set_password(form.password.data)
        
        # Auto-confirm if admin creates user
        if form.is_confirmed.data:
            user.confirm()
        
        db.session.add(user)
        db.session.commit()
        
        flash(_('User created successfully'), 'success')
        return redirect(url_for('admin.index'))
    
    return render_template('admin/add_user.html', form=form)

@bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@roles_required('admin')
def edit_user(user_id):
    """Edit an existing user"""
    user = User.query.get_or_404(user_id)
    form = UserForm(obj=user)
    
    if form.validate_on_submit():
        # Prevent admin from demoting themselves
        if user.id == current_user.id and form.role.data != 'admin':
            flash(_('You cannot remove your own admin role'), 'danger')
            return render_template('admin/edit_user.html', form=form, user=user)
        
        # Prevent admin from disabling themselves
        if user.id == current_user.id and not form.is_active.data:
            flash(_('You cannot disable your own account'), 'danger')
            return render_template('admin/edit_user.html', form=form, user=user)
        
        # Update user
        user.email = form.email.data.lower().strip()
        user.role = form.role.data
        user.language = form.language.data
        user.is_active = form.is_active.data
        
        # Update password if provided
        if form.new_password.data:
            user.set_password(form.new_password.data)
        
        # Update confirmation status
        if form.is_confirmed.data and not user.is_confirmed:
            user.confirm()
        elif not form.is_confirmed.data and user.is_confirmed:
            user.confirmed_at = None
        
        db.session.commit()
        flash(_('User updated successfully'), 'success')
        return redirect(url_for('admin.index'))
    
    return render_template('admin/edit_user.html', form=form, user=user)

@bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
@roles_required('admin')
def delete_user(user_id):
    """Delete a user"""
    user = User.query.get_or_404(user_id)
    
    # Prevent admin from deleting themselves
    if user.id == current_user.id:
        flash(_('You cannot delete your own account'), 'danger')
        return redirect(url_for('admin.index'))
    
    email = user.email
    db.session.delete(user)
    db.session.commit()
    
    flash(_('User %(email)s deleted successfully', email=email), 'success')
    return redirect(url_for('admin.index'))

@bp.route('/users/<int:user_id>/toggle-status', methods=['POST'])
@login_required
@roles_required('admin')
def toggle_user_status(user_id):
    """Enable/disable a user"""
    user = User.query.get_or_404(user_id)
    
    # Prevent admin from disabling themselves
    if user.id == current_user.id:
        flash(_('You cannot disable your own account'), 'danger')
        return redirect(url_for('admin.index'))
    
    user.is_active = not user.is_active
    db.session.commit()
    
    status = _('enabled') if user.is_active else _('disabled')
    flash(_('User %(email)s has been %(status)s', email=user.email, status=status), 'success')
    
    return redirect(url_for('admin.index'))

@bp.route('/users/<int:user_id>/billing', methods=['GET', 'POST'])
@login_required
@roles_required('admin')
def edit_user_billing(user_id):
    """Edit user's billing information"""
    user = User.query.get_or_404(user_id)
    
    # Get or create billing profile
    billing = user.billing or BillingProfile(user=user)
    
    from .forms import AdminBillingForm
    form = AdminBillingForm(obj=billing)
    
    if form.validate_on_submit():
        form.populate_obj(billing)
        db.session.add(billing)
        db.session.commit()
        flash(_('Billing details updated for %(email)s', email=user.email), 'success')
        return redirect(url_for('admin.edit_user', user_id=user_id))
    
    return render_template('admin/edit_billing.html', form=form, user=user, billing=billing)

@bp.route('/users/<int:user_id>/billing/clear', methods=['POST'])
@login_required
@roles_required('admin')
def clear_user_billing(user_id):
    """Clear user's billing information"""
    user = User.query.get_or_404(user_id)
    
    if user.billing:
        db.session.delete(user.billing)
        db.session.commit()
        flash(_('Billing details cleared for %(email)s', email=user.email), 'success')
    else:
        flash(_('No billing details to clear'), 'info')
    
    return redirect(url_for('admin.edit_user_billing', user_id=user_id))

# ============ PLAN MANAGEMENT ROUTES ============

@bp.route('/plans')
@login_required
@roles_required('admin')
def plans():
    """List all plans"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # Get all plans ordered by sort_order
    pagination = Plan.query.order_by(Plan.sort_order.asc(), Plan.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    plans = pagination.items
    
    return render_template(
        'admin/plans.html',
        plans=plans,
        pagination=pagination
    )

@bp.route('/plans/add', methods=['GET', 'POST'])
@login_required
@roles_required('admin')
def add_plan():
    """Add a new plan"""
    from .forms import PlanForm
    form = PlanForm()
    
    if form.validate_on_submit():
        # Check if plan name already exists
        if Plan.query.filter_by(name=form.name.data).first():
            flash(_('Plan with this name already exists'), 'danger')
            return render_template('admin/add_plan.html', form=form)
        
        # Create new plan
        plan = Plan(
            name=form.name.data,
            description=form.description.data,
            option1=form.option1.data,
            option2=form.option2.data,
            option3=form.option3.data,
            option4=form.option4.data,
            option5=form.option5.data,
            price=form.price.data,
            currency=form.currency.data,
            billing_period=form.billing_period.data,
            stripe_price_id=form.stripe_price_id.data,
            stripe_product_id=form.stripe_product_id.data,
            is_active=form.is_active.data,
            is_featured=form.is_featured.data,
            sort_order=form.sort_order.data
        )
        
        db.session.add(plan)
        db.session.commit()
        
        flash(_('Plan created successfully'), 'success')
        return redirect(url_for('admin.plans'))
    
    return render_template('admin/add_plan.html', form=form)

@bp.route('/plans/<int:plan_id>/edit', methods=['GET', 'POST'])
@login_required
@roles_required('admin')
def edit_plan(plan_id):
    """Edit an existing plan"""
    plan = Plan.query.get_or_404(plan_id)
    
    from .forms import PlanForm
    form = PlanForm(obj=plan)
    
    if form.validate_on_submit():
        # Update plan
        plan.name = form.name.data
        plan.description = form.description.data
        plan.option1 = form.option1.data
        plan.option2 = form.option2.data
        plan.option3 = form.option3.data
        plan.option4 = form.option4.data
        plan.option5 = form.option5.data
        plan.price = form.price.data
        plan.currency = form.currency.data
        plan.billing_period = form.billing_period.data
        plan.stripe_price_id = form.stripe_price_id.data
        plan.stripe_product_id = form.stripe_product_id.data
        plan.is_active = form.is_active.data
        plan.is_featured = form.is_featured.data
        plan.sort_order = form.sort_order.data
        
        db.session.commit()
        flash(_('Plan updated successfully'), 'success')
        return redirect(url_for('admin.plans'))
    
    return render_template('admin/edit_plan.html', form=form, plan=plan)

@bp.route('/plans/<int:plan_id>/delete', methods=['POST'])
@login_required
@roles_required('admin')
def delete_plan(plan_id):
    """Delete a plan"""
    plan = Plan.query.get_or_404(plan_id)
    
    # Check if any users are using this plan
    user_count = plan.users.count()
    if user_count > 0:
        flash(_('Cannot delete plan: %(count)d users are subscribed to this plan', count=user_count), 'danger')
        return redirect(url_for('admin.plans'))
    
    plan_name = plan.name
    db.session.delete(plan)
    db.session.commit()
    
    flash(_('Plan "%(name)s" deleted successfully', name=plan_name), 'success')
    return redirect(url_for('admin.plans'))

@bp.route('/plans/<int:plan_id>/toggle-status', methods=['POST'])
@login_required
@roles_required('admin')
def toggle_plan_status(plan_id):
    """Enable/disable a plan"""
    plan = Plan.query.get_or_404(plan_id)
    
    plan.is_active = not plan.is_active
    db.session.commit()
    
    status = _('enabled') if plan.is_active else _('disabled')
    flash(_('Plan "%(name)s" has been %(status)s', name=plan.name, status=status), 'success')
    
    return redirect(url_for('admin.plans'))
