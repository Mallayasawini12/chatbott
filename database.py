import sqlite3
import os
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

if os.environ.get('VERCEL'):
    DB_PATH = '/tmp/career_chatbot.db'
else:
    DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'career_chatbot.db')


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database and create tables if they do not exist."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create chat_history table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            sender TEXT CHECK(sender IN ('user', 'bot')) NOT NULL,
            message TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')
    
    # Create quiz_results table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS quiz_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            recommended_career TEXT NOT NULL,
            scores TEXT NOT NULL, -- JSON string representing score breakdown
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    ''')
    
    conn.commit()
    conn.close()

def register_user(username, email, password):
    """Registers a new user with a hashed password. Returns user ID or None if username/email exists."""
    password_hash = generate_password_hash(password)
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            'INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)',
            (username, email, password_hash)
        )
        conn.commit()
        user_id = cursor.lastrowid
        return user_id
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()

def check_user_credentials(username, password):
    """Verifies user login credentials. Returns the user row dict if valid, else None."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = cursor.fetchone()
    conn.close()
    
    if user and check_password_hash(user['password_hash'], password):
        return dict(user)
    return None

def get_user_by_id(user_id):
    """Fetches user details by user ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, username, email, created_at FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None

def save_chat_message(user_id, sender, message):
    """Saves a message (from user or bot) to the chat history."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO chat_history (user_id, sender, message) VALUES (?, ?, ?)',
        (user_id, sender, message)
    )
    conn.commit()
    conn.close()

def get_chat_history(user_id):
    """Gets chronological chat history for a user."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'SELECT sender, message, timestamp FROM chat_history WHERE user_id = ? ORDER BY timestamp ASC',
        (user_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def clear_chat_history(user_id):
    """Clears chat history for a user."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM chat_history WHERE user_id = ?', (user_id,))
    conn.commit()
    conn.close()

def save_quiz_result(user_id, recommended_career, scores_json):
    """Saves a user's skill assessment quiz result."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO quiz_results (user_id, recommended_career, scores) VALUES (?, ?, ?)',
        (user_id, recommended_career, scores_json)
    )
    conn.commit()
    result_id = cursor.lastrowid
    conn.close()
    return result_id

def get_latest_quiz_result(user_id):
    """Gets the latest quiz result for a user."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'SELECT id, recommended_career, scores, timestamp FROM quiz_results WHERE user_id = ? ORDER BY timestamp DESC LIMIT 1',
        (user_id,)
    )
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def get_quiz_result_by_id(result_id):
    """Gets a specific quiz result by database ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        'SELECT qr.id, qr.user_id, u.username, qr.recommended_career, qr.scores, qr.timestamp '
        'FROM quiz_results qr JOIN users u ON qr.user_id = u.id WHERE qr.id = ?',
        (result_id,)
    )
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

if __name__ == '__main__':
    # Initialize the database when run directly
    init_db()
    print("Database initialized successfully at:", DB_PATH)
