from flask import Flask, render_template, request, redirect, url_for, session, jsonify, g
from werkzeug.security import generate_password_hash, check_password_hash
import os
import json
import random

import database as db
import ai_engine

app = Flask(__name__)
app.secret_key = 'antigravity_ai_shopping_assistant_secret_key'

# Automatically initialize and seed the DB if it does not exist
if not os.path.exists(db.DATABASE):
    print("Database not found. Initializing and seeding...")
    from db_init import seed_db
    seed_db()

@app.teardown_appcontext
def close_connection(exception):
    db_conn = getattr(g, '_database', None)
    if db_conn is not None:
        db_conn.close()

# Helper for wrapping logged-in session state
def get_current_user():
    if 'user_id' in session:
        return db.get_user_by_id(session['user_id'])
    return None

def login_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user or not user.get('is_admin'):
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/')
def index():
    user = get_current_user()
    featured = db.get_all_products()
    for p in featured:
        p['is_wishlisted'] = db.is_in_wishlist(user['id'], p['id']) if user else False
    
    # Slice to get 4 featured products for storefront display
    featured_sliced = featured[:4]
    return render_template('index.html', user=user, featured_products=featured_sliced)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('index'))
        
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        user = db.get_user_by_username(username)
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['is_admin'] = bool(user['is_admin'])
            
            db.log_activity(user['id'], 'LOGIN', f"User {username} logged in successfully.")
            return redirect(url_for('index'))
        else:
            error = "Invalid username or password."
            db.log_activity(None, 'LOGIN_FAILED', f"Failed login attempt for username: {username}")
            
    return render_template('login.html', error=error)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('index'))
        
    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()
        
        if not username or not password:
            error = "Please fill in all fields."
        elif password != confirm_password:
            error = "Passwords do not match."
        elif len(password) < 6:
            error = "Password must be at least 6 characters."
        else:
            hashed_pw = generate_password_hash(password)
            user_id = db.create_user(username, hashed_pw)
            if user_id:
                session['user_id'] = user_id
                session['username'] = username
                session['is_admin'] = False
                
                db.log_activity(user_id, 'REGISTER', f"User {username} registered and logged in.")
                return redirect(url_for('index'))
            else:
                error = "Username already exists."
                
    return render_template('register.html', error=error)

@app.route('/logout')
def logout():
    user_id = session.get('user_id')
    username = session.get('username')
    if user_id:
        db.log_activity(user_id, 'LOGOUT', f"User {username} logged out.")
    session.clear()
    return redirect(url_for('index'))

# AI Assistant API Endpoint
@app.route('/api/chat', methods=['POST'])
def api_chat():
    data = request.get_json() or {}
    query = data.get('query', '').strip()
    elasticity_mode = data.get('elasticity_mode', 'strict')
    
    if not query:
        return jsonify({"status": "error", "message": "Query cannot be empty."}), 400
        
    user_id = session.get('user_id')
    
    # Save search to log history if user is logged in
    if user_id:
        db.add_recommendation_history(user_id, query)
        db.log_activity(user_id, 'AI_QUERY', f"AI query: '{query}' [Mode: {elasticity_mode}]")
    else:
        db.log_activity(None, 'AI_QUERY_GUEST', f"Guest AI query: '{query}' [Mode: {elasticity_mode}]")
        
    # Get all products from DB to filter/score
    all_products = db.get_all_products()
    
    # Process recommendations using the AI Engine
    result = ai_engine.get_recommendations(all_products, query, elasticity_mode)
    
    # Convert recommendations to a JSON-safe response
    response_data = {
        "status": "success",
        "parsed_query": result["parsed_query"],
        "recommendations": []
    }
    
    for item in result["recommendations"]:
        p = item["product"]
        # Include programmatically calculated spec scores
        spec_scores = ai_engine.calculate_feature_scores(p)
        response_data["recommendations"].append({
            "id": p["id"],
            "name": p["name"],
            "category": p["category"],
            "price": p["price"],
            "rating": p["rating"],
            "description": p["description"],
            "image_url": p["image_url"],
            "specs": p["specs_dict"],
            "score": item["score"],
            "explanation": item["explanation"],
            "spec_scores": spec_scores,
            "is_wishlisted": db.is_in_wishlist(user_id, p["id"]) if user_id else False
        })
        
    return jsonify(response_data)

# Traditional Product Listing & Filtering
@app.route('/products')
def products():
    category = request.args.get('category')
    max_price_str = request.args.get('max_price')
    min_rating_str = request.args.get('min_rating')
    search_query = request.args.get('search')
    
    max_price = float(max_price_str) if max_price_str else None
    min_rating = float(min_rating_str) if min_rating_str else None
    
    prod_list = db.get_all_products(
        category=category,
        max_price=max_price,
        min_rating=min_rating,
        search_query=search_query
    )
    
    user = get_current_user()
    
    # Log product search
    log_details = f"Filters - Category: {category}, MaxPrice: {max_price}, Query: {search_query}"
    db.log_activity(user['id'] if user else None, 'BROWSE_PRODUCTS', log_details)
    
    # Check wishlist status for each product
    for p in prod_list:
        p['is_wishlisted'] = db.is_in_wishlist(user['id'], p['id']) if user else False
        
    return render_template(
        'products.html',
        products=prod_list,
        user=user,
        category=category or '',
        max_price=max_price_str or '',
        min_rating=min_rating_str or '',
        search=search_query or ''
    )

