"""
Initialize the database with schema and sample data.

Usage:
    python init_db.py
"""

from app import create_app
from app.models.paper import init_db


def initialize_database():
    """Initialize the database with schema and sample data."""
    # Create the app so the DB pool is initialized
    create_app()

    print("Starting database initialization...")
    init_db()
    print("Database initialization complete!")


if __name__ == '__main__':
    initialize_database()
