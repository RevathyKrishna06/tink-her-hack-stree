from flask import Flask, render_template, request, redirect, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "stree_secret_key"


# ------------------ DATABASE INIT ------------------
def init_db():
    conn = sqlite3.connect("stree.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            age INTEGER,
            email TEXT UNIQUE,
            password TEXT
        )
    """)

    conn.commit()
    conn.close()

init_db()


# ------------------ SIGNUP ------------------
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        email = request.form['email']
        password = request.form['password']

        hashed_password = generate_password_hash(password)

        conn = sqlite3.connect("stree.db")
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO users (name, age, email, password)
                VALUES (?, ?, ?, ?)
            """, (name, age, email, hashed_password))
            conn.commit()
        except sqlite3.IntegrityError:
            conn.close()
            return "Email already registered!"

        conn.close()
        return redirect('/login')

    return render_template('signup.html')


# ------------------ LOGIN ------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = sqlite3.connect("stree.db")
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user[4], password):
            session['user'] = user[1]   # store name in session
            session['email'] = user[3]
            return redirect('/dashboard')
        else:
            return "Invalid Email or Password"

    return render_template('login.html')


# ------------------ DASHBOARD ------------------
@app.route('/dashboard')
def dashboard():
    if 'user' in session:
        return f"Welcome to STREE, {session['user']} 💖"
    return redirect('/login')


# ------------------ LOGOUT ------------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


if __name__ == "__main__":
    app.run(debug=True)