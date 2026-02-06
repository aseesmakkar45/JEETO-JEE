from flask import Flask, render_template, request, jsonify, send_from_directory, redirect, url_for
import razorpay
import csv
import os
import datetime
import json
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import uuid

# Try to load environment variables
try:
    from dotenv import load_dotenv, find_dotenv
    env_file = find_dotenv()
    print(f"Loading .env from: {env_file}")
    load_dotenv(env_file, override=True)
except ImportError:
    print("Warning: python-dotenv not installed. Skipping .env loading.")

app = Flask(__name__, static_url_path='', static_folder='.', template_folder='.')

# ------------------------------------------------------------------------------
# Configuration
# ------------------------------------------------------------------------------
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-change-this-in-production')
# Use DATABASE_URL from environment (for Postgres) or fallback to local SQLite
database_url = os.getenv('DATABASE_URL', 'sqlite:///jeeto_jee.db')
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Optimized DB Connection for Render/Cloud
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    "pool_pre_ping": True,  # Checks connection liveness before query (fixes disconnects)
    "pool_recycle": 300,    # Recycle connections every 5 minutes
    "pool_timeout": 30      # Wait max 30s for a connection
}

RAZORPAY_KEY_ID = os.getenv('RAZORPAY_KEY_ID')
RAZORPAY_KEY_SECRET = os.getenv('RAZORPAY_KEY_SECRET')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD')

client = None
if RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET:
    client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))
else:
    print("WARNING: Razorpay keys are missing or invalid. Payment features will not work.")

# ------------------------------------------------------------------------------
# Database Setup
# ------------------------------------------------------------------------------
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'index' # Redirect here if not logged in

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def as_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone
        }

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    custom_id = db.Column(db.String(50), unique=True, nullable=False)
    # Status: INIT, CREATED, ATTEMPTED, PAID, MOCK_PAID
    status = db.Column(db.String(20), default='INIT')
    
    amount = db.Column(db.Float, default=0.0)
    currency = db.Column(db.String(10), default='INR')
    
    # User Details
    student_name = db.Column(db.String(100))
    student_email = db.Column(db.String(100))
    student_phone = db.Column(db.String(20))
    
    # Plan Details
    plan_name = db.Column(db.String(100))
    plan_category = db.Column(db.String(50))
    
    # Razorpay Details
    razorpay_order_id = db.Column(db.String(100))
    razorpay_payment_id = db.Column(db.String(100))
    razorpay_signature = db.Column(db.String(200))
    
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def as_dict(self):
        return {
            'custom_id': self.custom_id,
            'status': self.status,
            'amount': self.amount,
            'student_name': self.student_name,
            'plan_name': self.plan_name,
            'razorpay_payment_id': self.razorpay_payment_id,
            'timestamp': self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        }

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Create tables
with app.app_context():
    db.create_all()

# ------------------------------------------------------------------------------
# Routes
# ------------------------------------------------------------------------------

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/index.html')
def index_redirect():
    return redirect(url_for('index'))

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory('.', path)

# Pricing Configuration (Must match frontend)
PRICING_CONFIG = {
    'jan': {'standard': 699, 'elite': 999},
    'april-boards': {'standard': 699, 'elite': 999},
    'april': {'standard': 499, 'elite': 699}
}

