# routes/auth.py
# Now with: rate limiting awareness, audit logging,
# input sanitization, and brute force protection

from flask import (
    Blueprint, render_template, redirect,
    url_for, flash, request,
)
from flask_login import (
    login_user, logout_user,
    login_required, current_user,
)
from models   import db, User, LoginLog
from security import (
    sanitize_string,
    log_login_attempt,
    get_client_ip,
    log_suspicious_activity,
)
from datetime import datetime, timedelta

auth_bp = Blueprint('auth', __name__)


# ── Brute force detection ──────────────────────────────
# How many failed attempts before we slow down responses
MAX_FAILED_ATTEMPTS = 5
LOCKOUT_WINDOW_MINUTES = 15


def check_brute_force(username, ip):
    """
    Check if this username or IP has too many recent
    failed login attempts.
    
    Returns True if we should block the attempt.
    """
    window = datetime.utcnow() - timedelta(minutes=LOCKOUT_WINDOW_MINUTES)

    # Count recent failures from this IP
    ip_failures = LoginLog.query.filter(
        LoginLog.ip_address == ip,
        LoginLog.success    == False,
        LoginLog.timestamp  >= window,
    ).count()

    # Count recent failures for this username
    user_failures = LoginLog.query.filter(
        LoginLog.username == username,
        LoginLog.success  == False,
        LoginLog.timestamp >= window,
    ).count()

    return ip_failures >= MAX_FAILED_ATTEMPTS or \
           user_failures >= MAX_FAILED_ATTEMPTS


# ─────────────────────────────────────────
# LOGIN
# ─────────────────────────────────────────
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Hardened login with audit logging and brute force detection."""

    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard'))

    if request.method == 'POST':

        # ── Sanitize inputs ────────────────────────────
        username = sanitize_string(
            request.form.get('username', ''),
            max_length=50
        )
        password = request.form.get('password', '').strip()
        remember = request.form.get('remember') == 'on'
        ip       = get_client_ip()
        ua       = request.headers.get('User-Agent', '')

        # ── Basic validation ───────────────────────────
        if not username or not password:
            flash('Please enter both username and password.', 'error')
            return render_template('auth/login.html', username=username)

        # ── Brute force check ──────────────────────────
        if check_brute_force(username, ip):
            log_suspicious_activity(
                f'Brute force detected for username: {username}'
            )
            flash(
                f'Too many failed attempts. '
                f'Please wait {LOCKOUT_WINDOW_MINUTES} minutes before trying again.',
                'error'
            )
            return render_template('auth/login.html')

        # ── Find user and verify password ──────────────
        user = User.query.filter_by(username=username).first()

        # We check both conditions together intentionally
        # so attackers cannot tell if the username exists
        if user is None or not user.check_password(password):

            # Log the failed attempt
            LoginLog.record(
                username   = username,
                ip         = ip,
                user_agent = ua,
                success    = False,
            )
            log_login_attempt(username, success=False, ip=ip)

            # Count remaining attempts
            window    = datetime.utcnow() - timedelta(minutes=LOCKOUT_WINDOW_MINUTES)
            failures  = LoginLog.query.filter(
                LoginLog.username == username,
                LoginLog.success  == False,
                LoginLog.timestamp >= window,
            ).count()
            remaining = max(0, MAX_FAILED_ATTEMPTS - failures)

            if remaining > 0:
                flash(
                    f'Invalid username or password. '
                    f'{remaining} attempt{"s" if remaining != 1 else ""} remaining.',
                    'error'
                )
            else:
                flash(
                    'Too many failed attempts. '
                    f'Please wait {LOCKOUT_WINDOW_MINUTES} minutes.',
                    'error'
                )

            return render_template('auth/login.html', username=username)

        # ── Check account is active ────────────────────
        if not user.is_active:
            log_suspicious_activity(
                f'Login attempt on deactivated account: {username}'
            )
            flash('This account has been deactivated.', 'error')
            return render_template('auth/login.html')

        # ── Successful login ───────────────────────────
        login_user(user, remember=remember)
        user.update_last_login()

        # Record the successful login
        LoginLog.record(
            username   = username,
            ip         = ip,
            user_agent = ua,
            success    = True,
            user_id    = user.id,
        )
        log_login_attempt(username, success=True, ip=ip)

        flash(f'Welcome back, {user.username}! 👋', 'success')

        # Safe redirect
        next_page = request.args.get('next')
        if next_page and next_page.startswith('/'):
            return redirect(next_page)

        return redirect(url_for('admin.dashboard'))

    return render_template('auth/login.html')


# ─────────────────────────────────────────
# LOGOUT
# ─────────────────────────────────────────
@auth_bp.route('/logout')
@login_required
def logout():
    username = current_user.username
    logout_user()
    flash(f'You have been logged out. See you soon, {username}!', 'info')
    return redirect(url_for('main.home'))


# ─────────────────────────────────────────
# PROFILE
# ─────────────────────────────────────────
@auth_bp.route('/profile')
@login_required
def profile():
    """Show profile with recent login history."""

    # Get last 10 login attempts for this user
    login_history = LoginLog.query.filter_by(
        username=current_user.username
    ).order_by(LoginLog.timestamp.desc()).limit(10).all()

    return render_template(
        'auth/profile.html',
        login_history=login_history,
    )
