# routes/errors.py
# ─────────────────────────────────────────────────────────
# Custom error pages for CyberNews.
# Instead of showing Flask's default ugly error pages,
# we show styled pages that match our site design.
# ─────────────────────────────────────────────────────────

from flask import Blueprint, render_template

errors_bp = Blueprint('errors', __name__)


@errors_bp.app_errorhandler(404)
def not_found(error):
    """
    Page Not Found.
    Triggered when someone visits a URL that doesn't exist.
    We must return the template AND the status code (404).
    """
    return render_template('errors/404.html'), 404


@errors_bp.app_errorhandler(500)
def server_error(error):
    """
    Internal Server Error.
    Triggered when something goes wrong in our Python code.
    """
    return render_template('errors/500.html'), 500


@errors_bp.app_errorhandler(403)
def forbidden(error):
    """
    Forbidden.
    Triggered when a user tries to access something they shouldn't.
    We'll use this later for admin-only pages.
    """
    return render_template('errors/403.html'), 403
