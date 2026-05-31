import mysql.connector
from mysql.connector import pooling

# Global reference — initialized by init_db_pool()
db_pool = None


def init_db_pool(config):
    """Initialize the MySQL connection pool from app config.
    
    Called once during app startup via create_app().
    """
    global db_pool
    db_pool = pooling.MySQLConnectionPool(
        pool_name="question_papers_pool",
        pool_size=config.DB_POOL_SIZE,
        pool_reset_session=True,
        host=config.DB_HOST,
        user=config.DB_USER,
        password=config.DB_PASSWORD,
        database=config.DB_NAME,
        port=config.DB_PORT,
    )


def get_db():
    """Get a connection from the pool."""
    if db_pool is None:
        raise RuntimeError(
            "Database pool not initialized. Call init_db_pool() first."
        )
    try:
        return db_pool.get_connection()
    except mysql.connector.Error as e:
        print(f"Could not connect to the database: {e}")
        return None
