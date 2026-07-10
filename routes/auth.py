# routes/auth.py
# ─────────────────────────────────────────────────────────
# Authentication routes for CyberNews:
#
#   GET  /login   → show login form
#   POST /login   → process login attempt
#   GET  /logout  → log user out
#   GET  /profile → logged-in user's profile
# ─────────────────────────────────────────────────────────

from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    request,
)
from flask_login import (
    login_user,
    logout_user,
    login_required,
    current_user,
)
from models   import db, User
from datetime import datetime

auth_bp = Blueprint('auth', __name__)


# ─────────────────────────────────────────
# LOGIN
# ─────────────────────────────────────────
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    GET:  Show the login form.
    POST: Validate credentials and log the user in.
    """

    # If user is already logged in, send them to admin
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard'))

    if request.method == 'POST':

        # Get form data
        # request.form is a dictionary of submitted values
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        remember = request.form.get('remember') == 'on'

        # ── Basic validation ───────────────────────────
        if not username or not password:
            flash('Please enter both username and password.', 'error')
            return render_template('auth/login.html', username=username)

        # ── Find the user ──────────────────────────────
        user = User.query.filter_by(username=username).first()

        # ── Verify password ────────────────────────────
        # IMPORTANT: We check both conditions together.
        # This prevents "username not found" vs "wrong password"
        # error messages that help attackers enumerate usernames.
        if user is None or not user.check_password(password):
            flash('Invalid username or password.', 'error')
            return render_template('auth/login.html', username=username)

        # ── Check account is active ────────────────────
        if not user.is_active:
            flash('This account has been deactivated.', 'error')
            return render_template('auth/login.html')

        # ── Log the user in ────────────────────────────
        # login_user() stores the user ID in the session cookie
        # remember=True sets a persistent cookie (stays after browser closes)
        login_user(user, remember=remember)

        # Update last login timestamp
        user.update_last_login()

        flash(f'Welcome back, {user.username}! 👋', 'success')

        # ── Redirect to originally requested page ──────
        # If user tried to visit /admin/articles before logging in,
        # Flask-Login saved that URL in 'next' parameter.
        # We redirect them there after login.
        next_page = request.args.get('next')

        # Security: only allow redirects to our own site
        # (prevent open redirect attacks)
        if next_page and next_page.startswith('/'):
            return redirect(next_page)

        return redirect(url_for('admin.dashboard'))

    # GET request: show the empty login form
    return render_template('auth/login.html')


# ─────────────────────────────────────────
# LOGOUT
# ─────────────────────────────────────────
@auth_bp.route('/logout')
@login_required   # Must be logged in to log out
def logout():
    """
    Clear the session and redirect to the homepage.
    logout_user() removes the user from the session.
    """
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
    """Show the logged-in user's profile."""
    return render_template('auth/profile.html')
