"""
Application factory for Question Papers Hub.

Usage:
    from app import create_app
    app = create_app()
"""

import os
from flask import Flask

from app.config import Config
from app.extensions import init_db_pool


def create_app(config_class=Config):
    """Create and configure the Flask application.

    Args:
        config_class: Configuration class to use (default: Config).

    Returns:
        Configured Flask application instance.
    """
    app = Flask(
        __name__,
        static_folder='static',
        static_url_path='/static',
    )

    # Load configuration
    app.config.from_object(config_class)
    app.config['UPLOAD_FOLDER'] = config_class.UPLOAD_FOLDER

    # Ensure upload directory exists
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Initialize database pool
    init_db_pool(config_class)

    # Register blueprints
    _register_blueprints(app)

    return app


def _register_blueprints(app):
    """Register all route blueprints with the app."""
    from app.routes.main_routes import main_bp
    from app.routes.paper_routes import papers_bp
    from app.routes.analysis_routes import analysis_bp
    from app.routes.data_routes import data_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(papers_bp)
    app.register_blueprint(analysis_bp)
    app.register_blueprint(data_bp)
