import sqlite3
import os
import json
from flask import g

DATABASE = 'shopping_assistant.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def execute_db(query, args=()):
    db = get_db()
    cur = db.execute(query, args)
    db.commit()
    lastrowid = cur.lastrowid
    cur.close()
    return lastrowid

def init_db_standalone():
    """Initializes the database without flask context (for initialization scripts)"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Create Users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        is_admin INTEGER DEFAULT 0
    )
    ''')
    
    # Create Products table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        price REAL NOT NULL,
        rating REAL NOT NULL,
        description TEXT NOT NULL,
        specs TEXT NOT NULL,
        image_url TEXT NOT NULL
    )
    ''')
    
    # Create Wishlists table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS wishlists (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        target_price REAL,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE,
        UNIQUE(user_id, product_id)
    )
    ''')
    
    # Create Recommendation History table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS recommendation_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        query TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
    )
    ''')
    
    # Create User Activity table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_activity (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        action TEXT NOT NULL,
        details TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
    )
    ''')
    
    conn.commit()
    conn.close()

def init_db():
    """Initializes database within flask context"""
    init_db_standalone()

# User Operations
def create_user(username, password_hash, is_admin=0):
    try:
        return execute_db(
            'INSERT INTO users (username, password_hash, is_admin) VALUES (?, ?, ?)',
            (username, password_hash, is_admin)
        )
    except sqlite3.IntegrityError:
        return None

def get_user_by_username(username):
    row = query_db('SELECT * FROM users WHERE username = ?', (username,), one=True)
    return dict(row) if row else None

def get_user_by_id(user_id):
    row = query_db('SELECT * FROM users WHERE id = ?', (user_id,), one=True)
    return dict(row) if row else None

# Product Operations
def get_all_products(category=None, max_price=None, min_rating=None, search_query=None):
    sql = 'SELECT * FROM products WHERE 1=1'
    args = []
    
    if category:
        sql += ' AND category = ?'
        args.append(category)
    if max_price is not None:
        sql += ' AND price <= ?'
        args.append(max_price)
    if min_rating is not None:
        sql += ' AND rating >= ?'
        args.append(min_rating)
    if search_query:
        sql += ' AND (name LIKE ? OR description LIKE ? OR category LIKE ?)'
        like_query = f'%{search_query}%'
        args.extend([like_query, like_query, like_query])
        
    rows = query_db(sql, args)
    products = []
    for r in rows:
        p = dict(r)
        # Parse specs JSON
        try:
            p['specs_dict'] = json.loads(p['specs'])
        except Exception:
            p['specs_dict'] = {}
        products.append(p)
    return products

def get_product_by_id(product_id):
    row = query_db('SELECT * FROM products WHERE id = ?', (product_id,), one=True)
    if row:
        p = dict(row)
        try:
            p['specs_dict'] = json.loads(p['specs'])
        except Exception:
            p['specs_dict'] = {}
        return p
    return None

def add_product(name, category, price, rating, description, specs_json, image_url):
    return execute_db(
        'INSERT INTO products (name, category, price, rating, description, specs, image_url) VALUES (?, ?, ?, ?, ?, ?, ?)',
        (name, category, price, rating, description, specs_json, image_url)
    )

def update_product(product_id, name, category, price, rating, description, specs_json, image_url):
    execute_db(
        'UPDATE products SET name = ?, category = ?, price = ?, rating = ?, description = ?, specs = ?, image_url = ? WHERE id = ?',
        (name, category, price, rating, description, specs_json, image_url, product_id)
    )

def delete_product(product_id):
    execute_db('DELETE FROM products WHERE id = ?', (product_id,))

# Wishlist Operations
def add_to_wishlist(user_id, product_id, target_price=None):
    try:
        execute_db(
            'INSERT INTO wishlists (user_id, product_id, target_price) VALUES (?, ?, ?)',
            (user_id, product_id, target_price)
        )
        return True
    except sqlite3.IntegrityError:
        # Already exists, maybe update target_price
        if target_price is not None:
            update_wishlist_target_price(user_id, product_id, target_price)
            return True
        return False

def remove_from_wishlist(user_id, product_id):
    execute_db('DELETE FROM wishlists WHERE user_id = ? AND product_id = ?', (user_id, product_id))

def get_wishlist(user_id):
    sql = '''
    SELECT p.*, w.target_price
    FROM wishlists w
    JOIN products p ON w.product_id = p.id
    WHERE w.user_id = ?
    '''
    rows = query_db(sql, (user_id,))
    products = []
    for r in rows:
        p = dict(r)
        try:
            p['specs_dict'] = json.loads(p['specs'])
        except Exception:
            p['specs_dict'] = {}
        products.append(p)
    return products

def update_wishlist_target_price(user_id, product_id, target_price):
    execute_db(
        'UPDATE wishlists SET target_price = ? WHERE user_id = ? AND product_id = ?',
        (target_price, user_id, product_id)
    )

def is_in_wishlist(user_id, product_id):
    row = query_db('SELECT id FROM wishlists WHERE user_id = ? AND product_id = ?', (user_id, product_id), one=True)
    return row is not None

# Recommendation History
def add_recommendation_history(user_id, query):
    execute_db(
        'INSERT INTO recommendation_history (user_id, query) VALUES (?, ?)',
        (user_id, query)
    )

def get_recommendation_history(user_id):
    rows = query_db(
        'SELECT * FROM recommendation_history WHERE user_id = ? ORDER BY timestamp DESC LIMIT 20',
        (user_id,)
    )
    return [dict(r) for r in rows]

# User Activity Logging
def log_activity(user_id, action, details):
    execute_db(
        'INSERT INTO user_activity (user_id, action, details) VALUES (?, ?, ?)',
        (user_id, action, details)
    )

def get_all_activities(limit=50):
    sql = '''
    SELECT a.*, u.username
    FROM user_activity a
    LEFT JOIN users u ON a.user_id = u.id
    ORDER BY a.timestamp DESC
    LIMIT ?
    '''
    rows = query_db(sql, (limit,))
    return [dict(r) for r in rows]

# Admin Stats
def get_stats():
    users_count = query_db('SELECT COUNT(*) as cnt FROM users', one=True)['cnt']
    products_count = query_db('SELECT COUNT(*) as cnt FROM products', one=True)['cnt']
    queries_count = query_db('SELECT COUNT(*) as cnt FROM recommendation_history', one=True)['cnt']
    activities_count = query_db('SELECT COUNT(*) as cnt FROM user_activity', one=True)['cnt']
    
    # Recent queries
    recent_queries_rows = query_db(
        'SELECT q.*, u.username FROM recommendation_history q LEFT JOIN users u ON q.user_id = u.id ORDER BY q.timestamp DESC LIMIT 5'
    )
    recent_queries = [dict(r) for r in recent_queries_rows]
    
    return {
        'users': users_count,
        'products': products_count,
        'queries': queries_count,
        'activities': activities_count,
        'recent_queries': recent_queries
    }
