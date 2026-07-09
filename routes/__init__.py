# routes/__init__.py
from .main   import main_bp
from .errors import errors_bp
from .admin  import admin_bp

all_blueprints = [main_bp, errors_bp, admin_bp]
