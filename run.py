"""
Entry point for the Question Papers Hub application.

Usage:
    python run.py
"""

from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
