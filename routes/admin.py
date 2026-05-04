from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from extensions import db
from models.user import User, AuditLog
from models.case import Case
from models.evidence import EvidenceFile
from datetime import datetime, timedelta

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    """Decorator to require admin access"""
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.role != 'admin':
            flash('Access denied. Admin only.', 'danger')
            return redirect(url_for('dashboard.index'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/users')
@login_required
@admin_required
def users_list():
    """List all users"""
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=users)

@admin_bp.route('/users/create', methods=['POST'])
@login_required
@admin_required
def create_user():
    """Create new user"""
    email = request.form.get('email')
    username = request.form.get('username')
    full_name = request.form.get('full_name')
    badge_number = request.form.get('badge_number')
    password = request.form.get('password')
    role = request.form.get('role', 'examiner')
    
    if User.query.filter_by(email=email).first():
        flash('Email already exists.', 'danger')
        return redirect(url_for('admin.users_list'))
    
    if User.query.filter_by(username=username).first():
        flash('Username already exists.', 'danger')
        return redirect(url_for('admin.users_list'))
    
    user = User(
        email=email,
        username=username,
        full_name=full_name,
        badge_number=badge_number,
        role=role
    )
    user.set_password(password)
    
    db.session.add(user)
    
    # Audit log
    log = AuditLog(
        user_id=current_user.id,
        action='USER_CREATED',
        details=f'Created user {email} with role {role}',
        ip_address=request.remote_addr,
        timestamp=datetime.utcnow()
    )
    db.session.add(log)
    db.session.commit()
    
    flash(f'User {full_name} created successfully!', 'success')
    return redirect(url_for('admin.users_list'))

@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    """Delete a user"""
    if user_id == current_user.id:
        flash('Cannot delete yourself.', 'danger')
        return redirect(url_for('admin.users_list'))
    
    user = User.query.get_or_404(user_id)
    name = user.full_name
    
    # Audit log before deletion
    log = AuditLog(
        user_id=current_user.id,
        action='USER_DELETED',
        details=f'Deleted user {user.email}',
        ip_address=request.remote_addr,
        timestamp=datetime.utcnow()
    )
    db.session.add(log)
    
    db.session.delete(user)
    db.session.commit()
    
    flash(f'User {name} deleted.', 'info')
    return redirect(url_for('admin.users_list'))

@admin_bp.route('/users/<int:user_id>/toggle-status', methods=['POST'])
@login_required
@admin_required
def toggle_user_status(user_id):
    """Activate/deactivate a user"""
    if user_id == current_user.id:
        flash('Cannot change your own status.', 'danger')
        return redirect(url_for('admin.users_list'))
    
    user = User.query.get_or_404(user_id)
    user.is_active = not user.is_active
    
    status = 'activated' if user.is_active else 'deactivated'
    
    log = AuditLog(
        user_id=current_user.id,
        action='USER_STATUS_CHANGED',
        details=f'{status} user {user.email}',
        ip_address=request.remote_addr,
        timestamp=datetime.utcnow()
    )
    db.session.add(log)
    db.session.commit()
    
    flash(f'User {user.full_name} {status}.', 'info')
    return redirect(url_for('admin.users_list'))

@admin_bp.route('/audit-logs')
@login_required
@admin_required
def audit_logs():
    """View system audit logs"""
    page = request.args.get('page', 1, type=int)
    user_filter = request.args.get('user_id', type=int)
    
    query = AuditLog.query
    
    if user_filter:
        query = query.filter_by(user_id=user_filter)
    
    logs = query.order_by(AuditLog.timestamp.desc()).paginate(page=page, per_page=50, error_out=False)
    users = User.query.all()
    
    return render_template('admin/audit_logs.html', logs=logs, users=users, selected_user=user_filter)

@admin_bp.route('/user-activity/<int:user_id>')
@login_required
@admin_required
def user_activity(user_id):
    """View detailed activity for a specific user"""
    user = User.query.get_or_404(user_id)
    
    # Get all actions by this user
    logs = AuditLog.query.filter_by(user_id=user_id)\
        .order_by(AuditLog.timestamp.desc()).limit(100).all()
    
    # Calculate session information
    login_logs = [l for l in logs if l.action == 'LOGIN']
    logout_logs = [l for l in logs if l.action == 'LOGOUT']
    
    # Calculate time spent
    total_time = user.total_time_spent or 0
    hours = total_time // 3600
    minutes = (total_time % 3600) // 60
    seconds = total_time % 60
    
    time_str = f"{hours}h {minutes}m {seconds}s"
    
    return render_template('admin/user_activity.html', 
                         user=user, 
                         logs=logs,
                         login_logs=login_logs,
                         logout_logs=logout_logs,
                         time_str=time_str)

@admin_bp.route('/recent-cases')
@login_required
@admin_required
def recent_cases():
    """View recent cases from all users"""
    days = request.args.get('days', 7, type=int)
    since = datetime.utcnow() - timedelta(days=days)
    
    cases = Case.query.filter(Case.created_at >= since)\
        .order_by(Case.created_at.desc()).all()
    
    return render_template('admin/recent_cases.html', cases=cases, days=days)