@app.route('/checkout')
def checkout():
    # Generate a new Order ID for every visit to checkout (or we could fetch pending ones)
    try:
        # Get Plan Details from URL to determine ID prefix
        plan_type = request.args.get('plan', 'standard').lower() # standard / elite
        if plan_type == 'std': plan_type = 'standard' # Normalize
        
        category = request.args.get('category', 'april').lower() # april / april-boards
        
        # Determine ID components
        # Type: s for Standard, e for Elite
        type_code = 'e' if 'elite' in plan_type else 's'
        
        # Category: b for Boards (april-boards), a for April (april)
        cat_code = 'b' if 'boards' in category else 'a'
        
        # Define the prefix for this series
        prefix = f"#aJEETO{type_code}JEE{cat_code}"
        
        # Create a placeholder payment record to reserve the row
        temp_id = str(uuid.uuid4())
        payment = Payment(custom_id=temp_id)
        db.session.add(payment)
        db.session.commit()
        
        # Custom ID Generation with Retry Logic (to prevent IntegrityError)
        max_retries = 5
        for attempt in range(max_retries):
            try:
                # Count existing orders with this prefix
                series_count = Payment.query.filter(Payment.custom_id.startswith(prefix)).count()
                next_seq = series_count + 1
                
                # Generate Custom ID
                new_id = f"{prefix}{next_seq:03d}"
                
                # Check for uniqueness BEFORE committing
                if not Payment.query.filter_by(custom_id=new_id).first():
                    payment.custom_id = new_id
                    db.session.commit()
                    break
                else:
                    # If ID exists, increment safely
                    print(f"Collision detected for {new_id}, trying next...")
                    continue
            except Exception as inner_e:
                db.session.rollback()
                if attempt == max_retries - 1:
                    raise inner_e
                print(f"Retry {attempt+1} due to: {inner_e}")

        # Upgrade Logic & Limit Check
        upgrade_price = None
        limit_reached = False
        
        if current_user.is_authenticated:
            # 1. Check Total Purchase Count
            purchase_count = Payment.query.filter(
                Payment.student_email == current_user.email,
                Payment.status.in_(['PAID', 'MOCK_PAID'])
            ).count()
            
            if purchase_count >= 2:
                limit_reached = True
            
            # 2. Upgrade Calculation (if under limit)
            if not limit_reached:
                # Find latest ACTIVE plan
                # Note: We check for 'PAID' or 'MOCK_PAID' just to be safe if testing
                last_payment = Payment.query.filter(
                    Payment.student_email == current_user.email, 
                    Payment.status.in_(['PAID', 'MOCK_PAID'])
                ).order_by(Payment.timestamp.desc()).first()
                
                if last_payment:
                    # Determine current plan value
                    old_category = last_payment.plan_category
                    if old_category:
                        old_category = old_category.lower()
                    old_plan_name = last_payment.plan_name.lower() if last_payment.plan_name else ''
                    old_type = 'elite' if 'elite' in old_plan_name else 'standard'
                    
                    # Get prices
                    try:
                        old_price = PRICING_CONFIG.get(old_category, {}).get(old_type, 0)
                        new_price = PRICING_CONFIG.get(category, {}).get(plan_type, 0)
                        
                        # Apply upgrade pricing if New >= Old (Upgrade/Swap) (Allow 0 diff coverage)
                        if new_price >= old_price and old_price > 0:
                            upgrade_price = new_price - old_price
                    except Exception:
                        pass # Fallback to standard price if config mismatch
        
        # Pass to template
        return render_template('checkout.html', order_id=payment.custom_id, upgrade_price=upgrade_price, limit_reached=limit_reached)
    except Exception as e:
        db.session.rollback()
        print(f"Error creating payment init: {e}")
        with open('checkout_error.txt', 'w') as f:
            f.write(str(e))
        return render_template('checkout.html', order_id="ERROR")

@app.route('/checkout.html')
def checkout_html():
    return redirect(url_for('checkout'))

@app.route('/success')
def success():
    # Get payment_id (DB ID) or custom_id from args
    cid = request.args.get('order_id')
    payment_ref = request.args.get('payment_ref') # Razorpay Pay ID
    
    # 1. Look up Payment Record
    title = "Enrollment Successful!"
    message = "Thank you for joining JEETO JEE. We have received your payment."
    
