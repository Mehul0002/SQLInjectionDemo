try:
    from flask import Flask, request, render_template # type: ignore
except ImportError:
    import sys
    sys.exit("Flask is not installed. Install it with: pip install Flask")
import sqlite3

app = Flask(__name__)

# Create database and users table
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS users (username TEXT, password TEXT)')
    c.execute("INSERT OR IGNORE INTO users VALUES ('admin', 'admin123')")
    conn.commit()
    conn.close()

@app.route('/vulnerable', methods=['GET', 'POST'])
def vulnerable_login():
    message = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # VULNERABLE QUERY: Direct string concatenation allows SQL injection
        # Attackers can use inputs like username: ' OR '1'='1 to bypass authentication
        query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute(query)
        result = c.fetchone()
        conn.close()

        if result:
            message = 'Login successful! (Vulnerable version)'
        else:
            message = 'Login failed.'

    return render_template('login.html', message=message, route='vulnerable')

@app.route('/secure', methods=['GET', 'POST'])
def secure_login():
    message = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # SECURE QUERY: Use parameterized queries to prevent SQL injection
        # Placeholders (?) ensure user input is treated as literal values, not SQL code
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        result = c.fetchone()
        conn.close()

        if result:
            message = 'Login successful! (Secure version)'
        else:
            message = 'Login failed.'

    return render_template('login.html', message=message, route='secure')

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
