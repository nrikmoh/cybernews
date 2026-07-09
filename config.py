# config.py
import os

# Base directory of the project
BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Base configuration."""

    SECRET_KEY = os.environ.get('SECRET_KEY') or 'cybernews-dev-key-change-in-production'

    # ── Database ───────────────────────────────────────
    # SQLite database stored in a file called cybernews.db
    # in the project root directory.
    # os.path.join builds the full path correctly on any OS.
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(BASE_DIR, 'cybernews.db')

    # Disable modification tracking — saves memory
    # (We don't need this SQLAlchemy feature)
    SQLALCHEMY_TRACK_MODIFICATIONS = False

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
