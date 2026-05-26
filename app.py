import os
import re
from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
import pymysql
import pymysql.cursors
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'super_secret_key_product_management_system'

# Database configuration (standard XAMPP credentials)
DB_HOST = 'localhost'
DB_USER = 'root'
DB_PASSWORD = ''
DB_NAME = 'product_system'

def get_db_connection():
    """Establishes and returns a connection to the MySQL database."""
    return pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        cursorclass=pymysql.cursors.DictCursor,
        connect_timeout=3
    )

def handle_db_error(e):
    """Generates a friendly response for database connection errors."""
    error_msg = str(e)
    # Check if request expects JSON
    if request.path.startswith('/api/') or request.headers.get('Accept') == 'application/json' or request.args.get('json') == 'true':
        return jsonify({
            'success': False,
            'message': 'Database connection error. Please ensure XAMPP MySQL is running.',
            'error': error_msg
        }), 500
    
    # Return a premium styled HTML error page
    return render_template('db_error.html', error=error_msg), 500

@app.errorhandler(Exception)
def handle_exception(e):
    """Global exception handler to capture operational db errors cleanly."""
    if isinstance(e, pymysql.MySQLError) or "pymysql" in str(type(e)).lower():
        return handle_db_error(e)
    # Default Flask exception handling
    return jsonify({
        'success': False,
        'message': 'An unexpected error occurred.',
        'error': str(e)
    }), 500

# Helper to check if user is logged in
def validate_email(email):
    """Simple regex email validation used in registration."""
    email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(email_regex, email) is not None

# ----------------- PAGE ROUTES -----------------

@app.route('/register', methods=['GET'])
def register_page():
    """Renders the registration page."""
    if is_logged_in():
        return redirect(url_for('products_page'))
    return render_template('register.html')

@app.route('/')
def index():
    """Redirect to products listing or login based on auth state."""
    if is_logged_in():
        return redirect(url_for('products_page'))
    return redirect(url_for('login_page'))

@app.route('/login', methods=['GET'])
def login_page():
    """Renders the login page."""
    if is_logged_in():
        return redirect(url_for('products_page'))
    return render_template('login.html')

@app.route('/products', methods=['GET'])
def products_page():
    """
    Serves either the HTML products page or the products JSON data.
    Ensures beginner-friendly, clean routing architecture.
    """
    if not is_logged_in():
        if request.headers.get('Accept') == 'application/json' or request.args.get('json') == 'true':
            return jsonify({'success': False, 'message': 'Unauthorized session. Please login.'}), 401
        return redirect(url_for('login_page'))

    # API request check (Accepts JSON or ?json=true)
    if request.headers.get('Accept') == 'application/json' or request.args.get('json') == 'true':
        search_query = request.args.get('search', '').strip()
        try:
            conn = get_db_connection()
            with conn.cursor() as cursor:
                if search_query:
                    # Filter products by name or category
                    sql = "SELECT * FROM products WHERE name LIKE %s OR category LIKE %s ORDER BY id DESC"
                    cursor.execute(sql, (f'%{search_query}%', f'%{search_query}%'))
                else:
                    sql = "SELECT * FROM products ORDER BY id DESC"
                    cursor.execute(sql)
                products = cursor.fetchall()
            conn.close()
            return jsonify({'success': True, 'products': products})
        except pymysql.MySQLError as e:
            return handle_db_error(e)

    # Browser page request
    return render_template('products.html')

@app.route('/add-product', methods=['GET'])
def add_product_page():
    """Renders the add product form page."""
    if not is_logged_in():
        return redirect(url_for('login_page'))
    return render_template('add_product.html')


# ----------------- API ROUTES -----------------

@app.route('/api/register', methods=['POST'])
def register_api():
    """Handles user registration. Stores hashed password."""
    data = request.get_json() or {}
    email = data.get('email', '').strip()
    password = data.get('password', '')
    if not email or not password:
        return jsonify({'success': False, 'message': 'Email and password are required.'}), 400
    # Simple email format check
    if not validate_email(email):
        return jsonify({'success': False, 'message': 'Invalid email format.'}), 400
    # Hash password
    pw_hash = generate_password_hash(password)
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            # Ensure email not already taken
            cursor.execute('SELECT id FROM users WHERE email = %s', (email,))
            if cursor.fetchone():
                conn.close()
                return jsonify({'success': False, 'message': 'Email already registered.'}), 409
            cursor.execute('INSERT INTO users (email, password) VALUES (%s, %s)', (email, pw_hash))
            conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Registration successful. Please log in.'}), 201
    except pymysql.MySQLError as e:
        return handle_db_error(e)

