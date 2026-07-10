# security.py
# ─────────────────────────────────────────────────────────
# Security utilities for CyberNews.
#
# This module handles:
# 1. Input sanitization and validation
# 2. Security helper functions
# 3. Audit logging
# ─────────────────────────────────────────────────────────

import re
import html
import logging
from datetime  import datetime
from functools import wraps
from flask     import request, abort, current_app
from flask_login import current_user


# ── Set up security logger ─────────────────────────────
# This creates a separate log file just for security events
# so we can monitor suspicious activity

logging.basicConfig(level=logging.INFO)
security_logger = logging.getLogger('cybernews.security')

# Create file handler — writes security events to a file
file_handler = logging.FileHandler('security.log')
file_handler.setLevel(logging.WARNING)

# Format: timestamp | level | message
formatter = logging.Formatter(
    '%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
file_handler.setFormatter(formatter)
security_logger.addHandler(file_handler)


# ═══════════════════════════════════════════════════════
# 1. INPUT SANITIZATION
# Clean user input before using it
# ═══════════════════════════════════════════════════════

def sanitize_string(text, max_length=500):
    """
    Clean a text string for safe use.
    
    Steps:
    1. Convert to string (in case non-string passed)
    2. Strip whitespace from both ends
    3. Escape HTML special characters
       e.g. <script> becomes &lt;script&gt;
    4. Enforce maximum length
    
    Usage:
        title = sanitize_string(request.form.get('title'), max_length=300)
    """
    if text is None:
        return ''

    # Convert to string
    text = str(text)

    # Strip leading/trailing whitespace
    text = text.strip()

    # Escape HTML to prevent XSS
    # < → &lt;    > → &gt;    & → &amp;    " → &quot;
    text = html.escape(text)

    # Enforce length limit
    text = text[:max_length]

    return text


def sanitize_url(url, max_length=500):
    """
    Validate and clean a URL.
    Only allows http:// and https:// URLs.
    Rejects javascript: and data: URLs which can be used for XSS.
    """
    if not url:
        return ''

    url = str(url).strip()

    # Only allow safe URL schemes
    if not url.startswith(('http://', 'https://')):
        return ''

    # Limit length
    return url[:max_length]


def sanitize_email(email):
    """
    Validate and clean an email address.
    Returns the cleaned email or empty string if invalid.
    """
    if not email:
        return ''

    email = str(email).strip().lower()

    # Basic email format check using regex
    # This checks: something@something.something
    pattern = r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return ''

    return email[:120]


def sanitize_search_query(query, max_length=100):
    """
    Clean a search query.
    Removes characters that could cause issues in SQL LIKE queries.
    SQLAlchemy parameterizes queries so SQL injection is already
    prevented, but we clean the input anyway for extra safety.
    """
    if not query:
        return ''

    query = str(query).strip()

    # Remove characters that have no place in a search query
    # Keep: letters, numbers, spaces, hyphens, dots
    query = re.sub(r'[^\w\s\-\.]', '', query)

    return query[:max_length]


def validate_password_strength(password):
    """
    Check if a password meets minimum security requirements.
    
    Returns: (is_valid: bool, message: str)
    
    Requirements:
    - At least 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one number
    """
    if len(password) < 8:
        return False, 'Password must be at least 8 characters long.'

    if not re.search(r'[A-Z]', password):
        return False, 'Password must contain at least one uppercase letter.'

    if not re.search(r'[a-z]', password):
        return False, 'Password must contain at least one lowercase letter.'

    if not re.search(r'\d', password):
        return False, 'Password must contain at least one number.'

    return True, 'Password is strong.'


# ═══════════════════════════════════════════════════════
# 2. SECURITY DECORATORS
# Python decorators that add security checks to routes
# ═══════════════════════════════════════════════════════

def admin_required(f):
    """
    Decorator that requires the user to be an admin.
    Use this on top of @login_required for admin-only routes.
    
    Usage:
        @app.route('/admin/dangerous')
        @login_required
        @admin_required
        def dangerous_action():
            ...
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            abort(403)
        if current_user.role != 'admin':
            # Log this suspicious access attempt
            security_logger.warning(
                f'UNAUTHORIZED ACCESS ATTEMPT | '
                f'User: {current_user.username} | '
                f'Role: {current_user.role} | '
                f'URL: {request.url} | '
                f'IP: {get_client_ip()}'
            )
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


# ═══════════════════════════════════════════════════════
# 3. AUDIT LOGGING
# Record important security events
# ═══════════════════════════════════════════════════════

def get_client_ip():
    """
    Get the real client IP address.
    
    When behind a proxy (like Nginx), the real IP is in
    the X-Forwarded-For header, not request.remote_addr.
    We check both.
    """
    # Check for proxy header first
    forwarded_for = request.headers.get('X-Forwarded-For')
    if forwarded_for:
        # X-Forwarded-For can be a comma-separated list
        # The first IP is the original client
        return forwarded_for.split(',')[0].strip()

    return request.remote_addr or 'unknown'


def log_login_attempt(username, success, ip=None):
    """
    Log a login attempt to the security log file.
    
    We log BOTH successes and failures:
    - Failures help detect brute force attacks
    - Successes help detect account compromise
    """
    ip     = ip or get_client_ip()
    status = 'SUCCESS' if success else 'FAILED'
    level  = logging.INFO if success else logging.WARNING

    security_logger.log(
        level,
        f'LOGIN {status} | '
        f'Username: {username} | '
        f'IP: {ip} | '
        f'User-Agent: {request.headers.get("User-Agent", "unknown")[:100]}'
    )


def log_admin_action(action, details=''):
    """
    Log an administrative action.
    Creates an audit trail of who did what and when.
    """
    username = current_user.username if current_user.is_authenticated else 'anonymous'
    ip       = get_client_ip()

    security_logger.info(
        f'ADMIN ACTION | '
        f'User: {username} | '
        f'Action: {action} | '
        f'Details: {details} | '
        f'IP: {ip}'
    )


def log_suspicious_activity(description):
    """Log suspicious activity for review."""
    ip = get_client_ip()
    security_logger.warning(
        f'SUSPICIOUS | '
        f'{description} | '
        f'IP: {ip} | '
        f'URL: {request.url} | '
        f'Method: {request.method}'
    )


# ═══════════════════════════════════════════════════════
# 4. SECURITY HEADERS
# HTTP headers that tell browsers to be more secure
# ═══════════════════════════════════════════════════════

def add_security_headers(response):
    """
    Add security headers to every HTTP response.
    
    These headers tell the browser how to behave securely.
    Think of them as security instructions for the browser.
    """

    # ── X-Content-Type-Options ─────────────────────────
    # Prevents browser from guessing the content type.
    # Stops "MIME sniffing" attacks.
    response.headers['X-Content-Type-Options'] = 'nosniff'

    # ── X-Frame-Options ────────────────────────────────
    # Prevents your site from being embedded in an iframe.
    # Stops "clickjacking" attacks where attackers overlay
    # invisible iframes over your site to steal clicks.
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'

    # ── X-XSS-Protection ───────────────────────────────
    # Tells older browsers to block XSS attacks.
    # Modern browsers don't need this (they have CSP)
    # but it doesn't hurt to include it.
    response.headers['X-XSS-Protection'] = '1; mode=block'

    # ── Referrer-Policy ────────────────────────────────
    # Controls what URL information is sent when clicking links.
    # 'strict-origin-when-cross-origin' = send full path for
    # same-origin links, only the domain for cross-origin links.
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'

    # ── Permissions-Policy ─────────────────────────────
    # Disables browser features we don't use.
    # Reduces attack surface.
    response.headers['Permissions-Policy'] = (
        'camera=(), microphone=(), geolocation=(), '
        'payment=(), usb=(), magnetometer=()'
    )

    # ── Remove Server header ───────────────────────────
    # Don't reveal what server software we're running.
    # Attackers use this to find known vulnerabilities.
    response.headers.pop('Server', None)

    return response
