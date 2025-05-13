import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
from mysql.connector import Error
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Base directory for dynamic path resolution
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Database connection
db_config = {
    'host': '127.0.0.1',  # Use '127.0.0.1' instead of 'localhost' to avoid socket issues
    'user': 'root',       # Ensure this matches your MySQL username
    'password': 'MYsqlpass@123',  # Ensure this matches your MySQL password
    'database': 'peerlink_db',
    'port': 3306          # Ensure this matches the MySQL server port
}

def get_db_connection():
    try:
        print(f"Connecting to MySQL with config: {db_config}")
        connection = mysql.connector.connect(**db_config)
        if connection.is_connected():
            print("Successfully connected to the database")
        return connection
    except mysql.connector.Error as e:
        print(f"Error connecting to MySQL: {e}")
        flash(f"Database connection failed: {e}", "error")
        return None

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('auth'))
    connection = get_db_connection()
    if not connection:
        return "Database connection failed. Please try again later.", 500
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM events ORDER BY date ASC LIMIT 5")
    events = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template('dashboard.html', events=events)

@app.route('/auth', methods=['GET', 'POST'])
def auth():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        connection = get_db_connection()
        if not connection:
            return "Database connection failed. Please try again later.", 500
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute("SELECT id, username, password FROM student_login WHERE username=%s", (username,))
            user = cursor.fetchone()
        except mysql.connector.Error as e:
            print(f"Error fetching user: {e}")
            flash("An error occurred while fetching user data.", "error")
            return redirect(url_for('auth'))
        finally:
            cursor.close()
            connection.close()
        if user and user['password'] == password:
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('index'))
        flash("Invalid credentials. Please try again.", "error")
        return redirect(url_for('auth'))
    return render_template('auth.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        bio = request.form['bio']
        mobile = request.form['mobile']
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']  # Store as plain text (NOT RECOMMENDED)

        connection = get_db_connection()
        if not connection:
            return "Database connection failed. Please try again later.", 500
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT * FROM student_login WHERE username=%s OR email=%s", (username, email))
            existing_user = cursor.fetchone()
            if existing_user:
                flash("Username or email already exists.", "error")
                return redirect(url_for('signup'))
            cursor.execute("""
                INSERT INTO student_login (name, bio, mobile, username, password, email)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (name, bio, mobile, username, password, email))
            connection.commit()
        except mysql.connector.Error as e:
            print(f"Error during signup: {e}")
            flash("An error occurred during signup. Please try again.", "error")
        finally:
            cursor.close()
            connection.close()
        flash("Signup successful. Please log in.", "success")
        return redirect(url_for('auth'))
    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth'))

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('auth'))
    connection = get_db_connection()
    if not connection:
        return "Database connection failed. Please try again later.", 500
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT username FROM student_login WHERE id=%s", (session['user_id'],))
    user = cursor.fetchone()
    
    # Handle the absence of the user_bio table gracefully
    try:
        cursor.execute("SELECT bio FROM user_bio WHERE user_id=%s", (session['user_id'],))
        bio = cursor.fetchone()
        user['bio'] = bio['bio'] if bio else None
    except mysql.connector.Error as e:
        print(f"Error fetching bio: {e}")
        user['bio'] = None

    cursor.execute("SELECT * FROM circles WHERE id IN (SELECT circle_id FROM user_circle WHERE user_id=%s)", (session['user_id'],))
    circles = cursor.fetchall()
    cursor.execute("SELECT * FROM events WHERE id IN (SELECT event_id FROM user_event WHERE user_id=%s)", (session['user_id'],))
    events = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template('profile.html', user=user, circles=circles, events=events)

@app.route('/update_profile', methods=['POST'])
def update_profile():
    if 'user_id' not in session:
        return redirect(url_for('auth'))
    
    # Safely get form data
    bio = request.form.get('bio', '').strip()

    connection = get_db_connection()
    if not connection:
        return "Database connection failed. Please try again later.", 500
    cursor = connection.cursor()
    try:
        # Update the bio in the user_bio table
        cursor.execute("""
            INSERT INTO user_bio (user_id, bio)
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE bio=%s
        """, (session['user_id'], bio, bio))
        connection.commit()
    except mysql.connector.Error as e:
        print(f"Error updating bio: {e}")
    finally:
        cursor.close()
        connection.close()

    return redirect(url_for('profile'))

@app.route('/delete_bio', methods=['POST'])
def delete_bio():
    if 'user_id' not in session:
        return redirect(url_for('auth'))
    
    connection = get_db_connection()
    if not connection:
        return "Database connection failed. Please try again later.", 500
    cursor = connection.cursor()
    try:
        # Delete the bio from the user_bio table
        cursor.execute("DELETE FROM user_bio WHERE user_id=%s", (session['user_id'],))
        connection.commit()
    except mysql.connector.Error as e:
        print(f"Error deleting bio: {e}")
    finally:
        cursor.close()
        connection.close()

    return redirect(url_for('profile'))

@app.route('/update_bio', methods=['POST'])
def update_bio():
    if 'user_id' not in session:
        return redirect(url_for('auth'))
    
    bio = request.form['bio']
    connection = get_db_connection()
    if not connection:
        return "Database connection failed. Please try again later.", 500
    cursor = connection.cursor()
    try:
        # Update the bio in the user_bio table
        cursor.execute("""
            INSERT INTO user_bio (user_id, bio)
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE bio=%s
        """, (session['user_id'], bio, bio))
        connection.commit()
    except mysql.connector.Error as e:
        print(f"Error updating bio: {e}")
    finally:
        cursor.close()
        connection.close()

    return redirect(url_for('profile'))

@app.route('/events', methods=['GET', 'POST'])
def events():
    query = request.args.get('query', '')
    connection = get_db_connection()
    if not connection:
        return "Database connection failed. Please try again later.", 500
    cursor = connection.cursor(dictionary=True)
    if query:
        cursor.execute("SELECT * FROM events WHERE title LIKE %s OR location LIKE %s", (f"%{query}%", f"%{query}%"))
    else:
        cursor.execute("SELECT * FROM events")
    events = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template('events.html', events=events)

@app.route('/add_event', methods=['POST'])
def add_event():
    if 'user_id' not in session:
        return redirect(url_for('auth'))
    
    title = request.form['title']
    date = request.form['date']
    location = request.form['location']
    description = request.form.get('description', '')

    connection = get_db_connection()
    if not connection:
        return "Database connection failed. Please try again later.", 500
    cursor = connection.cursor()
    try:
        cursor.execute("""
            INSERT INTO events (title, date, location, description)
            VALUES (%s, %s, %s, %s)
        """, (title, date, location, description))
        connection.commit()
        flash("Event added successfully.", "success")
    except mysql.connector.Error as e:
        print(f"Error adding event: {e}")
        flash("Failed to add the event. Please try again.", "error")
    finally:
        cursor.close()
        connection.close()

    return redirect(url_for('events'))

@app.route('/update_event/<int:event_id>', methods=['POST'])
def update_event(event_id):
    if 'user_id' not in session:
        return redirect(url_for('auth'))
    
    title = request.form['title']
    date = request.form['date']
    location = request.form['location']
    description = request.form.get('description', '')

    connection = get_db_connection()
    if not connection:
        return "Database connection failed. Please try again later.", 500
    cursor = connection.cursor()
    try:
        cursor.execute("""
            UPDATE events
            SET title=%s, date=%s, location=%s, description=%s
            WHERE id=%s
        """, (title, date, location, description, event_id))
        connection.commit()
    except mysql.connector.Error as e:
        print(f"Error updating event: {e}")
    finally:
        cursor.close()
        connection.close()

    return redirect(url_for('events'))

@app.route('/delete_event', methods=['POST'])
def delete_event():
    if 'user_id' not in session:
        return redirect(url_for('auth'))
    
    event_id = request.form.get('event_id')
    if not event_id:
        flash("Event ID is missing. Please try again.", "error")
        return redirect(url_for('events'))
    
    connection = get_db_connection()
    if not connection:
        return "Database connection failed. Please try again later.", 500
    cursor = connection.cursor()
    try:
        cursor.execute("DELETE FROM events WHERE id=%s", (event_id,))
        connection.commit()
        flash("Event deleted successfully.", "success")
    except mysql.connector.Error as e:
        print(f"Error deleting event: {e}")
        flash("Failed to delete the event. Please try again.", "error")
    finally:
        cursor.close()
        connection.close()

    return redirect(url_for('events'))

@app.route('/circles', methods=['GET', 'POST'])
def circles():
    connection = get_db_connection()
    if not connection:
        return "Database connection failed. Please try again later.", 500
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM circles")
    circles = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template('circles.html', circles=circles)

@app.route('/social_feed', methods=['GET', 'POST'])
def social_feed():
    connection = get_db_connection()
    if not connection:
        return "Database connection failed. Please try again later.", 500
    cursor = connection.cursor(dictionary=True)
    if request.method == 'POST':
        content = request.form['content']
        badge = request.form['badge']
        image = request.files['image']
        image_url = None
        if image:
            upload_folder = os.path.join(BASE_DIR, 'static', 'uploads')
            os.makedirs(upload_folder, exist_ok=True)
            image_path = os.path.join(upload_folder, image.filename)
            image.save(image_path)
            image_url = f"/static/uploads/{image.filename}"
        cursor.execute("INSERT INTO posts (content, badge, image_url, user_id) VALUES (%s, %s, %s, %s)",
                       (content, badge, image_url, session['user_id']))
        connection.commit()
    cursor.execute("SELECT * FROM posts ORDER BY timestamp DESC")
    posts = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template('social_feed.html', posts=posts)

@app.route('/xp_dashboard')
def xp_dashboard():
    if 'user_id' not in session:
        return redirect(url_for('auth'))
    connection = get_db_connection()
    if not connection:
        return "Database connection failed. Please try again later.", 500
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM user_xp WHERE user_id=%s", (session['user_id'],))
    user_xp = cursor.fetchone()
    cursor.execute("SELECT * FROM milestones WHERE user_id=%s", (session['user_id'],))
    milestones = cursor.fetchall()
    cursor.execute("SELECT * FROM rewards")
    rewards = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template('xp_dashboard.html', user=user_xp, milestones=milestones, rewards=rewards)

@app.route('/rsvp/<int:event_id>', methods=['POST'])
def rsvp_event(event_id):
    if 'user_id' not in session:
        return redirect(url_for('auth'))
    connection = get_db_connection()
    if not connection:
        return "Database connection failed. Please try again later.", 500
    cursor = connection.cursor()
    cursor.execute("INSERT INTO user_event (user_id, event_id) VALUES (%s, %s)", (session['user_id'], event_id))
    connection.commit()
    cursor.close()
    connection.close()
    return redirect(url_for('events'))

@app.route('/init_db')
def init_db():
    try:
        # Connect to MySQL server without specifying a database
        connection = mysql.connector.connect(
            host=db_config['host'],
            user=db_config['user'],
            password=db_config['password']
        )
        cursor = connection.cursor()

        # Drop the database if it exists
        cursor.execute("DROP DATABASE IF EXISTS peerlink_db")
        print("Dropped existing database (if any).")

        # Read and execute the setup.sql script
        setup_file_path = os.path.join(BASE_DIR, 'setup.sql')
        if not os.path.exists(setup_file_path):
            return "Setup file not found. Please ensure 'setup.sql' exists in the project directory.", 500

        with open(setup_file_path, 'r') as f:
            sql_script = f.read()
        for statement in sql_script.split(';'):
            if statement.strip():
                cursor.execute(statement)
        connection.commit()
        print("Database initialized successfully!")
        cursor.close()
        connection.close()
        return "Database initialized successfully!"
    except mysql.connector.Error as e:
        print(f"Error initializing database: {e}")
        return f"Error initializing database: {e}", 500

@app.route('/setup')
def setup():
    try:
        # Connect to MySQL server without specifying a database
        connection = mysql.connector.connect(
            host=db_config['host'],
            user=db_config['user'],
            password=db_config['password']
        )
        cursor = connection.cursor()

        # Read and execute the setup.sql script
        setup_file_path = os.path.join(BASE_DIR, 'setup.sql')
        if not os.path.exists(setup_file_path):
            return "Setup file not found. Please ensure 'setup.sql' exists in the project directory.", 500

        with open(setup_file_path, 'r') as f:
            sql_script = f.read()
        for statement in sql_script.split(';'):
            if statement.strip():
                cursor.execute(statement)
        connection.commit()
        print("Database setup completed successfully!")
        cursor.close()
        connection.close()
        return "Database setup completed successfully!"
    except mysql.connector.Error as e:
        print(f"Error during database setup: {e}")
        return f"Error during database setup: {e}", 500

if __name__ == '__main__':
    app.run(debug=True)