@app.route('/api/login', methods=['POST'])
def login_api():
    """Handles secure user authentication and session creation."""
    # Read email and password from JSON request
    data = request.get_json() or {}
    email = data.get('email', '').strip()
    password = data.get('password', '')

    if not email or not password:
        return jsonify({'success': False, 'message': 'Please provide both email and password.'}), 400

    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            sql = "SELECT * FROM users WHERE email = %s"
            cursor.execute(sql, (email,))
            user = cursor.fetchone()
        conn.close()

        if user and check_password_hash(user['password'], password):
            # Establish session credentials
            session['user_id'] = user['id']
            session['email'] = user['email']
            return jsonify({'success': True, 'message': 'Authentication successful. Redirecting...'})
        else:
            return jsonify({'success': False, 'message': 'Invalid email or password.'}), 401

    except pymysql.MySQLError as e:
        return handle_db_error(e)

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    """Clears the user session and logs out."""
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('login_page'))

@app.route('/add-product', methods=['POST'])
def add_product_api():
    """Handles adding a new product via POST API."""
    if not is_logged_in():
        return jsonify({'success': False, 'message': 'Unauthorized session. Please login.'}), 401

    data = request.get_json() or {}
    name = data.get('name', '').strip()
    price = data.get('price')
    description = data.get('description', '').strip()
    image = data.get('image', '').strip()
    category = data.get('category', '').strip()

    # Form field validations
    if not all([name, price, description, image, category]):
        return jsonify({'success': False, 'message': 'All form fields are required.'}), 400

    try:
        price_val = float(price)
        if price_val <= 0:
            return jsonify({'success': False, 'message': 'Price must be a positive decimal number.'}), 400
    except ValueError:
        return jsonify({'success': False, 'message': 'Invalid price format.'}), 400

    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            sql = "INSERT INTO products (name, price, description, image, category) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(sql, (name, price_val, description, image, category))
            conn.commit()
            product_id = cursor.lastrowid
        conn.close()

        return jsonify({
            'success': True,
            'message': 'Product added successfully!',
            'product_id': product_id
        }), 201

    except pymysql.MySQLError as e:
        return handle_db_error(e)

@app.route('/update-product/<int:product_id>', methods=['PUT'])
def update_product_api(product_id):
    """Handles updating product details via PUT API."""
    if not is_logged_in():
        return jsonify({'success': False, 'message': 'Unauthorized session. Please login.'}), 401

    data = request.get_json() or {}
    name = data.get('name', '').strip()
    price = data.get('price')
    description = data.get('description', '').strip()
    image = data.get('image', '').strip()
    category = data.get('category', '').strip()

    # Form field validations
    if not all([name, price, description, image, category]):
        return jsonify({'success': False, 'message': 'All form fields are required for update.'}), 400

    try:
        price_val = float(price)
        if price_val <= 0:
            return jsonify({'success': False, 'message': 'Price must be a positive decimal number.'}), 400
    except ValueError:
        return jsonify({'success': False, 'message': 'Invalid price format.'}), 400

    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            # Check if product exists first
            cursor.execute("SELECT id FROM products WHERE id = %s", (product_id,))
            if not cursor.fetchone():
                conn.close()
                return jsonify({'success': False, 'message': 'Product not found.'}), 404

            sql = """UPDATE products 
                     SET name = %s, price = %s, description = %s, image = %s, category = %s 
                     WHERE id = %s"""
            cursor.execute(sql, (name, price_val, description, image, category, product_id))
            conn.commit()
        conn.close()

        return jsonify({'success': True, 'message': 'Product updated successfully!'})

    except pymysql.MySQLError as e:
        return handle_db_error(e)

@app.route('/delete-product/<int:product_id>', methods=['DELETE'])
def delete_product_api(product_id):
    """Handles deleting a product via DELETE API."""
    if not is_logged_in():
        return jsonify({'success': False, 'message': 'Unauthorized session. Please login.'}), 401

    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            # Check if product exists first
            cursor.execute("SELECT id FROM products WHERE id = %s", (product_id,))
            if not cursor.fetchone():
                conn.close()
                return jsonify({'success': False, 'message': 'Product not found.'}), 404

            sql = "DELETE FROM products WHERE id = %s"
            cursor.execute(sql, (product_id,))
            conn.commit()
        conn.close()

        return jsonify({'success': True, 'message': 'Product deleted successfully!'})

    except pymysql.MySQLError as e:
        return handle_db_error(e)

if __name__ == '__main__':
    # Running Flask server on port 5000 in debug mode
    app.run(debug=True, host='0.0.0.0', port=5000)
