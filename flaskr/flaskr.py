import sqlite3
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash
from contextlib import closing

app = Flask(__name__)
app.config.from_object('config')
app.config.from_envvar('SETTINGS', silent=True)

def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

@app.before_request
def before_request():
    g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

@app.route('/')
def show_entries():
    cur = g.db.execute('select title, text, author from entries order by id desc')
    entries = [dict(title=row[0], text=row[1], author=row[2]) for row in cur.fetchall()]
    return render_template('show_entries.html', entries=entries)

@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    g.db.execute('insert into entries (title, text, author) values (?, ?, ?)',
        [request.form['title'], request.form['text'], session['username']])
    g.db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('show_entries'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':

        if request.form['username'] == app.config['ADMIN_USERNAME'] and \
            request.form['password'] == app.config['ADMIN_PASSWORD']:
            session['logged_in'] = True
            session['username'] = 'ADMIN'
            flash('You were logged in as Admin')
            return redirect(url_for('show_entries'))

        cur = g.db.execute('select name, password from users')
        users = {row[0]: row[1] for row in cur.fetchall()}

        if not request.form['username'] in users:
            error = 'Invalid username'
        elif users[request.form['username']] != request.form['password']:
            error = 'Invalid password'

        else:
            session['logged_in'] = True
            session['username'] = request.form['username']
            flash('You were logged in')
            return redirect(url_for('show_entries'))

    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        error=None
        g.db.execute('insert into users (name, password) values (?, ?)',
                     [request.form['username'], request.form['password']])
        g.db.commit()
        flash('New user was successfully registered')
        return redirect(url_for('show_entries'))
    return render_template('register.html')


if __name__ == '__main__':
    print(connect_db())
    app.run()
