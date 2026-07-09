# config.py
# ─────────────────────────────────────────────────────────
# All configuration settings for CyberNews.
# Having settings in one place makes the app easy to manage.
# Different environments (development, production) can have
# different settings.
# ─────────────────────────────────────────────────────────

import os

class Config:
    """Base configuration — settings shared by all environments."""

    # Secret key is used by Flask to sign cookies and sessions.
    # In production this MUST be a long random string kept secret.
    # os.urandom(24) generates 24 random bytes.
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'cybernews-dev-key-change-in-production'

    # Application info
    APP_NAME    = 'CyberNews'
    APP_TAGLINE = 'Security Intelligence Daily'

    # Pagination — how many articles per page
    ARTICLES_PER_PAGE = 9

    # Categories list (used in templates and routes)
    CATEGORIES = [
        'Malware',
        'Data Breaches',
        'Vulnerabilities',
        'Privacy',
        'Research',
        'Threats',
    ]

    # Trusted news sources
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
    """Development settings — extra debugging info shown."""
    DEBUG = True


class ProductionConfig(Config):
    """Production settings — no debug info shown to users."""
    DEBUG = False


# Dictionary to select config by name
config = {
    'development': DevelopmentConfig,
    'production':  ProductionConfig,
    'default':     DevelopmentConfig,
}
