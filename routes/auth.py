# routes/auth.py
from flask import (
    Blueprint, render_template, redirect,
    url_for, flash, request, session,
)
from flask_login import (
    login_user, logout_user,
    login_required, current_user,
)
from models   import db, User, LoginLog
from datetime import datetime, timedelta
import re

auth_bp = Blueprint('auth', __name__)

# ── Brute force settings ───────────────────────────────
MAX_ATTEMPTS       = 5
LOCKOUT_MINUTES    = 15


def _get_ip():
    forwarded = request.headers.get('X-Forwarded-For')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return request.remote_addr or 'unknown'


def _is_locked_out(username, ip):
    """Check if IP or username is locked out."""
    window = datetime.utcnow() - timedelta(minutes=LOCKOUT_MINUTES)

    ip_failures = LoginLog.query.filter(
        LoginLog.ip_address == ip,
        LoginLog.success    == False,
        LoginLog.timestamp  >= window,
    ).count()

    user_failures = LoginLog.query.filter(
        LoginLog.username  == username,
        LoginLog.success   == False,
        LoginLog.timestamp >= window,
    ).count()

    return ip_failures >= MAX_ATTEMPTS or user_failures >= MAX_ATTEMPTS


def _remaining_attempts(username, ip):
    """How many attempts remain before lockout."""
    window = datetime.utcnow() - timedelta(minutes=LOCKOUT_MINUTES)

    ip_failures = LoginLog.query.filter(
        LoginLog.ip_address == ip,
        LoginLog.success    == False,
        LoginLog.timestamp  >= window,
    ).count()

    user_failures = LoginLog.query.filter(
        LoginLog.username  == username,
        LoginLog.success   == False,
        LoginLog.timestamp >= window,
    ).count()

    return max(0, MAX_ATTEMPTS - max(ip_failures, user_failures))


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Hardened login with brute force protection."""

    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard'))

    if request.method == 'POST':
        ip       = _get_ip()
        ua       = request.headers.get('User-Agent', '')
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        remember = request.form.get('remember') == 'on'

        # ── Basic validation ───────────────────────────
        if not username or not password:
            flash('Please enter both username and password.', 'error')
            return render_template('auth/login.html', username=username)

        # ── Sanitize username ──────────────────────────
        username = re.sub(r'[^a-zA-Z0-9_\-\.]', '', username)[:50]

        # ── Brute force check ──────────────────────────
        if _is_locked_out(username, ip):
            LoginLog.record(
                username=username, ip=ip,
                user_agent=ua, success=False,
            )
            flash(
                f'Too many failed attempts. '
                f'Please wait {LOCKOUT_MINUTES} minutes.',
                'error'
            )
            return render_template('auth/login.html')

        # ── Find user ──────────────────────────────────
        user = User.query.filter_by(username=username).first()

        # ── Verify password ────────────────────────────
        if user is None or not user.check_password(password):
            LoginLog.record(
                username=username, ip=ip,
                user_agent=ua, success=False,
            )

            remaining = _remaining_attempts(username, ip)

            if remaining > 0:
                flash(
                    f'Invalid username or password. '
                    f'{remaining} attempt{"s" if remaining != 1 else ""} remaining.',
                    'error'
                )
            else:
                flash(
                    f'Too many failed attempts. '
                    f'Please wait {LOCKOUT_MINUTES} minutes.',
                    'error'
                )

            return render_template('auth/login.html', username=username)

        # ── Check account active ───────────────────────
        if not user.is_active:
            flash('This account has been deactivated.', 'error')
            return render_template('auth/login.html')

        # ── Successful login ───────────────────────────
        login_user(user, remember=remember)
        user.update_last_login()

        LoginLog.record(
            username=username, ip=ip,
            user_agent=ua, success=True,
            user_id=user.id,
        )

        flash(f'Welcome back, {user.username}! 👋', 'success')

        # Safe redirect only
        next_page = request.args.get('next', '')
        if next_page and next_page.startswith('/') and not next_page.startswith('//'):
            return redirect(next_page)

        return redirect(url_for('admin.dashboard'))

    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    username = current_user.username
    logout_user()
    session.clear()
    flash(f'You have been logged out. See you soon, {username}!', 'info')
    return redirect(url_for('main.home'))


@auth_bp.route('/profile')
@login_required
def profile():
    login_history = LoginLog.query.filter_by(
        username=current_user.username
    ).order_by(LoginLog.timestamp.desc()).limit(10).all()

    return render_template(
        'auth/profile.html',
        login_history=login_history,
    )
