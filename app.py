# app.py
from flask import Flask
from config import config
from models import db
from routes import all_blueprints
from datetime import datetime


def create_app(config_name='development'):
    """Application factory."""

    app = Flask(__name__)

    # ── Load config ────────────────────────────────────
    app.config.from_object(config[config_name])

    # ── Initialize database ────────────────────────────
    # This connects SQLAlchemy to our Flask app.
    # db was created in models.py without an app,
    # now we give it one.
    db.init_app(app)

    # ── Register blueprints ────────────────────────────
    for blueprint in all_blueprints:
        app.register_blueprint(blueprint)

    # ── Context processors ─────────────────────────────
    @app.context_processor
    def inject_globals():
        from models import Article
        return {
            'app_name':     app.config['APP_NAME'],
            'app_tagline':  app.config['APP_TAGLINE'],
            'categories':   app.config['CATEGORIES'],
            'current_year': datetime.now().year,
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


if __name__ == '__main__':
    print("""
    ╔══════════════════════════════════════╗
    ║   🛡️  CyberNews Dev Server           ║
    ║   http://0.0.0.0:5000               ║
    ╚══════════════════════════════════════╝
    """)
    app.run(host='0.0.0.0', port=5000, debug=True)
