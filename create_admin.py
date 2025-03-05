from app import create_app
from database.models import db, User

def create_admin_user():
    app = create_app()
    with app.app_context():
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(username='admin', email='admin@example.com', role='admin')
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print('Admin user created successfully.')
        else:
            print('Admin user already exists.')

if __name__ == '__main__':
    create_admin_user()
