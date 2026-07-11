# app.py
# ─────────────────────────────────────────────────────────
# CyberNews — Main Application
# ─────────────────────────────────────────────────────────

from flask              import Flask, request, abort
from flask_login        import LoginManager
from flask_bcrypt       import Bcrypt
from flask_wtf.csrf     import CSRFProtect
from flask_limiter      import Limiter
from flask_limiter.util import get_remote_address
from config             import config
from models             import db
from routes             import all_blueprints
from datetime           import datetime
import logging
import os

# ── Extension instances ────────────────────────────────
bcrypt        = Bcrypt()
login_manager = LoginManager()
csrf          = CSRFProtect()
limiter       = Limiter(
    key_func       = get_remote_address,
    default_limits = ['300 per minute'],
    storage_uri    = 'memory://',
)

# ── Security Logger ───────────────────────────────────
security_logger = logging.getLogger('cybernews.security')
security_logger.setLevel(logging.WARNING)

_log_handler = logging.FileHandler('security.log')
_log_handler.setFormatter(logging.Formatter(
    '%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
))
security_logger.addHandler(_log_handler)


def create_app(config_name=None):
    """Application factory."""

    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # ── Initialize extensions ──────────────────────────
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)

    # ── Flask-Login settings ───────────────────────────
    login_manager.login_view             = 'auth.login'
    login_manager.login_message          = 'Please log in to access the admin panel.'
    login_manager.login_message_category = 'warning'

    # ── User loader ────────────────────────────────────
    @login_manager.user_loader
    def load_user(user_id):
        from models import User
        return db.session.get(User, int(user_id))

    # ── Register blueprints ────────────────────────────
    for blueprint in all_blueprints:
        app.register_blueprint(blueprint)

    # ── CSRF Exemptions for JSON APIs ──────────────────
    api_endpoints = [
        'main.api_subscribe',
        'main.api_search',
        'main.api_articles',
        'main.api_live_feed',
        'main.api_stats',
    ]
    for endpoint in api_endpoints:
        if endpoint in app.view_functions:
            csrf.exempt(app.view_functions[endpoint])

    # ── Rate limit login endpoint ──────────────────────
    login_view = app.view_functions.get('auth.login')
    if login_view:
        limiter.limit('10 per minute')(login_view)

    # ═══════════════════════════════════════════════════
    # SECURITY MIDDLEWARE
    # ═══════════════════════════════════════════════════
    @app.before_request
    def security_middleware():
        """Block malicious requests before Flask processes them."""

        ip   = _get_ip()
        path = request.path.lower()
        url  = request.url.lower()
        ua   = request.headers.get('User-Agent', '').lower()

        # ── Allow static files ─────────────────────────
        if path.startswith('/static/'):
            return None

        # ── Block attack tools by User-Agent ──────────
        bad_agents = [
            'sqlmap', 'nikto', 'nmap', 'masscan',
            'dirbuster', 'gobuster', 'hydra', 'burpsuite',
            'metasploit', 'acunetix', 'nessus', 'openvas',
            'w3af', 'zaproxy', 'havij', 'pangolin',
        ]
        for agent in bad_agents:
            if agent in ua:
                _log_block(ip, f'Attack tool: {agent}')
                abort(403)

        # ── Block scanner/attack paths ─────────────────
        attack_paths = [
            '/wp-admin', '/wp-login', '/wp-content',
            '/wp-includes', '/xmlrpc.php', '/admin.php',
            '/phpmyadmin', '/.env', '/config.php',
            '/shell.php', '/cmd.php', '/eval.php',
            '/.git', '/.ssh', '/backup',
            '/db.sql', '/dump.sql', '/database.sql',
            '/config.yml', '/config.yaml',
            '/actuator', '/console', '/.htaccess',
        ]
        for attack_path in attack_paths:
            if path == attack_path or path.startswith(attack_path + '/'):
                _log_block(ip, f'Scanner path: {attack_path}')
                abort(403)

        # ── Block SQL injection in query string ────────
        query_string = request.query_string.decode('utf-8', errors='ignore').lower()
        sql_patterns = [
            "' or ", "' and ", "union select",
            "drop table", "insert into", "'; drop",
            "exec(", "xp_cmdshell", "waitfor delay",
            "benchmark(", "sleep(",
        ]
        for pattern in sql_patterns:
            if pattern in query_string:
                _log_block(ip, f'SQL injection: {pattern}')
                abort(403)

        # ── Block path traversal ───────────────────────
        if '..' in path or '%2e%2e' in url:
            _log_block(ip, 'Path traversal')
            abort(403)

        # ── Block excessively long URLs ────────────────
        if len(url) > 2000:
            _log_block(ip, f'URL too long: {len(url)}')
            abort(403)

        # ── Block requests with no User-Agent ─────────
        # (real browsers always send User-Agent)
        # Comment out if causing issues with legitimate bots
        # if not request.headers.get('User-Agent'):
        #     _log_block(ip, 'Missing User-Agent')
        #     abort(403)

        return None

    # ═══════════════════════════════════════════════════
    # PAGE VIEW TRACKING
    # ═══════════════════════════════════════════════════
    @app.before_request
    def track_all_pages():
        """Automatically track every page view."""
        path = request.path

        skip_prefixes = [
            '/static/', '/api/', '/admin',
            '/favicon', '/robots.txt', '/sitemap.xml',
        ]

        for prefix in skip_prefixes:
            if path.startswith(prefix):
                return None

        if request.method != 'GET':
            return None

        try:
            from models import PageView
            ip = _get_ip()
            PageView.record_view(
                page       = path,
                ip         = ip,
                user_agent = request.headers.get('User-Agent'),
                referrer   = request.headers.get('Referer', ''),
            )
        except Exception:
            try:
                db.session.rollback()
            except Exception:
                pass

        return None

    # ═══════════════════════════════════════════════════
    # SECURITY HEADERS
    # ═══════════════════════════════════════════════════
    @app.after_request
    def apply_security_headers(response):
        """Add security headers to every response."""

        # Prevent MIME type sniffing
        response.headers['X-Content-Type-Options'] = 'nosniff'

        # Prevent clickjacking
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'

        # XSS protection for older browsers
        response.headers['X-XSS-Protection'] = '1; mode=block'

        # Control referrer information
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'

        # Restrict browser features
        response.headers['Permissions-Policy'] = (
            'camera=(), microphone=(), geolocation=(), '
            'payment=(), usb=(), magnetometer=()'
        )

        # Content Security Policy
        response.headers['Content-Security-Policy'] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' cdnjs.cloudflare.com; "
            "style-src 'self' 'unsafe-inline' "
            "fonts.googleapis.com cdnjs.cloudflare.com; "
            "font-src 'self' fonts.gstatic.com cdnjs.cloudflare.com; "
            "img-src 'self' data: https:; "
            "connect-src 'self'; "
            "frame-ancestors 'none';"
        )

        # Hide server information
        response.headers.pop('Server', None)

        return response

    # ═══════════════════════════════════════════════════
    # CONTEXT PROCESSORS
    # ═══════════════════════════════════════════════════
    @app.context_processor
    def inject_globals():
        from models import Article, PageView
        from flask_login import current_user

        try:
            total_views     = PageView.total_views()
            unique_visitors = PageView.unique_visitors()
        except Exception:
            total_views     = 0
            unique_visitors = 0

        try:
            recent = Article.query.filter_by(published=True) \
                                  .order_by(Article.created_at.desc()) \
                                  .limit(10).all()
        except Exception:
            recent = []

        return {
            'app_name':        app.config['APP_NAME'],
            'app_tagline':     app.config['APP_TAGLINE'],
            'categories':      app.config['CATEGORIES'],
            'current_year':    datetime.now().year,
            'current_user':    current_user,
            'total_views':     total_views,
            'unique_visitors': unique_visitors,
            'all_articles':    recent,
        }

    # ═══════════════════════════════════════════════════
    # TEMPLATE FILTERS
    # ═══════════════════════════════════════════════════
    @app.template_filter('category_color')
    def category_color_filter(category):
        return {
            'Malware':         'malware',
            'Data Breaches':   'data-breaches',
            'Vulnerabilities': 'vulnerabilities',
            'Privacy':         'privacy',
            'Research':        'research',
            'Threats':         'threats',
        }.get(category, 'research')

    @app.template_filter('reading_time')
    def reading_time_filter(text):
        words   = len(text.split()) if text else 0
        minutes = max(1, round(words / 200))
        return f"{minutes} min read"

    @app.template_filter('truncate_words')
    def truncate_words_filter(text, num=25):
        words = text.split()
        if len(words) <= num:
            return text
        return ' '.join(words[:num]) + '...'

    @app.template_global()
    def csrf_token_form():
        from flask_wtf.csrf import generate_csrf
        token = generate_csrf()
        return f'<input type="hidden" name="csrf_token" value="{token}">'

    return app


# ── Helper functions ───────────────────────────────────
def _get_ip():
    forwarded = request.headers.get('X-Forwarded-For')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return request.remote_addr or 'unknown'


def _log_block(ip, reason):
    security_logger.warning(
        'BLOCKED | IP: %s | Reason: %s | Path: %s | UA: %s',
        ip, reason, request.path,
        request.headers.get('User-Agent', '')[:80]
    )


# ── Create app instance ────────────────────────────────
app = create_app()


if __name__ == '__main__':
    print("""
    ╔══════════════════════════════════════╗
    ║   🛡️  CyberNews Dev Server           ║
    ║   http://0.0.0.0:5000               ║
    ╚══════════════════════════════════════╝
    """)
    app.run(host='0.0.0.0', port=5000, debug=True)
