import os
import sys

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))  

from app import create_app
from database.models import db, User, Document, CreditRequest, ScanLog, DocumentMatch
from werkzeug.security import generate_password_hash

def init_db():
    app = create_app()
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Check if admin user exists
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            # Create admin user
            admin = User(
                username='admin',
                email='admin@example.com',
                role='admin',
                password_hash=generate_password_hash('admin123')
            )
            db.session.add(admin)
            
            # Create test user
            test_user = User(
                username='testuser',
                email='test@example.com',
                role='user',
                password_hash=generate_password_hash('test123')
            )
            db.session.add(test_user)
            
            db.session.commit()
            print("Database initialized with admin and test users.")
        else:
            print("Database already initialized.")

if __name__ == '__main__':
    init_db()
