"""
Machine Uptime Issues Management System (MUIMS)
Flask application factory and configuration
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

# Initialize extensions
db = SQLAlchemy()

def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///muims.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions with app
    db.init_app(app)
    
    # Add template filters
    @app.template_filter('nl2br')
    def nl2br_filter(text):
        """Convert newlines to HTML line breaks"""
        if text:
            return text.replace('\n', '<br>')
        return text
    
    @app.template_filter("datetime")
    def _format_datetime(value, fmt="%Y-%m-%d %H:%M"):
        from datetime import datetime
        if not value:
            return ""
        if isinstance(value, str):
            return value
        return value.strftime(fmt)
    
    @app.template_filter("sev_badge")
    def sev_badge(severity: str):
        """Return Bootstrap badge classes for a severity string."""
        if not severity:
            return "bg-secondary"
        s = severity.strip().lower()
        return {
            "low": "bg-info text-dark",
            "medium": "bg-warning text-dark",
            "high": "bg-danger",
            "critical": "bg-danger",  # or customize below with CSS if you want a distinct color
        }.get(s, "bg-secondary")

    @app.template_filter("status_badge")
    def status_badge(status: str):
        """Return Bootstrap badge classes for a status string."""
        if not status:
            return "bg-secondary"
        s = status.strip().lower()
        return {
            "open": "bg-primary",
            "in progress": "bg-secondary",
            "resolved": "bg-success",
            "closed": "bg-dark",
        }.get(s, "bg-secondary")
    
    # Add human_duration filter
    def _human_duration(value):
        try:
            return value.human_duration() if hasattr(value, "human_duration") else "N/A"
        except Exception:
            return "N/A"
    
    app.jinja_env.filters["human_duration"] = _human_duration
    
    # Register blueprints
    from app.routes import main
    app.register_blueprint(main)
    
    # Register CLI commands
    from app.cli import register_cli
    register_cli(app)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app
