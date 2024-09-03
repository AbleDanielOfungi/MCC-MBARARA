from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# Database connection function
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# add team route   
import os
from flask import Flask, request, redirect, url_for, render_template

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'  # Directory where uploaded files will be saved
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # Limit file size to 5MB

def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/add_team', methods=('GET', 'POST'))
def add_team():
    if request.method == 'POST':
        team_name = request.form['team_name'].strip()
        badge = request.files['badge']

        if badge and allowed_file(badge.filename):
            filename = f"{team_name.replace(' ', '_').lower()}.{badge.filename.rsplit('.', 1)[1].lower()}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            badge.save(filepath)
            badge_url = url_for('static', filename=f'uploads/{filename}')
            
            conn = get_db_connection()
            conn.execute('INSERT INTO teams (name, badge_url) VALUES (?, ?)', (team_name.title(), badge_url))
            conn.commit()
            conn.close()

            return redirect(url_for('index'))
        else:
            return "Invalid file type. Please upload an image file."

    return render_template('add_team.html')


#index route
@app.route('/')
def index():
    conn = get_db_connection()
    league_table = conn.execute('''
        SELECT t.name AS team_name, lt.matches_played, lt.wins, lt.draws, lt.losses, 
               lt.goals_scored, lt.goals_conceded, lt.goal_difference, lt.points,
               RANK() OVER (ORDER BY lt.points DESC, lt.goal_difference DESC) AS position
        FROM league_table lt
        JOIN teams t ON lt.team_id = t.id
        ORDER BY position ASC
    ''').fetchall()
    conn.close()
    return render_template('index.html', league_table=league_table)

# add result 
@app.route('/add_result', methods=('GET', 'POST'))
def add_result():
    if request.method == 'POST':
        team1 = request.form['team1'].strip()
        team2 = request.form['team2'].strip()
        score1 = int(request.form['score1'])
        score2 = int(request.form['score2'])

        conn = get_db_connection()

        # Check if teams exist in the teams table (case-insensitive)
        team1_id = conn.execute('SELECT id FROM teams WHERE LOWER(name) = LOWER(?)', (team1,)).fetchone()
        team2_id = conn.execute('SELECT id FROM teams WHERE LOWER(name) = LOWER(?)', (team2,)).fetchone()

        if not team1_id:
            conn.execute('INSERT INTO teams (name) VALUES (?)', (team1.capitalize(),))
            team1_id = conn.execute('SELECT id FROM teams WHERE LOWER(name) = LOWER(?)', (team1,)).fetchone()

        if not team2_id:
            conn.execute('INSERT INTO teams (name) VALUES (?)', (team2.capitalize(),))
            team2_id = conn.execute('SELECT id FROM teams WHERE LOWER(name) = LOWER(?)', (team2,)).fetchone()

        # Prevent duplicate registration of teams
        if team1_id['id'] == team2_id['id']:
            return render_template('add_result.html', error="A team cannot play against itself.")

        # Insert the match result
        conn.execute('INSERT INTO matches (team1_id, team2_id, score1, score2) VALUES (?, ?, ?, ?)',
                     (team1_id['id'], team2_id['id'], score1, score2))

        # Update the league table for both teams
        update_league_table(conn, team1_id['id'], score1, score2)
        update_league_table(conn, team2_id['id'], score2, score1)

        conn.commit()
        conn.close()

        return redirect(url_for('index'))

    return render_template('add_result.html')

#update league table
def update_league_table(conn, team_id, goals_scored, goals_conceded):
    team_stats = conn.execute('SELECT * FROM league_table WHERE team_id = ?', (team_id,)).fetchone()

    if team_stats:
        # Update the existing record
        matches_played = team_stats['matches_played'] + 1
        goals_scored_total = team_stats['goals_scored'] + goals_scored
        goals_conceded_total = team_stats['goals_conceded'] + goals_conceded
        goal_difference = goals_scored_total - goals_conceded_total
        points = team_stats['points']
        wins = team_stats['wins']
        draws = team_stats['draws']
        losses = team_stats['losses']

        # Update points and win/draw/loss count based on the result
        if goals_scored > goals_conceded:
            points += 3
            wins += 1
        elif goals_scored == goals_conceded:
            points += 1
            draws += 1
        else:
            losses += 1

        conn.execute('''
            UPDATE league_table
            SET matches_played = ?, points = ?, goal_difference = ?, goals_scored = ?, 
                goals_conceded = ?, wins = ?, draws = ?, losses = ?
            WHERE team_id = ?
        ''', (matches_played, points, goal_difference, goals_scored_total, goals_conceded_total, wins, draws, losses, team_id))

    else:
        # Insert a new record
        matches_played = 1
        goal_difference = goals_scored - goals_conceded
        goals_scored_total = goals_scored
        goals_conceded_total = goals_conceded
        wins = 0
        draws = 0
        losses = 0
        points = 0

        if goals_scored > goals_conceded:
            points = 3
            wins = 1
        elif goals_scored == goals_conceded:
            points = 1
            draws = 1
        else:
            losses = 1

        conn.execute('''
            INSERT INTO league_table (team_id, points, goal_difference, goals_scored, 
                                      goals_conceded, matches_played, wins, draws, losses)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (team_id, points, goal_difference, goals_scored_total, goals_conceded_total, matches_played, wins, draws, losses))




if __name__ == '__main__':
    app.run(debug=True)