# Product Detail Page
@app.route('/product/<int:product_id>')
def product_detail(product_id):
    product = db.get_product_by_id(product_id)
    if not product:
        return "Product not found", 404
        
    user = get_current_user()
    db.log_activity(user['id'] if user else None, 'VIEW_PRODUCT', f"Viewed product: {product['name']} (ID: {product_id})")
    
    is_wishlisted = db.is_in_wishlist(user['id'], product_id) if user else False
    spec_scores = ai_engine.calculate_feature_scores(product)
    
    # Suggest similar items in the same category
    category_products = db.get_all_products(category=product['category'])
    similar_products = [p for p in category_products if p['id'] != product_id][:3]
    
    return render_template(
        'product_detail.html',
        product=product,
        user=user,
        is_wishlisted=is_wishlisted,
        spec_scores=spec_scores,
        similar_products=similar_products
    )

# Comparison Dashboard
@app.route('/compare')
def compare():
    ids_str = request.args.get('ids', '')
    product_ids = []
    if ids_str:
        try:
            product_ids = [int(i) for i in ids_str.split(',') if i.strip()]
        except ValueError:
            pass
            
    products_list = []
    for pid in product_ids[:3]:  # Max 3 products compared
        p = db.get_product_by_id(pid)
        if p:
            p['spec_scores'] = ai_engine.calculate_feature_scores(p)
            products_list.append(p)
            
    user = get_current_user()
    db.log_activity(
        user['id'] if user else None,
        'COMPARE_PRODUCTS',
        f"Compared product IDs: {ids_str}"
    )
    
    ai_verdict = ai_engine.generate_comparison_verdict(products_list) if len(products_list) >= 2 else None
    
    # Also fetch all products for the picker menu
    all_products = db.get_all_products()
    
    return render_template(
        'compare.html',
        products=products_list,
        ai_verdict=ai_verdict,
        all_products=all_products,
        user=user
    )

# Wishlist Endpoints & Page
@app.route('/wishlist')
@login_required
def wishlist():
    user = get_current_user()
    items = db.get_wishlist(user['id'])
    
    # Add wishlist toggle statuses
    for item in items:
        item['is_wishlisted'] = True
        
    return render_template('wishlist.html', items=items, user=user)

@app.route('/api/wishlist/toggle', methods=['POST'])
def api_wishlist_toggle():
    user = get_current_user()
    if not user:
        return jsonify({"status": "unauthorized", "message": "Please log in to manage your wishlist."}), 401
        
    data = request.get_json() or {}
    product_id = data.get('product_id')
    if not product_id:
        return jsonify({"status": "error", "message": "Missing product ID."}), 400
        
    in_wish = db.is_in_wishlist(user['id'], product_id)
    if in_wish:
        db.remove_from_wishlist(user['id'], product_id)
        db.log_activity(user['id'], 'WISHLIST_REMOVE', f"Removed product ID {product_id} from wishlist.")
        return jsonify({"status": "success", "action": "removed", "is_wishlisted": False})
    else:
        # Check if they set an optional target price
        target_price = data.get('target_price')
        db.add_to_wishlist(user['id'], product_id, target_price)
        db.log_activity(user['id'], 'WISHLIST_ADD', f"Added product ID {product_id} to wishlist (Target: {target_price}).")
        return jsonify({"status": "success", "action": "added", "is_wishlisted": True})

@app.route('/api/wishlist/target_price', methods=['POST'])
@login_required
def api_wishlist_target_price():
    user = get_current_user()
    data = request.get_json() or {}
    product_id = data.get('product_id')
    target_price = data.get('target_price')
    
    if not product_id or target_price is None:
        return jsonify({"status": "error", "message": "Missing parameters."}), 400
        
    try:
        target_val = float(target_price) if target_price != "" else None
        db.update_wishlist_target_price(user['id'], product_id, target_val)
        db.log_activity(user['id'], 'WISHLIST_TARGET_UPDATE', f"Updated target price of product ID {product_id} to ₹{target_val}.")
        return jsonify({"status": "success", "target_price": target_val})
    except ValueError:
        return jsonify({"status": "error", "message": "Invalid target price format."}), 400

