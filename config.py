# config.py
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Base directory of the project
BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Base configuration."""

    SECRET_KEY = os.environ.get('SECRET_KEY') or 'cybernews-dev-key-change-in-production'

    WTF_CSRF_ENABLED = True

    # ── Database ───────────────────────────────────────
    # SQLite database stored in a file called cybernews.db
    # in the project root directory.
    # os.path.join builds the full path correctly on any OS.
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(BASE_DIR, 'cybernews.db')

    # Disable modification tracking — saves memory
    # (We don't need this SQLAlchemy feature)
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ── Session Security ───────────────────────────────
    # Cookie only sent over HTTPS (enable when you have SSL)
    # SESSION_COOKIE_SECURE = True

    # JavaScript cannot access the session cookie
    SESSION_COOKIE_HTTPONLY = True

    # Cookie only sent in first-party context
    SESSION_COOKIE_SAMESITE = 'Lax'

    # Session expires after 1 hour of inactivity
    PERMANENT_SESSION_LIFETIME = 3600

    # Don't reveal the framework in error pages
    PROPAGATE_EXCEPTIONS = False

    # App info
    APP_NAME    = 'CyberNews'
    APP_TAGLINE = 'Security Intelligence Daily'

    ARTICLES_PER_PAGE = 9

    CATEGORIES = [
        'Malware',
        'Data Breaches',
        'Vulnerabilities',
        'Privacy',
        'Research',
        'Threats',
    ]

    SOURCES = [
        'The Hacker News',
        'SecurityWeek',
        'Krebs on Security',
        'Mandiant',
        'CISA',
        'NSA',
        'FBI Cyber Division',
        'Snyk Security',
        'GitHub Security',
        'Reuters',
    ]


class DevelopmentConfig(Config):
    DEBUG = True


class ProductionConfig(Config):
    DEBUG = False


config = {
    'development': DevelopmentConfig,
    'production':  ProductionConfig,
    'default':     DevelopmentConfig,
}