# WhatsApp Links Configuration
    WHATSAPP_LINKS = {
        'april': {
            'standard': 'https://chat.whatsapp.com/D5jRDS7Kqjb1LUF0O9VXY7',
            'elite': 'https://chat.whatsapp.com/JRYpdmuAweo2VL6Zuud60N'
        },
        'april-boards': {
            'standard': 'https://chat.whatsapp.com/KMgl7zS0d6v3Zuq06Cubzm',
            'elite': 'https://chat.whatsapp.com/DobPEtJV5MSICtNiQRWCXD'
        }
    }

    whatsapp_link = None
    if cid:
        payment = Payment.query.filter_by(custom_id=cid).first()
        if payment:
             # 2. Determine Message Type
             user_email = payment.student_email
             
             # Count PAID/MOCK_PAID payments for this user, including this one
             count = 0
             if user_email:
                 count = Payment.query.filter(
                    Payment.student_email == user_email,
                    Payment.status.in_(['PAID', 'MOCK_PAID'])
                 ).count()
             
             plan_name = payment.plan_name or "Premium Plan"
             
             # Determine Link
             try:
                 p_cat = payment.plan_category.lower() if payment.plan_category else 'april'
                 p_name = payment.plan_name.lower() if payment.plan_name else 'standard'
                 p_type = 'elite' if 'elite' in p_name else 'standard'
                 
                 whatsapp_link = WHATSAPP_LINKS.get(p_cat, {}).get(p_type)
             except Exception:
                 pass

             if count > 1:
                 # Upgrade
                 title = "Upgrade Successful! 🚀"
                 message = f"You have successfully upgraded your account to <strong>{plan_name}</strong>. Enjoy the new elite features!"
             else:
                 # New Purchase
                 title = "Welcome Aboard! 🎉"
                 message = f"You have successfully subscribed to <strong>{plan_name}</strong>."
                 if whatsapp_link:
                     message += " Please join the exclusive WhatsApp community below to get started."

    return render_template('success.html', order_id=cid, payment_ref=payment_ref, title=title, message=message, whatsapp_link=whatsapp_link)

# ------------------------------------------------------------------------------
# Auth Endpoints
# ------------------------------------------------------------------------------

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    name = data.get('name')
    email = data.get('email')
    phone = data.get('phone')
    password = data.get('password')

    # Basic Validation
    if not name or not email or not phone or not password:
        return jsonify({'error': 'All fields are required'}), 400
    
    # Check if user exists (Check email or phone individually)
    if User.query.filter((User.email == email) | (User.phone == phone)).first():
        return jsonify({'error': 'User with this email or phone already exists'}), 400

    new_user = User(name=name, email=email, phone=phone)
    new_user.set_password(password)
    
    db.session.add(new_user)
    db.session.commit()
    
    login_user(new_user)
    return jsonify({'message': 'Registration successful', 'user': new_user.as_dict()})

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    identifier = data.get('identifier')
    password = data.get('password')

    user = User.query.filter((User.email == identifier) | (User.phone == identifier)).first()

    if user and user.check_password(password):
        login_user(user, remember=True)
        return jsonify({'message': 'Login successful', 'user': user.as_dict()})
    
    return jsonify({'error': 'Invalid credentials'}), 401

@app.route('/api/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Logged out successfully'})

@app.route('/api/user', methods=['GET'])
def get_current_user():
    if current_user.is_authenticated:
        return jsonify({'authenticated': True, 'user': current_user.as_dict()})
    return jsonify({'authenticated': False}), 200

# ------------------------------------------------------------------------------
# Payment / Lead Endpoints
# ------------------------------------------------------------------------------

