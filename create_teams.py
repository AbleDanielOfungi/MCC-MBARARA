import sqlite3

# Path to your SQLite database
db_path = 'your_database.db'

# SQL command to create the teams table
create_table_sql = '''
CREATE TABLE IF NOT EXISTS teams (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    badge_url TEXT
);
'''

def create_teams_table():
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Execute the SQL command to create the table
        cursor.execute(create_table_sql)
        print("Table 'teams' created successfully.")
    except sqlite3.OperationalError as e:
        print(f"An error occurred: {e}")
    finally:
        # Commit changes and close the connection
        conn.commit()
        conn.close()

if __name__ == '__main__':
    create_teams_table()
