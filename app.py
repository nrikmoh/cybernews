# app.py
# ─────────────────────────────────────────────────────────
# CyberNews — Main Application Entry Point
#
# This file:
# 1. Creates the Flask application using the factory pattern
# 2. Loads configuration
# 3. Registers all blueprints (route groups)
# 4. Adds template filters and context processors
# 5. Starts the development server
# ─────────────────────────────────────────────────────────

from flask import Flask, request
from config import config
from routes import all_blueprints
import data as db
from datetime import datetime


def create_app(config_name='development'):
    """
    Application factory function.
    Creates and configures the Flask application.
    
    Using a factory function (instead of a global app variable)
    makes the app easier to test and configure differently
    for development vs production.
    """

    app = Flask(__name__)

    # ── Load configuration ─────────────────────────────
    app.config.from_object(config[config_name])

    # ── Register blueprints ────────────────────────────
    # Blueprints are groups of related routes.
    # We import and register all of them at once.
    for blueprint in all_blueprints:
        app.register_blueprint(blueprint)

    # ── Context Processors ────────────────────────────
    # These functions run before every template render
    # and inject variables that are available in ALL templates.
    # No need to pass them manually in every route.

    @app.context_processor
    def inject_globals():
        """
        Variables available in every template automatically.
        Access them directly: {{ app_name }}, {{ current_year }}
        """
        return {
            'app_name':   app.config['APP_NAME'],
            'app_tagline': app.config['APP_TAGLINE'],
            'categories': app.config['CATEGORIES'],
            'current_year': datetime.now().year,
            'all_articles': db.get_all_articles(),
        }

    # ── Template Filters ──────────────────────────────
    # Custom functions you can use inside Jinja2 templates
    # like built-in filters (| upper, | lower, etc.)

    @app.template_filter('reading_time')
    def reading_time_filter(text):
        """
        Estimates reading time based on word count.
        Average reading speed: ~200 words per minute.
        Usage in template: {{ article.body | reading_time }}
        """
        word_count   = len(text.split())
        minutes      = max(1, round(word_count / 200))
        return f"{minutes} min read"

    @app.template_filter('category_color')
    def category_color_filter(category):
        """
        Returns a CSS class suffix for a given category.
        Usage: class="badge badge-{{ article.category | category_color }}"
        """
        colors = {
            'Malware':        'malware',
            'Data Breaches':  'data-breaches',
            'Vulnerabilities':'vulnerabilities',
            'Privacy':        'privacy',
            'Research':       'research',
            'Threats':        'threats',
        }
        return colors.get(category, 'research')

    @app.template_filter('truncate_words')
    def truncate_words_filter(text, num_words=25):
        """
        Truncates text to a maximum number of words.
        Usage: {{ article.summary | truncate_words(20) }}
        """
        words = text.split()
        if len(words) <= num_words:
            return text
        return ' '.join(words[:num_words]) + '...'

    return app


# ── Create the app instance ───────────────────────────
app = create_app('development')


# ── Run the development server ────────────────────────
if __name__ == '__main__':
    print("""
    ╔══════════════════════════════════════╗
    ║   🛡️  CyberNews Dev Server           ║
    ║   http://0.0.0.0:5000               ║
    ╚══════════════════════════════════════╝
    """)
    app.run(
        host  = '0.0.0.0',
        port  = 5000,
        debug = True,
    )
