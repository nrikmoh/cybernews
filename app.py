# app.py
from flask            import Flask, request
from flask_login      import LoginManager
from flask_bcrypt     import Bcrypt
from flask_wtf.csrf   import CSRFProtect
from flask_limiter    import Limiter
from flask_limiter.util import get_remote_address
from config           import config
from models           import db
from routes           import all_blueprints
from security         import add_security_headers
from datetime         import datetime

# ── Extension instances ────────────────────────────────
bcrypt        = Bcrypt()
login_manager = LoginManager()
csrf          = CSRFProtect()

# Rate limiter — limits how many requests per minute
# get_remote_address extracts the client's IP automatically
limiter = Limiter(
    key_func   = get_remote_address,
    default_limits = ['200 per minute'],  # global default
)


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

    # ── Security headers on every response ────────────
    # This function runs after every request and adds
    # security headers to the response
    @app.after_request
    def apply_security_headers(response):
        return add_security_headers(response)

    # ── Content Security Policy ────────────────────────
    # CSP tells the browser which sources are allowed
    # to load scripts, styles, images, etc.
    # This is one of the strongest XSS defenses.
    @app.after_request
    def add_csp(response):
        response.headers['Content-Security-Policy'] = (
            # Scripts: only from our server and CDNs we use
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' cdnjs.cloudflare.com; "
            # Styles: our server + Google Fonts + Font Awesome
            "style-src 'self' 'unsafe-inline' "
            "fonts.googleapis.com cdnjs.cloudflare.com; "
            # Fonts: our server + Google Fonts
            "font-src 'self' fonts.gstatic.com cdnjs.cloudflare.com; "
            # Images: our server + HTTPS sources (for Unsplash etc.)
            "img-src 'self' data: https:; "
            # API calls: only to our own server
            "connect-src 'self'; "
            # No iframes allowed
            "frame-ancestors 'none';"
        )
        return response

    # ── Context processors ─────────────────────────────
    @app.context_processor
    def inject_globals():
        from models import Article
        from flask_login import current_user
        return {
            'app_name':     app.config['APP_NAME'],
            'app_tagline':  app.config['APP_TAGLINE'],
            'categories':   app.config['CATEGORIES'],
            'current_year': datetime.now().year,
            'current_user': current_user,
            'all_articles': Article.query.filter_by(published=True)
                                         .order_by(Article.created_at.desc())
                                         .limit(10).all(),
        }

    # ── Template filters ───────────────────────────────
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


# ── Apply rate limits to sensitive routes ──────────────
# We do this after app creation so we can import the routes
# 5 login attempts per minute per IP
from routes.auth import auth_bp
limiter.limit('5 per minute')(auth_bp)


if __name__ == '__main__':
    print("""
    ╔══════════════════════════════════════╗
    ║   🛡️  CyberNews Dev Server           ║
    ║   http://0.0.0.0:5000               ║
    ╚══════════════════════════════════════╝
    """)
    app.run(host='0.0.0.0', port=5000, debug=True)
