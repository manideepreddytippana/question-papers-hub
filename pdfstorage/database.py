import mysql.connector
from mysql.connector import pooling
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Create a connection pool
db_pool = pooling.MySQLConnectionPool(
    pool_name="question_papers_pool",
    pool_size=5,  # Number of connections in the pool
    pool_reset_session=True,
    host=os.getenv('DB_HOST'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD'),
    database=os.getenv('DB_NAME'),
    port=int(os.getenv('DB_PORT', 3306))
)

def get_db():
    """Gets a connection from the connection pool."""
    try:
        conn = db_pool.get_connection()
        return conn
    except mysql.connector.Error as e:
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
            schema_content = f.read()
            # Split by semicolon to execute multiple statements
            statements = schema_content.split(';')
            for statement in statements:
                statement = statement.strip()
                if statement:
                    cursor.execute(statement)
        conn.commit()
        print("Database initialized successfully.")
    except mysql.connector.Error as e:
        print(f"Failed to initialize database: {e}")
    finally:
        cursor.close()
        conn.close()

def add_paper(subject, branch, regulation, filename):
    """Adds a new question paper record to the database."""
    conn = get_db()
    if not conn:
        raise Exception("Database connection failed")
    
    cursor = conn.cursor()
    query = ('INSERT INTO papers (subject, branch, regulation, filename) '
             'VALUES (%s, %s, %s, %s)')
    try:
        cursor.execute(query, (subject, branch, regulation, filename))
        conn.commit()
    finally:
        cursor.close()
        conn.close()

def get_all_papers():
    """Retrieves all question paper records."""
    conn = get_db()
    if not conn:
        return []
    
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute('SELECT * FROM papers ORDER BY id DESC')
        papers = cursor.fetchall()
        # Convert datetime objects to ISO format strings
        for paper in papers:
            if 'upload_date' in paper and paper['upload_date']:
                paper['upload_date'] = paper['upload_date'].isoformat()
        return papers
    finally:
        cursor.close()
        conn.close()

def get_subjects():
    """Retrieves all subjects."""
    conn = get_db()
    if not conn:
        return []
    
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT name FROM subjects ORDER BY name')
        subjects = [item[0] for item in cursor.fetchall()]
        return subjects
    finally:
        cursor.close()
        conn.close()

def get_branches():
    """Retrieves all branches."""
    conn = get_db()
    if not conn:
        return []
    
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT name FROM branches ORDER BY name')
        branches = [item[0] for item in cursor.fetchall()]
        return branches
    finally:
        cursor.close()
        conn.close()

def get_regulations():
    """Retrieves all regulations."""
    conn = get_db()
    if not conn:
        return []
    
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT name FROM regulations ORDER BY name')
        regulations = [item[0] for item in cursor.fetchall()]
        return regulations
    finally:
        cursor.close()
        conn.close()

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
    except mysql.connector.Error as err:
        print(f"Failed to delete record: {err}")
        conn.rollback()
        raise err
    finally:
        cursor.close()
        conn.close()