# routes/__init__.py
# This file makes the routes/ folder a Python package.
# It also registers all blueprints in one place.

from .main   import main_bp
from .errors import errors_bp

# List of all blueprints to register
# We import this list in app.py
all_blueprints = [main_bp, errors_bp]
