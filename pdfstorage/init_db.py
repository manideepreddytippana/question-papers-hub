# init_db.py
import database

def initialize():
    """
    A dedicated function to initialize the database.
    """
    print("This script will initialize the database defined in database.py.")
    print("WARNING: This will drop existing tables and delete all data.")
    
    confirm = input("Are you sure you want to continue? (y/n): ")

    if confirm.lower() == 'y':
        try:
            database.init_db()
            print("\nDatabase initialization complete.")
        except Exception as e:
            print(f"\nAn error occurred during initialization: {e}")
    else:
        print("\nInitialization cancelled.")

if __name__ == '__main__':
    initialize()