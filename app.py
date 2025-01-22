from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
import sqlite3
import os
import tensorflow as tf
from keras.preprocessing.image import load_img, img_to_array
from werkzeug.security import generate_password_hash

# Initialize Flask app
app = Flask(__name__,static_folder='static')
app.secret_key = 'your_secret_key'

# Define upload folder and allowed extensions
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'mp4', 'avi', 'mov'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Load ML model
MODEL_PATH = 'models\mobilenetv2_600_detector.h5'
model = tf.keras.models.load_model(MODEL_PATH)

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# SQLite database setup
def init_db():
    with sqlite3.connect('user_data.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            username TEXT UNIQUE NOT NULL,
                            password TEXT NOT NULL)''')
        conn.commit()

# Initialize the database
init_db()

# Helper function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

from werkzeug.security import check_password_hash

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    # Check if the user is 'admin' and password is 'Admin@123'
    if username == 'admin' and password == 'Admin@123':
        session['user'] = username  # Store username in session
        return redirect(url_for('landing'))  # Redirect to landing page
    
    # Check against database if the user exists
    with sqlite3.connect('user_data.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()

    if user and user[2] == password:  # user[2] is the stored password
        session['user'] = username  # Store username in session
        return redirect(url_for('landing'))  # Redirect to landing page
    else:
        flash('Invalid credentials, please try again.')
        return redirect(url_for('login'))  # Redirect to login page


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Hash the password before saving to the database
        hashed_password = generate_password_hash(password)

        with sqlite3.connect('user_data.db') as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
                conn.commit()
                flash('Registration successful. Please log in.')
                return redirect(url_for('login'))
            except sqlite3.IntegrityError:
                flash('Username already exists. Please choose a different one.')

    return render_template('index.html')

@app.route('/landing')
def landing():
    if 'user' in session:
        return render_template('landing.html')
    else:
        return redirect(url_for('login'))

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'user' not in session:
        return redirect(url_for('login'))

    file_type = request.args.get('type')

    if request.method == 'POST':
        file = request.files['file']

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            if file_type == 'image':
                result = process_image(file_path)
            else:
                result = 'Video processing is not implemented yet.'

            session['result'] = result
            return redirect(url_for('result'))
        else:
            flash('Invalid file type. Please upload an appropriate file.')

    return render_template('upload.html', type=file_type)

@app.route('/result')
def result():
    if 'result' in session:
        return render_template('result.html', result=session['result'])
    else:
        return redirect(url_for('landing'))

# Function to process the uploaded image
def process_image(image_path):
    try:
        img = load_img(image_path, target_size=(224, 224))
        img_array = img_to_array(img)
        img_array = tf.expand_dims(img_array, axis=0)  # Add batch dimension
        img_array /= 255.0  # Normalize

        predictions = model.predict(img_array)
        class_label = 'Real' if predictions[0][0] > 0.5 else 'Fake'
        return f'The uploaded image is classified as: {class_label}'
    except Exception as e:
        return f'Error in processing the image: {str(e)}'

@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('result', None)
    flash('You have been logged out.')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