@app.route('/api/create-order', methods=['POST'])
def create_order():
    if not client:
        return jsonify({'error': 'Razorpay not configured'}), 503

    try:
        data = request.json
        amount = data.get('amount')
        student = data.get('student_details', {})
        plan = data.get('plan_details', {})
        custom_id = data.get('custom_id') # Passed from frontend
        
        # Update the Payment Record
        payment = None
        if custom_id:
            payment = Payment.query.filter_by(custom_id=custom_id).first()
            if payment:
                payment.amount = amount/100 if amount else 0
                payment.student_name = student.get('name')
                payment.student_email = student.get('identifier') or student.get('email') # Check naming
                payment.student_phone = student.get('phone')
                payment.plan_name = plan.get('name')
                payment.plan_category = plan.get('category')
                payment.status = 'CREATED'
                db.session.commit()

        if amount == 0:
             print("Free Upgrade / Zero Cost Order")
             import time
             order_data = {
                 'id': f'order_free_{int(time.time())}',
                 'amount': 0,
                 'currency': 'INR',
                 'status': 'paid' # Auto-paid
             }
             order = order_data
        # Check for MOCK/PLACEHOLDER Keys
        elif 'PLACEHOLDER' in RAZORPAY_KEY_ID:
            print("Using Mock Order (Placeholder Keys)")
            import time
            order_data = {
                'id': f'order_mock_{int(time.time())}',
                'amount': amount,
                'currency': 'INR',
                'status': 'created'
            }
            order = order_data # Skip real API call
        else:
            order_data = {'amount': amount, 'currency': 'INR', 'payment_capture': 1}
            order = client.order.create(data=order_data)
        
        # Save Razorpay Order ID to DB
        if payment:
            payment.razorpay_order_id = order.get('id')
            db.session.commit()

        
        # Inject Key ID for frontend
        response_data = order.copy()
        response_data['key'] = RAZORPAY_KEY_ID
        
        return jsonify(response_data)
    except Exception as e:
        db.session.rollback()
        print(f"Error creating order: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/verify-payment', methods=['POST'])
def verify_payment():
    if not client:
        return jsonify({'error': 'Razorpay not configured'}), 503

    try:
        data = request.json
        
        # MOCK BYPASS: Check if this is a simulation
        razorpay_payment_id = data.get('razorpay_payment_id', '')
        custom_id = data.get('custom_id') # We need to pass this from frontend or lookup by Order ID
        
        # Find Payment by Razorpay Order ID if custom_id missing, or vice versa
        payment = None
        if data.get('razorpay_order_id'):
            payment = Payment.query.filter_by(razorpay_order_id=data['razorpay_order_id']).first()
        
        if not payment and custom_id:
             payment = Payment.query.filter_by(custom_id=custom_id).first()

        # FAIL-SAFE: Create record if missing but user paid
        if not payment and not razorpay_payment_id.startswith('pay_mock_'):
            print(f"FAIL-SAFE TRIGGERED: Missing record for {custom_id or 'UNKNOWN'}. Creating one now.")
            try:
                # Extract details from request if available
                student = data.get('student_details', {})
                plan = data.get('plan_details', {})
                
                payment = Payment(
                    custom_id=custom_id or f"FS_{str(uuid.uuid4())[:8]}",
                    status='CREATED', # Will be updated to PAID below
                    student_name=student.get('name'),
                    student_email=student.get('email'),
                    student_phone=student.get('phone'),
                    plan_name=plan.get('name'),
                    plan_category=plan.get('category'),
                    amount=plan.get('price', 0)
                )
                db.session.add(payment)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                print(f"Fail-safe record creation failed: {e}")

        # Handle Mock or Free Payment
        if razorpay_payment_id.startswith('pay_mock_') or (payment and payment.razorpay_order_id and payment.razorpay_order_id.startswith('order_free_')):
            if payment:
                payment.status = 'PAID' # Mark as truly PAID
                # User requested NO transaction ID for zero-cost upgrades, so we allow empty string
                payment.razorpay_payment_id = razorpay_payment_id 
                db.session.commit()
            return jsonify({'status': 'success', 'custom_id': payment.custom_id if payment else ''})

        if razorpay_payment_id.startswith('pay_mock_'):
            if payment:
                payment.status = 'MOCK_PAID'
                payment.razorpay_payment_id = razorpay_payment_id
                db.session.commit()
            return jsonify({'status': 'success', 'custom_id': payment.custom_id if payment else ''})

        params_dict = {
            'razorpay_order_id': data['razorpay_order_id'],
            'razorpay_payment_id': data['razorpay_payment_id'],
            'razorpay_signature': data['razorpay_signature']
        }
        client.utility.verify_payment_signature(params_dict)
        
        if payment:
            payment.status = 'PAID'
            payment.razorpay_payment_id = data['razorpay_payment_id']
            payment.razorpay_signature = data['razorpay_signature']
            db.session.commit()
            
        return jsonify({'status': 'success', 'custom_id': payment.custom_id if payment else ''})
    except razorpay.errors.SignatureVerificationError:
        db.session.rollback()
        return jsonify({'error': 'Payment verification failed'}), 400
    except Exception as e:
        db.session.rollback()
        print(f"Error verifying payment: {e}")
        return jsonify({'error': str(e)}), 500

# ------------------------------------------------------------------------------
# Admin Routes
# ------------------------------------------------------------------------------
from flask import session

@app.route('/admin')
def admin_root():
    return redirect(url_for('admin_login'))

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            return render_template('templates/admin_login.html', error="Invalid Password")
    return render_template('templates/admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin_login'))