# Wishlist Price Drop Alert Simulator (Innovative Feature)
@app.route('/api/wishlist/simulate_price_drop', methods=['POST'])
@login_required
def api_wishlist_simulate_price_drop():
    user = get_current_user()
    wishlist_items = db.get_wishlist(user['id'])
    
    alerts = []
    for item in wishlist_items:
        # Only simulate price drops if target price is set
        if item['target_price'] is not None:
            actual_price = item['price']
            target = item['target_price']
            
            # Simulate a 10% - 30% discount randomly
            discount = random.uniform(0.10, 0.30)
            simulated_new_price = round(actual_price * (1 - discount), 2)
            
            # If the simulated discounted price is below the target price, trigger alert
            if simulated_new_price <= target:
                saving = round(actual_price - simulated_new_price, 2)
                alerts.append({
                    "product_id": item['id'],
                    "name": item['name'],
                    "old_price": actual_price,
                    "new_price": simulated_new_price,
                    "target_price": target,
                    "saving": saving,
                    "message": f"🚨 PRICE DROP ALERT! '{item['name']}' has dropped to ₹{simulated_new_price:,.2f} which is below your target of ₹{target:,.2f}! Save ₹{saving:,.2f}!"
                })
                
    db.log_activity(
        user['id'],
        'SIMULATE_PRICE_ALERT',
        f"Simulated price check. Triggered {len(alerts)} alerts."
    )
    return jsonify({"status": "success", "alerts": alerts})

# Search / Recommendations History
@app.route('/history')
@login_required
def history():
    user = get_current_user()
    queries = db.get_recommendation_history(user['id'])
    db.log_activity(user['id'], 'VIEW_HISTORY', "Viewed recommendations history.")
    return render_template('history.html', queries=queries, user=user)

# Admin Dashboard Area
@app.route('/admin')
@admin_required
def admin():
    stats = db.get_stats()
    products_list = db.get_all_products()
    activities = db.get_all_activities(limit=30)
    user = get_current_user()
    return render_template(
        'admin.html',
        stats=stats,
        products=products_list,
        activities=activities,
        user=user
    )

@app.route('/admin/product/add', methods=['GET', 'POST'])
@admin_required
def admin_product_add():
    user = get_current_user()
    error = None
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        category = request.form.get('category', '').strip()
        price_str = request.form.get('price', '').strip()
        rating_str = request.form.get('rating', '').strip()
        description = request.form.get('description', '').strip()
        image_url = request.form.get('image_url', '').strip()
        
        # specs parsing from individual input fields
        specs_dict = {}
        for key, val in request.form.items():
            if key.startswith('spec_key_'):
                index = key.replace('spec_key_', '')
                val_key = request.form.get(f'spec_key_{index}', '').strip()
                val_val = request.form.get(f'spec_val_{index}', '').strip()
                if val_key and val_val:
                    specs_dict[val_key] = val_val
                    
        try:
            price = float(price_str)
            rating = float(rating_str)
            
            if not name or not category or not description:
                error = "Please fill in all basic product information fields."
            else:
                db.add_product(
                    name, category, price, rating, description,
                    json.dumps(specs_dict), image_url or "https://images.unsplash.com/photo-1531403009284-440f080d1e12?w=500"
                )
                db.log_activity(user['id'], 'ADMIN_ADD_PRODUCT', f"Added product: {name}")
                return redirect(url_for('admin'))
        except ValueError:
            error = "Price and Rating must be valid numeric values."
            
    return render_template('admin_product_form.html', product=None, user=user, error=error, action="Add New")

@app.route('/admin/product/edit/<int:product_id>', methods=['GET', 'POST'])
@admin_required
def admin_product_edit(product_id):
    product = db.get_product_by_id(product_id)
    if not product:
        return "Product not found", 404
        
    user = get_current_user()
    error = None
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        category = request.form.get('category', '').strip()
        price_str = request.form.get('price', '').strip()
        rating_str = request.form.get('rating', '').strip()
        description = request.form.get('description', '').strip()
        image_url = request.form.get('image_url', '').strip()
        
        # specs parsing
        specs_dict = {}
        for key, val in request.form.items():
            if key.startswith('spec_key_'):
                index = key.replace('spec_key_', '')
                val_key = request.form.get(f'spec_key_{index}', '').strip()
                val_val = request.form.get(f'spec_val_{index}', '').strip()
                if val_key and val_val:
                    specs_dict[val_key] = val_val
                    
        try:
            price = float(price_str)
            rating = float(rating_str)
            
            if not name or not category or not description:
                error = "Please fill in all basic product information fields."
            else:
                db.update_product(
                    product_id, name, category, price, rating, description,
                    json.dumps(specs_dict), image_url or product['image_url']
                )
                db.log_activity(user['id'], 'ADMIN_EDIT_PRODUCT', f"Edited product ID {product_id}: {name}")
                return redirect(url_for('admin'))
        except ValueError:
            error = "Price and Rating must be valid numeric values."
            
    return render_template('admin_product_form.html', product=product, user=user, error=error, action="Edit")

@app.route('/admin/product/delete/<int:product_id>', methods=['POST'])
@admin_required
def admin_product_delete(product_id):
    product = db.get_product_by_id(product_id)
    name = product['name'] if product else f"ID {product_id}"
    user = get_current_user()
    
    db.delete_product(product_id)
    db.log_activity(user['id'], 'ADMIN_DELETE_PRODUCT', f"Deleted product: {name} (ID: {product_id})")
    return redirect(url_for('admin'))

if __name__ == '__main__':
    app.run(debug=True)
