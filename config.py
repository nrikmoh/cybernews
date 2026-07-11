# config.py
import os
from datetime import timedelta
from dotenv import load_dotenv

# Load .env file
load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Base configuration."""

    # ── Secret Key ─────────────────────────────────────
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'change-this-in-production'

    # ── Database ────────────────────────────────────────
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get('DATABASE_URL') or
        'sqlite:///' + os.path.join(BASE_DIR, 'cybernews.db')
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }

    # ── Session Security ────────────────────────────────
    SESSION_COOKIE_HTTPONLY  = True    # JS cannot access cookie
    SESSION_COOKIE_SAMESITE  = 'Lax'  # CSRF protection
    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)

    # ── CSRF ────────────────────────────────────────────
    WTF_CSRF_ENABLED      = True
    WTF_CSRF_TIME_LIMIT   = 3600  # 1 hour

    # ── App Info ────────────────────────────────────────
    APP_NAME    = 'CyberNews'
    APP_TAGLINE = 'Security Intelligence Daily'

    ARTICLES_PER_PAGE = 20

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
    """Development — debug on, less strict."""
    DEBUG = True
    SESSION_COOKIE_SECURE = False  # HTTP ok in dev


class ProductionConfig(Config):
    """Production — debug off, maximum security."""
    DEBUG   = False
    TESTING = False

    # Only send cookie over HTTPS
    SESSION_COOKIE_SECURE = True

    # Shorter session in production
    PERMANENT_SESSION_LIFETIME = timedelta(hours=1)


config = {
    'development': DevelopmentConfig,
    'production':  ProductionConfig,
    'default':     DevelopmentConfig,
}
