import database as db

def initialize_database():
    """Initialize the database with schema and sample data."""
    print("Starting database initialization...")
    db.init_db()
    print("Database initialization complete!")

if __name__ == '__main__':
    initialize_database()