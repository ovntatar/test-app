from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from ...extensions import db
from ...models import User
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
