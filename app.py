"""
Document Scanner Application - Main Application Module

This is the main entry point for the Document Scanner application. It initializes the Flask
application, sets up database connections, configures authentication, and registers all
API endpoints.

The application provides document scanning and matching functionality with a credit-based
system. Users get 20 free scans per day and can request additional credits from admins.

Author: Bhawesh Bhaskar
Date: March 2025
"""

import os
import json
import datetime
from flask import Flask, request, jsonify, render_template, redirect, url_for, flash, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler
import atexit

# Import application components
from database.models import db, User, Document, CreditRequest, ScanLog, DocumentMatch
from backend.api.auth import auth_bp
from backend.api.user import user_bp
from backend.api.document import document_bp
from backend.api.admin import admin_bp
from backend.api.credit import credit_bp

# Load environment variables from .env file
load_dotenv()

def create_app(test_config=None):
    """
    Create and configure the Flask application instance.
    
    Args:
        test_config (dict, optional): Test configuration to override default settings
    
    Returns:
        Flask: Configured Flask application instance
    """
    # Initialize Flask app
    app = Flask(__name__, instance_relative_config=True)
    
    # Load configuration
    from config import Config
    app.config.from_object(Config)
    
    # Initialize CSRF protection
    csrf = CSRFProtect()
    csrf.init_app(app)
    
    # Set upload size limit (16MB) to prevent server overload
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
    
    # Configure template and static file locations
    app.template_folder = os.path.join(app.root_path, 'frontend/templates')
    app.static_folder = os.path.join(app.root_path, 'frontend/static')
    
    # Create upload directory if it doesn't exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Initialize database and migration support
    db.init_app(app)
    from flask_migrate import Migrate
    migrate = Migrate(app, db)
    
    # Set up user authentication
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'  # Redirect unauthorized users to login page
    login_manager.init_app(app)
    
    @login_manager.user_loader
    def load_user(user_id):
        """Load user by ID for Flask-Login."""
        return User.query.get(int(user_id))
    
    # Register API blueprints
    app.register_blueprint(auth_bp)      # Authentication routes
    app.register_blueprint(user_bp)      # User profile and settings
    app.register_blueprint(document_bp)  # Document management
    app.register_blueprint(admin_bp)     # Admin dashboard
    app.register_blueprint(credit_bp)    # Credit system
    
    # Define main route
    @app.route('/')
    def index():
        """Render the application's home page."""
        return render_template('index.html')
    
    # Set up automated credit reset system
    with app.app_context():
        scheduler = BackgroundScheduler()
        
        def reset_daily_credits():
            """
            Reset user credits to 20 at midnight.
            Only resets if the user hasn't had a reset in the last 24 hours.
            """
            with app.app_context():
                users = User.query.all()
                now = datetime.datetime.now()
                
                for user in users:
                    # Check if it's been 24 hours since last reset
                    if user.last_credit_reset and (now - user.last_credit_reset).days >= 1:
                        user.credits = 20  # Reset to daily free limit
                        user.last_credit_reset = now
                        print(f"Reset credits for user {user.username} at {now}")
                
                db.session.commit()
                print(f"Daily credit reset completed at {now}")
        
        # Run credit reset job every hour to handle different timezones
        scheduler.add_job(reset_daily_credits, 'interval', hours=1)
        scheduler.start()
        
        # Ensure scheduler is properly shut down when app exits
        atexit.register(lambda: scheduler.shutdown())
    
    return app

# Run the application in development mode
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5003)
