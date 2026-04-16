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

def add_paper(subject, branch, regulation, filename, semester=None, year=None):
    """Adds a new question paper record to the database."""
    conn = get_db()
    if not conn:
        raise Exception("Database connection failed")
    
    cursor = conn.cursor()
    if semester or year:
        query = ('INSERT INTO papers (subject, branch, regulation, filename, semester, year) '
                 'VALUES (%s, %s, %s, %s, %s, %s)')
        try:
            cursor.execute(query, (subject, branch, regulation, filename, semester, year))
            conn.commit()
        finally:
            cursor.close()
            conn.close()
    else:
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
    finally:
        cursor.close()
        conn.close()

# ===== NEW FUNCTIONS FOR ENHANCED FEATURES =====

def get_papers_by_filters(branch=None, regulation=None, year=None, subject_ids=None):
    """Retrieves papers based on filters."""
    conn = get_db()
    if not conn:
        return []
    
    cursor = conn.cursor(dictionary=True)
    query = 'SELECT * FROM papers WHERE 1=1'
    params = []
    
    if branch:
        query += ' AND branch = %s'
        params.append(branch)

    if regulation:
        query += ' AND regulation = %s'
        params.append(regulation)
    
    if year:
        # Accept either full year-semester format (e.g., "2-1") or year only (e.g., "2").
        if '-' in str(year):
            query += ' AND (semester = %s OR CONCAT(year, "-", semester) = %s)'
            params.extend([year, year])
        else:
            query += ' AND year = %s'
            params.append(year)
    
    if subject_ids:
        placeholders = ','.join(['%s'] * len(subject_ids))
        query += f' AND subject IN ({placeholders})'
        params.extend(subject_ids)
    
    query += ' ORDER BY upload_date DESC'
    
    try:
        cursor.execute(query, params)
        papers = cursor.fetchall()
        for paper in papers:
            if 'upload_date' in paper and paper['upload_date']:
                paper['upload_date'] = paper['upload_date'].isoformat()
        return papers
    finally:
        cursor.close()
        conn.close()

def get_years():
    """Retrieves all available years."""
    conn = get_db()
    if not conn:
        return []
    
    cursor = conn.cursor()
    try:
        cursor.execute('''
            SELECT DISTINCT CONCAT(year, '-', semester) as year_sem
            FROM years
            ORDER BY year, semester
        ''')
        return [row[0] for row in cursor.fetchall()]
    finally:
        cursor.close()
        conn.close()

def add_questions(paper_id, questions_list):
    """Adds extracted questions to database."""
    conn = get_db()
    if not conn:
        raise Exception("Database connection failed")
    
    cursor = conn.cursor()
    query = '''INSERT INTO questions 
               (paper_id, question_text, question_number, question_type) 
               VALUES (%s, %s, %s, %s)'''
    
    try:
        for idx, q in enumerate(questions_list, 1):
            cursor.execute(query, (paper_id, q.get('text'), idx, q.get('type', 'Unknown')))
        conn.commit()
    finally:
        cursor.close()
        conn.close()

def get_pattern_group(subject_id, branch_id):
    """Retrieves similar question patterns."""
    conn = get_db()
    if not conn:
        return []
    
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute('''
            SELECT * FROM question_patterns
            WHERE subject_id = %s AND branch_id = %s
            ORDER BY importance_score DESC
        ''', (subject_id, branch_id))
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

def save_learning_plan(subject_id, branch_id, year, plan_data):
    """Saves generated learning plan."""
    import json
    conn = get_db()
    if not conn:
        raise Exception("Database connection failed")
    
    cursor = conn.cursor()
    query = '''INSERT INTO learning_plans
               (subject_id, branch_id, year, analysis_result, top_questions, study_focus_areas)
               VALUES (%s, %s, %s, %s, %s, %s)'''
    
    try:
        cursor.execute(query, (
            subject_id,
            branch_id,
            year,
            plan_data.get('analysis', ''),
            json.dumps(plan_data.get('top_questions', [])),
            json.dumps(plan_data.get('focus_areas', []))
        ))
        conn.commit()
    finally:
        cursor.close()
        conn.close()

def get_subjects_dict():
    """Retrieves all subjects as dictionary."""
    conn = get_db()
    if not conn:
        return {}
    
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute('SELECT id, name FROM subjects ORDER BY name')
        return {row['name']: row['id'] for row in cursor.fetchall()}
    finally:
        cursor.close()
        conn.close()

def get_branches_dict():
    """Retrieves all branches as dictionary."""
    conn = get_db()
    if not conn:
        return {}
    
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute('SELECT id, name FROM branches ORDER BY name')
        return {row['name']: row['id'] for row in cursor.fetchall()}
    finally:
        cursor.close()
        conn.close()