import sqlite3
from hashlib import sha256

def init_db():
    """Initialize the SQLite database and create the users table."""
    conn = sqlite3.connect('user_data.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()


def hash_password(password):
    """Hash a password using SHA-256 for secure storage."""
    return sha256(password.encode()).hexdigest()


def register_user(username, password):
    """Register a new user if the username is not already taken."""
    conn = sqlite3.connect('user_data.db')
    cursor = conn.cursor()

    try:
        hashed_password = hash_password(password)
        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
        conn.commit()
        print("User registered successfully.")
    except sqlite3.IntegrityError:
        print("Error: Username already exists.")
    finally:
        conn.close()


def login_user(username, password):
    """Verify user credentials for login."""
    conn = sqlite3.connect('user_data.db')
    cursor = conn.cursor()

    hashed_password = hash_password(password)
    cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, hashed_password))
    user = cursor.fetchone()
    conn.close()

    if user:
        print("Login successful. Welcome, {}!".format(username))
        return True
    else:
        print("Error: Invalid username or password.")
        return False


# Initialize the database
init_db()

# Menu for testing the functionality
while True:
    print("\nSelect an option:")
    print("1. Register")
    print("2. Login")
    print("3. Exit")

    choice = input("Enter your choice: ")

    if choice == '1':
        username = input("Enter a username: ")
        password = input("Enter a password: ")
        register_user(username, password)
    elif choice == '2':
        username = input("Enter your username: ")
        password = input("Enter your password: ")
        login_user(username, password)
    elif choice == '3':
        print("Goodbye!")
        break
    else:
        print("Invalid choice. Please try again.")
