import sqlite3

# Path to your SQLite database
db_path = 'database.db'

# SQL command to create the league_table
create_table_sql = '''
CREATE TABLE IF NOT EXISTS league_table (
    team_id INTEGER PRIMARY KEY,
    matches_played INTEGER DEFAULT 0,
    wins INTEGER DEFAULT 0,
    draws INTEGER DEFAULT 0,
    losses INTEGER DEFAULT 0,
    goals_scored INTEGER DEFAULT 0,
    goals_conceded INTEGER DEFAULT 0,
    goal_difference INTEGER DEFAULT 0,
    points INTEGER DEFAULT 0,
    FOREIGN KEY (team_id) REFERENCES teams (id)
);
'''

def create_league_table():
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Execute the SQL command to create the table
        cursor.execute(create_table_sql)
        print("Table 'league_table' created successfully.")
    except sqlite3.OperationalError as e:
        print(f"An error occurred: {e}")
    finally:
        # Commit changes and close the connection
        conn.commit()
        conn.close()

if __name__ == '__main__':
    create_league_table()
