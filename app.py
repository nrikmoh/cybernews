# app.py
from flask import Flask
from flask_login  import LoginManager
from flask_bcrypt import Bcrypt
from flask_wtf.csrf import CSRFProtect
from config       import config
from models       import db
from routes       import all_blueprints
from datetime     import datetime

# ── Extension instances ────────────────────────────────
# Created here (outside create_app) so they can be
# imported by other modules like models.py
bcrypt       = Bcrypt()
login_manager = LoginManager()
csrf          = CSRFProtect()


def create_app(config_name='development'):
    """Application factory."""

    app = Flask(__name__)

    # ── Load config ────────────────────────────────────
    app.config.from_object(config[config_name])

    # ── Initialize extensions ──────────────────────────
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    # ── Flask-Login settings ───────────────────────────
    # Where to redirect when @login_required fails
    login_manager.login_view       = 'auth.login'

    # The flash message shown when redirected
    login_manager.login_message    = 'Please log in to access the admin panel.'

    # Message category (used for CSS styling)
    login_manager.login_message_category = 'warning'

    # ── User loader ────────────────────────────────────
    # Flask-Login calls this function on every request
    # to reload the user from the session.
    # It receives the user_id stored in the session cookie
    # and must return the User object (or None).
    @login_manager.user_loader
    def load_user(user_id):
        from models import User
        # Integer cast because get_id() returns a string
        return db.session.get(User, int(user_id))

    # ── Register blueprints ────────────────────────────
    for blueprint in all_blueprints:
        app.register_blueprint(blueprint)

    # ── Context processors ─────────────────────────────
    @app.context_processor
    def inject_globals():
        from models import Article
        from flask_login import current_user
        return {
            'app_name':      app.config['APP_NAME'],
            'app_tagline':   app.config['APP_TAGLINE'],
            'categories':    app.config['CATEGORIES'],
            'current_year':  datetime.now().year,
            'current_user':  current_user,
            'all_articles':  Article.query.filter_by(published=True)
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


# ── Create the app instance ────────────────────────────
app = create_app('development')


if __name__ == '__main__':
    print("""
    ╔══════════════════════════════════════╗
    ║   🛡️  CyberNews Dev Server           ║
    ║   http://0.0.0.0:5000               ║
    ╚══════════════════════════════════════╝
    """)
    app.run(host='0.0.0.0', port=5000, debug=True)
