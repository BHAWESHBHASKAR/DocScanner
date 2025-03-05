import sqlite3
import os
import argparse
from app import create_app, db

def get_db_path():
    """Get the database path from the app config."""
    app = create_app()
    db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
    return db_path

def migrate_database():
    """Add missing columns to existing tables."""
    db_path = get_db_path()
    print(f"Migrating database at: {db_path}")
    
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Define tables and their expected columns with types
    tables_columns = {
        'documents': {
            'content_hash': 'TEXT',
            'content_vector': 'TEXT',
            'file_type': 'TEXT',
            'file_size': 'INTEGER',
            'word_count': 'INTEGER',
            'language': 'TEXT',
            'updated_at': 'TIMESTAMP'
        },
        'users': {
            'email': 'TEXT',
            'role': 'TEXT',
            'credits': 'INTEGER',
            'total_credits_granted': 'INTEGER DEFAULT 20',
            'last_login': 'TIMESTAMP',
            'last_credit_reset': 'TIMESTAMP'
        },
        'scan_logs': {
            'similarity_score': 'REAL',
            'scan_type': 'TEXT DEFAULT "standard"',
            'scan_metadata': 'TEXT',
            'matched_documents': 'TEXT'
        },
        'credit_requests': {
            'status': 'TEXT DEFAULT "pending"',
            'approved_by': 'INTEGER',
            'approved_at': 'TIMESTAMP',
            'amount': 'INTEGER DEFAULT 0',
            'reason': 'TEXT'
        },
        'document_matches': {
            'scan_id': 'INTEGER',
            'ai_similarity_score': 'REAL',
            'traditional_similarity_score': 'REAL',
            'match_type': 'TEXT DEFAULT "low"',
            'match_details': 'TEXT',
            'updated_at': 'TIMESTAMP'
        }
    }
    
    # Foreign key constraints for each table
    foreign_keys = {
        'document_matches': [
            ('scan_id', 'scan_logs', 'id'),
            ('source_document_id', 'documents', 'id'),
            ('matched_document_id', 'documents', 'id')
        ],
        'scan_logs': [
            ('user_id', 'users', 'id'),
            ('document_id', 'documents', 'id')
        ],
        'credit_requests': [
            ('user_id', 'users', 'id'),
            ('approved_by', 'users', 'id')
        ],
        'documents': [
            ('user_id', 'users', 'id')
        ]
    }
    
    # Check each table and add missing columns
    for table, columns in tables_columns.items():
        # Check if table exists
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
        if not cursor.fetchone():
            print(f"Table {table} does not exist. Creating it...")
            
            # Create table with all columns
            create_columns = []
            for column, data_type in columns.items():
                create_columns.append(f"{column} {data_type}")
            
            # Add id column as primary key
            create_columns.insert(0, "id INTEGER PRIMARY KEY AUTOINCREMENT")
            
            # Add foreign key constraints
            if table in foreign_keys:
                for fk_column, ref_table, ref_column in foreign_keys[table]:
                    if fk_column not in columns:
                        create_columns.append(f"{fk_column} INTEGER")
                    create_columns.append(
                        f"FOREIGN KEY ({fk_column}) REFERENCES {ref_table}({ref_column})"
                    )
            
            create_sql = f"CREATE TABLE {table} (\n    " + ",\n    ".join(create_columns) + "\n)"
            cursor.execute(create_sql)
            print(f"Created table {table}")
            continue
            
        # Get existing columns
        cursor.execute(f"PRAGMA table_info({table})")
        existing_columns = [column[1] for column in cursor.fetchall()]
        
        # Add missing columns
        for column, data_type in columns.items():
            if column not in existing_columns:
                print(f"Adding {column} column to {table} table")
                cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {data_type}")
        
        # Add foreign key columns if they don't exist
        if table in foreign_keys:
            for fk_column, _, _ in foreign_keys[table]:
                if fk_column not in existing_columns and fk_column not in columns:
                    print(f"Adding foreign key column {fk_column} to {table} table")
                    cursor.execute(f"ALTER TABLE {table} ADD COLUMN {fk_column} INTEGER")
    
    # Enable foreign key support
    cursor.execute("PRAGMA foreign_keys = ON")
    
    # Commit changes and close connection
    conn.commit()
    conn.close()
    
    print("Database migration completed successfully!")

def backup_database():
    """Create a backup of the database."""
    import datetime
    import shutil
    
    db_path = get_db_path()
    backup_dir = os.path.join(os.path.dirname(db_path), 'backups')
    
    # Create backup directory if it doesn't exist
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    # Create backup filename with timestamp
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_path = os.path.join(backup_dir, f"document_scanner_{timestamp}.db")
    
    # Copy database file to backup location
    shutil.copy2(db_path, backup_path)
    
    print(f"Database backup created at: {backup_path}")

def reset_database():
    """Reset the database by dropping all tables and recreating them."""
    app = create_app()
    
    with app.app_context():
        # Drop all tables
        db.drop_all()
        print("All tables dropped.")
        
        # Create all tables
        db.create_all()
        print("All tables recreated.")
        
        # Initialize admin user
        from database.models import User
        admin = User.query.filter_by(role='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@example.com',
                role='admin',
                credits=20,
                total_credits_granted=20
            )
            admin.set_password('admin')
            db.session.add(admin)
            db.session.commit()
            print("Admin user created.")
    
    print("Database reset completed successfully!")

def main():
    parser = argparse.ArgumentParser(description='Database management utilities')
    parser.add_argument('action', choices=['migrate', 'backup', 'reset'],
                        help='Action to perform on the database')
    
    args = parser.parse_args()
    
    if args.action == 'migrate':
        migrate_database()
    elif args.action == 'backup':
        backup_database()
    elif args.action == 'reset':
        backup_database()  # Always backup before reset
        reset_database()

if __name__ == "__main__":
    main()
