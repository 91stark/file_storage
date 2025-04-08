from flask import Flask, render_template, request, redirect, session, flash
from db_config import init_mysql
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
mysql = init_mysql(app)


if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

@app.route('/')
def home():
    if 'user_id' in session:
        return redirect('/dashboard')
    return redirect('/login')

# Signup
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password'] 

        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)", 
                       (username, email, password))
        mysql.connection.commit()
        flash('Signup successful! Please log in.')
        return redirect('/login')
    return render_template('signup.html')

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']  

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE email = %s", [email])
        user = cursor.fetchone()
        if user and user['password'] == password:  
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect('/dashboard')
        flash('Invalid credentials.')
    return render_template('login.html')

# Dashboard
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')
    
    user_id = session['user_id']
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM files WHERE user_id = %s", [user_id])
    files = cursor.fetchall()
    return render_template('dashboard.html', files=files)

# Upload file
@app.route('/upload', methods=['POST'])
def upload():
    if 'user_id' not in session:
        return redirect('/login')

    file = request.files['file']
    if file:
        user_folder = os.path.join(app.config['UPLOAD_FOLDER'], str(session['user_id']))
        os.makedirs(user_folder, exist_ok=True)

        filepath = os.path.join(user_folder, file.filename)
        file.save(filepath)

        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO files (user_id, filename, filepath, upload_time) VALUES (%s, %s, %s, %s)", 
                       (session['user_id'], file.filename, filepath, datetime.now()))
        mysql.connection.commit()
        flash('File uploaded successfully!')
    return redirect('/dashboard')

# Delete file
@app.route('/delete/<int:file_id>', methods=['POST'])
def delete(file_id):
    if 'user_id' not in session:
        return redirect('/login')

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM files WHERE id = %s AND user_id = %s", (file_id, session['user_id']))
    file = cursor.fetchone()
    if file:
        os.remove(file['filepath'])
        cursor.execute("DELETE FROM files WHERE id = %s", [file_id])
        mysql.connection.commit()
        flash('File deleted successfully!')
    return redirect('/dashboard')

# Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)