@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    users = User.query.all()
    # Loading orders from CSV for now, or we could add a DB model for Orders later if needed.
    # For now, let's just display users. If orders are in CSV, we can read them.
    
    # Filter: Show only completed payments with a valid Razorpay Payment ID
    orders = Payment.query.filter(
        Payment.razorpay_payment_id != None,
        Payment.razorpay_payment_id != ''
    ).order_by(Payment.id.desc()).all()
    
    # Map User Phone -> Latest Order ID for display in Users table
    user_latest_order = {}
    for order in orders:
        # Link by Phone Number
        if order.student_phone and order.student_phone not in user_latest_order:
            user_latest_order[order.student_phone] = order.custom_id
            
    return render_template('templates/admin_dashboard.html', users=users, orders=orders, user_orders=user_latest_order)

@app.route('/profile')
@login_required
def profile():
    # Simple logic: Just get the first letter of the name
    user_initial = current_user.name[0].upper() if current_user.name else "?"
    return render_template('profile.html', user=current_user, user_initial=user_initial)

@app.route('/my-plan')
@login_required
def my_plan():
    # Find latest PAID payment for this user by phone
    # We use phone because email might not be reliable if they changed it, but phone is our key linker now
    latest_payment = Payment.query.filter_by(student_phone=current_user.phone, status='PAID')\
        .order_by(Payment.id.desc()).first()
    
    # If no real payment, check mock
    if not latest_payment:
        latest_payment = Payment.query.filter_by(student_phone=current_user.phone, status='MOCK_PAID')\
            .order_by(Payment.id.desc()).first()
            
    active_plan = None
    if latest_payment:
        active_plan = {
            'name': latest_payment.plan_name,
            'category': latest_payment.plan_category,
            'custom_id': latest_payment.custom_id
        }
        
    return render_template('my_plans.html', user=current_user, active_plan=active_plan)

@app.route('/admin/delete/user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'error': 'User not found'}), 404

@app.route('/admin/delete/order/<int:order_id>', methods=['POST'])
def delete_order(order_id):
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    order = Payment.query.get(order_id)
    if order:
        db.session.delete(order)
        db.session.commit()
        return jsonify({'success': True})
    return jsonify({'error': 'Order not found'}), 404

@app.route('/admin/delete-all/<item_type>', methods=['POST'])
def delete_all_items(item_type):
    if not session.get('admin_logged_in'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        if item_type == 'user':
            num_deleted = db.session.query(User).delete()
            db.session.commit()
            return jsonify({'success': True, 'count': num_deleted})
        elif item_type == 'order':
            num_deleted = db.session.query(Payment).delete()
            db.session.commit()
            return jsonify({'success': True, 'count': num_deleted})
        else:
            return jsonify({'error': 'Invalid item type'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/terms')
def terms():
    return render_template('terms.html')

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

@app.route('/refund')
def refund():
    return render_template('refund.html')

# ------------------------------------------------------------------------------
# Helper Functions
# ------------------------------------------------------------------------------
def save_order(student, plan, transaction_id, status='PAID', amount=0):
    file_exists = os.path.isfile('orders.csv')
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    row = [timestamp, student.get('name'), student.get('email'), student.get('phone'), plan.get('name'), plan.get('category'), amount, status, transaction_id]
    
    with open('orders.csv', 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['Timestamp', 'Name', 'Email', 'Phone', 'Plan Name', 'Category', 'Amount', 'Status', 'Transaction/Order ID'])
        writer.writerow(row)

@app.teardown_appcontext
def shutdown_session(exception=None):
    db.session.remove()

if __name__ == '__main__':
    print("Starting Flask server on http://localhost:8000")
    app.run(port=8000, debug=True)
