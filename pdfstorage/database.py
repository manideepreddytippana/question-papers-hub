# database.py
import psycopg2
import psycopg2.extras # Needed for dictionary cursor
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_db():
    """Establishes a connection to the PostgreSQL database."""
    # Render provides a single DATABASE_URL, which is the preferred way to connect
    db_url = os.getenv('DATABASE_URL')
    try:
        if db_url:
            # We are in the Render environment
            conn = psycopg2.connect(db_url)
        else:
            # We are in the local environment
            conn = psycopg2.connect(
                dbname=os.getenv('DB_NAME'),
                user=os.getenv('DB_USER'),
                password=os.getenv('DB_PASSWORD'),
                host=os.getenv('DB_HOST'),
                port=os.getenv('DB_PORT')
            )
        return conn
    except psycopg2.OperationalError as e:
        print(f"Could not connect to the database: {e}")
        return None

def init_db():
    """Initializes the database using the schema.sql file."""
    conn = get_db()
    if not conn:
        print("Aborting initialization.")
        return

    cursor = conn.cursor()
    print("Initializing database...")
    try:
        with open('schema.sql', 'r') as f:
            cursor.execute(f.read())
        conn.commit()
        print("Database initialized successfully.")
    except psycopg2.Error as e:
        print(f"Failed to initialize database: {e}")
    finally:
        cursor.close()
        conn.close()

def add_paper(subject, branch, regulation, filename):
    """Adds a new question paper record to the database."""
    conn = get_db()
    cursor = conn.cursor()
    query = ('INSERT INTO papers (subject, branch, regulation, filename) '
             'VALUES (%s, %s, %s, %s)')
    cursor.execute(query, (subject, branch, regulation, filename))
    conn.commit()
    cursor.close()
    conn.close()

def get_all_papers():
    """Retrieves all question paper records."""
    conn = get_db()
    # Use DictCursor to get results as dictionaries (like dictionary=True in mysql.connector)
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cursor.execute('SELECT * FROM papers ORDER BY id DESC')
    papers = [dict(row) for row in cursor.fetchall()] # Convert DictRow objects to standard dicts
    for paper in papers:
        if 'upload_date' in paper and paper['upload_date']:
            paper['upload_date'] = paper['upload_date'].isoformat()
    cursor.close()
    conn.close()
    return papers

def get_subjects():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT name FROM subjects ORDER BY name')
    subjects = [item[0] for item in cursor.fetchall()]
    cursor.close()
    conn.close()
    return subjects

def get_branches():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT name FROM branches ORDER BY name')
    branches = [item[0] for item in cursor.fetchall()]
    cursor.close()
    conn.close()
    return branches

def get_regulations():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT name FROM regulations ORDER BY name')
    regulations = [item[0] for item in cursor.fetchall()]
    cursor.close()
    conn.close()
    return regulations

def delete_paper(filename):
    """Deletes a paper record from the database based on its filename."""
    conn = get_db()
    if not conn:
        raise Exception("Database connection failed")

    cursor = conn.cursor()
    query = 'DELETE FROM papers WHERE filename = %s'
    try:
        cursor.execute(query, (filename,))
        conn.commit()
        if cursor.rowcount == 0:
            print(f"Warning: No record found with filename '{filename}' to delete.")
    except psycopg2.Error as err:
        print(f"Failed to delete record: {err}")
        conn.rollback()
        raise err
    finally:
        cursor.close()
        conn.close()