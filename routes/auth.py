from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from extensions import db
from models.user import User, AuditLog
from datetime import datetime
import time

auth_bp = Blueprint('auth', __name__)

@auth_bp.before_app_request
def track_user_activity():
    """Track user activity on each request"""
    if current_user.is_authenticated:
        current_user.last_activity = datetime.utcnow()
        db.session.commit()

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = request.form.get('remember') == 'on'
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            if user.is_active:
                login_user(user, remember=remember)
                user.last_login = datetime.utcnow()
                session['login_time'] = time.time()
                
                # Audit log
                log = AuditLog(
                    user_id=user.id,
                    action='LOGIN',
                    details=f'User logged in from {request.remote_addr}',
                    ip_address=request.remote_addr,
                    timestamp=datetime.utcnow()
                )
                db.session.add(log)
                db.session.commit()
                
                next_page = request.args.get('next')
                if user.role == 'admin':
                    flash(f'Welcome Administrator {user.full_name}!', 'success')
                    return redirect(next_page or url_for('dashboard.admin_dashboard'))
                else:
                    flash(f'Welcome back, {user.full_name}!', 'success')
                    return redirect(next_page or url_for('dashboard.index'))
            else:
                flash('Your account has been deactivated. Contact administrator.', 'danger')
        else:
            flash('Invalid email or password.', 'danger')
    
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        full_name = request.form.get('full_name')
        badge_number = request.form.get('badge_number')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return render_template('register.html')
        
        if User.query.filter_by(username=username).first():
            flash('Username already taken.', 'danger')
            return render_template('register.html')
        
        # First registered user becomes admin
        is_first = User.query.count() == 0
        role = 'admin' if is_first else 'examiner'
        
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
            user_id=1 if not is_first else None,
            action='REGISTER',
            details=f'New user registered: {email} as {role}',
            ip_address=request.remote_addr,
            timestamp=datetime.utcnow()
        )
        db.session.add(log)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    # Calculate session duration
    login_time = session.get('login_time')
    if login_time:
        duration = int(time.time() - login_time)
        current_user.total_time_spent = (current_user.total_time_spent or 0) + duration
    
    current_user.last_logout = datetime.utcnow()
    
    # Audit log
    log = AuditLog(
        user_id=current_user.id,
        action='LOGOUT',
        details=f'User logged out. Session duration: {duration if login_time else "unknown"}s',
        ip_address=request.remote_addr,
        timestamp=datetime.utcnow()
    )
    db.session.add(log)
    db.session.commit()
    
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/profile')
@login_required
def profile():
    return render_template('profile.html')