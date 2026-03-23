from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'blogsecretkey2024'

DB_PATH = os.path.join(os.path.dirname(__file__), 'blog.db')

# ─── Database Setup ───────────────────────────────────────────────────────────

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.executescript('''
        CREATE TABLE IF NOT EXISTS users (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            name     TEXT    NOT NULL,
            email    TEXT    UNIQUE NOT NULL,
            password TEXT    NOT NULL,
            created  TEXT    NOT NULL
        );
        CREATE TABLE IF NOT EXISTS articles (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            title      TEXT    NOT NULL,
            category   TEXT    NOT NULL,
            content    TEXT    NOT NULL,
            author_id  INTEGER NOT NULL,
            created    TEXT    NOT NULL,
            FOREIGN KEY (author_id) REFERENCES users(id)
        );
        CREATE TABLE IF NOT EXISTS comments (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            article_id INTEGER NOT NULL,
            author_id  INTEGER NOT NULL,
            body       TEXT    NOT NULL,
            created    TEXT    NOT NULL,
            FOREIGN KEY (article_id) REFERENCES articles(id),
            FOREIGN KEY (author_id)  REFERENCES users(id)
        );
    ''')
    conn.commit()
    conn.close()

init_db()

# ─── Helper ───────────────────────────────────────────────────────────────────

def logged_in():
    return 'user_id' in session

def now():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# ─── Routes ───────────────────────────────────────────────────────────────────

@app.route('/')
def home():
    conn = get_db()
    articles = conn.execute(
        '''SELECT a.*, u.name AS author_name
           FROM articles a JOIN users u ON a.author_id = u.id
           ORDER BY a.created DESC LIMIT 9'''
    ).fetchall()
    categories = conn.execute(
        'SELECT DISTINCT category FROM articles'
    ).fetchall()
    conn.close()
    return render_template('index.html', articles=articles, categories=categories)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name     = request.form.get('name', '').strip()
        email    = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()

        if not name or not email or not password:
            flash('All fields are required.', 'danger')
            return redirect(url_for('register'))

        conn = get_db()
        existing = conn.execute('SELECT id FROM users WHERE email=?', (email,)).fetchone()
        if existing:
            flash('Email already registered.', 'danger')
            conn.close()
            return redirect(url_for('register'))

        conn.execute(
            'INSERT INTO users (name, email, password, created) VALUES (?,?,?,?)',
            (name, email, password, now())
        )
        conn.commit()
        conn.close()
        flash('Account created! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email    = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()

        conn = get_db()
        user = conn.execute(
            'SELECT * FROM users WHERE email=? AND password=?', (email, password)
        ).fetchone()
        conn.close()

        if user:
            session['user_id']   = user['id']
            session['user_name'] = user['name']
            flash(f"Welcome back, {user['name']}!", 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid email or password.', 'danger')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

@app.route('/article/new', methods=['GET', 'POST'])
def new_article():
    if not logged_in():
        flash('Please log in to write an article.', 'warning')
        return redirect(url_for('login'))

    if request.method == 'POST':
        title    = request.form.get('title', '').strip()
        category = request.form.get('category', '').strip()
        content  = request.form.get('content', '').strip()

        if not title or not category or not content:
            flash('All fields are required.', 'danger')
            return redirect(url_for('new_article'))

        conn = get_db()
        conn.execute(
            'INSERT INTO articles (title, category, content, author_id, created) VALUES (?,?,?,?,?)',
            (title, category, content, session['user_id'], now())
        )
        conn.commit()
        conn.close()
        flash('Article published successfully!', 'success')
        return redirect(url_for('success'))

    return render_template('new_article.html')

@app.route('/success')
def success():
    return render_template('success.html')

@app.route('/article/<int:article_id>')
def view_article(article_id):
    conn = get_db()
    article = conn.execute(
        '''SELECT a.*, u.name AS author_name
           FROM articles a JOIN users u ON a.author_id = u.id
           WHERE a.id = ?''', (article_id,)
    ).fetchone()

    if not article:
        conn.close()
        flash('Article not found.', 'danger')
        return redirect(url_for('home'))

    comments = conn.execute(
        '''SELECT c.*, u.name AS commenter
           FROM comments c JOIN users u ON c.author_id = u.id
           WHERE c.article_id = ? ORDER BY c.created ASC''', (article_id,)
    ).fetchall()
    conn.close()
    return render_template('article.html', article=article, comments=comments)

@app.route('/article/<int:article_id>/comment', methods=['POST'])
def add_comment(article_id):
    if not logged_in():
        flash('Please log in to comment.', 'warning')
        return redirect(url_for('login'))

    body = request.form.get('body', '').strip()
    if not body:
        flash('Comment cannot be empty.', 'danger')
        return redirect(url_for('view_article', article_id=article_id))

    conn = get_db()
    conn.execute(
        'INSERT INTO comments (article_id, author_id, body, created) VALUES (?,?,?,?)',
        (article_id, session['user_id'], body, now())
    )
    conn.commit()
    conn.close()
    flash('Comment added!', 'success')
    return redirect(url_for('view_article', article_id=article_id))

@app.route('/article/<int:article_id>/delete', methods=['POST'])
def delete_article(article_id):
    if not logged_in():
        return redirect(url_for('login'))

    conn = get_db()
    article = conn.execute('SELECT * FROM articles WHERE id=?', (article_id,)).fetchone()
    if article and article['author_id'] == session['user_id']:
        conn.execute('DELETE FROM comments WHERE article_id=?', (article_id,))
        conn.execute('DELETE FROM articles WHERE id=?', (article_id,))
        conn.commit()
        flash('Article deleted.', 'info')
    conn.close()
    return redirect(url_for('dashboard'))

@app.route('/article/<int:article_id>/edit', methods=['GET', 'POST'])
def edit_article(article_id):
    if not logged_in():
        return redirect(url_for('login'))

    conn = get_db()
    article = conn.execute('SELECT * FROM articles WHERE id=?', (article_id,)).fetchone()

    if not article or article['author_id'] != session['user_id']:
        flash('Not authorised.', 'danger')
        conn.close()
        return redirect(url_for('home'))

    if request.method == 'POST':
        title    = request.form.get('title', '').strip()
        category = request.form.get('category', '').strip()
        content  = request.form.get('content', '').strip()
        conn.execute(
            'UPDATE articles SET title=?, category=?, content=? WHERE id=?',
            (title, category, content, article_id)
        )
        conn.commit()
        conn.close()
        flash('Article updated!', 'success')
        return redirect(url_for('view_article', article_id=article_id))

    conn.close()
    return render_template('edit_article.html', article=article)

@app.route('/dashboard')
def dashboard():
    if not logged_in():
        return redirect(url_for('login'))

    conn = get_db()
    articles = conn.execute(
        'SELECT * FROM articles WHERE author_id=? ORDER BY created DESC',
        (session['user_id'],)
    ).fetchall()
    conn.close()
    return render_template('dashboard.html', articles=articles)

@app.route('/category/<name>')
def by_category(name):
    conn = get_db()
    articles = conn.execute(
        '''SELECT a.*, u.name AS author_name
           FROM articles a JOIN users u ON a.author_id = u.id
           WHERE a.category=? ORDER BY a.created DESC''', (name,)
    ).fetchall()
    conn.close()
    return render_template('category.html', articles=articles, category=name)
@app.route('/submit', methods=['POST'])
def submit():
    # Generic form handler used by jQuery AJAX demo
    return {'status': 'ok'}

if __name__ == '__main__':
    app.run(debug=True)
