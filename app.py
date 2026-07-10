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

# ── Extension instances ────────────────────────────────
bcrypt        = Bcrypt()
login_manager = LoginManager()
csrf          = CSRFProtect()
limiter       = Limiter(
    key_func       = get_remote_address,
    default_limits = ['300 per minute'],
)

# ── Security Logger ───────────────────────────────────
security_logger = logging.getLogger('cybernews.security')
security_logger.setLevel(logging.WARNING)

file_handler = logging.FileHandler('security.log')
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
))
security_logger.addHandler(file_handler)


def create_app(config_name='development'):
    """Application factory."""

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

    # ── Rate limit the login endpoint ─────────────────
    login_view = app.view_functions.get('auth.login')
    if login_view:
        limiter.limit('10 per minute')(login_view)

    # ── Template globals ───────────────────────────────
    @app.template_global()
    def csrf_token_form():
        """Generate CSRF token input for plain HTML forms."""
        from flask_wtf.csrf import generate_csrf
        token = generate_csrf()
        return f'<input type="hidden" name="csrf_token" value="{token}">'

    # ═══════════════════════════════════════════════════
    # SECURITY MIDDLEWARE — runs before EVERY request
    # ═══════════════════════════════════════════════════
    @app.before_request
    def security_middleware():

        ip   = _get_ip()
        path = request.path.lower()
        url  = request.url.lower()
        ua   = request.headers.get('User-Agent', '').lower()

        # ── 1. Block attack tool user agents ───────────
        bad_agents = [
            'sqlmap', 'nikto', 'nmap', 'masscan',
            'dirbuster', 'gobuster', 'hydra',
            'burpsuite', 'metasploit', 'acunetix',
            'nessus', 'openvas', 'w3af', 'zaproxy',
        ]
        for agent in bad_agents:
            if agent in ua:
                _log_block(ip, 'Attack tool: ' + agent)
                abort(403)

        # ── 2. Block common scanner/attack paths ───────
        attack_paths = [
            '/wp-admin', '/wp-login', '/wp-content',
            '/wp-includes', '/xmlrpc.php', '/admin.php',
            '/phpmyadmin', '/.env', '/config.php',
            '/shell.php', '/cmd.php', '/eval.php',
            '/.git', '/.ssh',
            '/backup', '/db.sql', '/dump.sql',
        ]
        for attack_path in attack_paths:
            if path == attack_path or path.startswith(attack_path + '/'):
                _log_block(ip, 'Scanner path: ' + attack_path)
                abort(403)

        # ── 3. Block SQL injection in URL ──────────────
        sql_patterns = [
            "' or ", "' and ", "1=1", "union select",
            "drop table", "insert into", "'; drop",
            "exec(", "xp_cmdshell",
        ]
        for pattern in sql_patterns:
            if pattern in url:
                _log_block(ip, 'SQL injection: ' + pattern)
                abort(403)

        # ── 4. Block path traversal ────────────────────
        if '..' in path:
            _log_block(ip, 'Path traversal attempt')
            abort(403)

        # ── 5. Block very long URLs ────────────────────
        if len(url) > 2000:
            _log_block(ip, 'URL too long: ' + str(len(url)))
            abort(403)

    def _get_ip():
        """Get real client IP."""
        forwarded = request.headers.get('X-Forwarded-For')
        if forwarded:
            return forwarded.split(',')[0].strip()
        return request.remote_addr or 'unknown'

    def _log_block(ip, reason):
        """Log a blocked request to security.log."""
        security_logger.warning(
            'BLOCKED | IP: %s | Reason: %s | Path: %s | UA: %s',
            ip, reason, request.path,
            request.headers.get('User-Agent', '')[:80]
        )

    # ═══════════════════════════════════════════════════
    # SECURITY HEADERS — added to every response
    # ═══════════════════════════════════════════════════
    @app.after_request
    def apply_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options']        = 'SAMEORIGIN'
        response.headers['X-XSS-Protection']       = '1; mode=block'
        response.headers['Referrer-Policy']        = 'strict-origin-when-cross-origin'
        response.headers['Permissions-Policy']     = (
            'camera=(), microphone=(), geolocation=(), '
            'payment=(), usb=(), magnetometer=()'
        )
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
        return response

    # ═══════════════════════════════════════════════════
    # CONTEXT PROCESSORS
    # ═══════════════════════════════════════════════════
    @app.context_processor
    def inject_globals():
        from models import Article
        from flask_login import current_user

        try:
            from models import PageView
            total_views     = PageView.total_views()
            unique_visitors = PageView.unique_visitors()
        except Exception:
            total_views     = 0
            unique_visitors = 0

        return {
            'app_name':        app.config['APP_NAME'],
            'app_tagline':     app.config['APP_TAGLINE'],
            'categories':      app.config['CATEGORIES'],
            'current_year':    datetime.now().year,
            'current_user':    current_user,
            'total_views':     total_views,
            'unique_visitors': unique_visitors,
            'all_articles':    Article.query.filter_by(published=True)
                                            .order_by(Article.created_at.desc())
                                            .limit(10).all(),
        }

    # ═══════════════════════════════════════════════════
    # TEMPLATE FILTERS
    # ═══════════════════════════════════════════════════
    @app.template_filter('category_color')
    def category_color_filter(category):
        colors = {
            'Malware':         'malware',
            'Data Breaches':   'data-breaches',
            'Vulnerabilities': 'vulnerabilities',
            'Privacy':         'privacy',
            'Research':        'research',
            'Threats':         'threats',
        }
        return colors.get(category, 'research')

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

    return app


# ── Create app instance ────────────────────────────────
app = create_app('development')


if __name__ == '__main__':
    print("""
    ╔══════════════════════════════════════╗
    ║   🛡️  CyberNews Dev Server           ║
    ║   http://0.0.0.0:5000               ║
    ╚══════════════════════════════════════╝
    """)
    app.run(host='0.0.0.0', port=5000, debug=True)
