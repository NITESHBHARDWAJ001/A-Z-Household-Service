from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, current_user,logout_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime
import os
import time
import datetime as dt


app = Flask(__name__, instance_path='/tmp')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tmp/provider.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = '17ce2afd1bf4a1e4eecbfbdf'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view ="login"
db = SQLAlchemy(app)
class User(db.Model):
    username = db.Column(db.String(80), primary_key=True, unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    user_type = db.Column(db.String(20), nullable=False)
# Service Provider Model
class Service_provider(UserMixin,db.Model):
    Fullname = db.Column(db.String(20), nullable=False)
    username = db.Column(db.String(80), primary_key=True, unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    service_name = db.Column(db.String(100), nullable=False)
    experience = db.Column(db.Integer, nullable=False)
    address = db.Column(db.String(200), nullable=False)
    pincode = db.Column(db.String(14), nullable=False)
    document_name = db.Column(db.String(250), nullable=False)
    document_data = db.Column(db.LargeBinary, nullable=False)
    status = db.Column(db.String(20), default='pending')
    def get_id(self):
        return self.username

# User Registration Model
class User_registeration(UserMixin,db.Model):
    Fullname = db.Column(db.String(20), nullable=False)
    username= db.Column(db.String(80), primary_key=True,unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    pincode = db.Column(db.String(14), nullable=False)
    def get_id(self):
        return self.username

# Service Request Model
class request_service(db.Model):
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    Fullname = db.Column(db.String(20), nullable=False)
    Service_required = db.Column(db.String(100), nullable=False)
    Description = db.Column(db.String(200))
    Provider_username=db.Column(db.String(200))
    status = db.Column(db.String(20), default='pending') 
    User_username=db.Column(db.String(20)) 
     # Link to a service provider
    service_provider_username = db.Column(db.String(80), db.ForeignKey('service_provider.username'), nullable=True)

    # Relationship to access the assigned service provider
    service_provider = db.relationship('Service_provider', backref='requests')

class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    price = db.Column(db.Integer,nullable=False)
    description = db.Column(db.String(200))

class AdminUser(UserMixin):
    id =1
    user_type ='admin' 

class BlockedUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False)
    user_type = db.Column(db.String(50), nullable=False)
    blocked_at = db.Column(db.DateTime, default=datetime.utcnow)

    def _repr_(self):
        return f"<BlockedUser {self.username}>"

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 star rating
    comment = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign keys
    service_provider_username = db.Column(db.String(80), db.ForeignKey('service_provider.username'), nullable=False)
    user_username = db.Column(db.String(80), db.ForeignKey('user_registeration.username'), nullable=False)
    
    # Relationships
    service_provider = db.relationship('Service_provider', backref=db.backref('reviews', lazy='dynamic'))
    user = db.relationship('User_registeration', backref=db.backref('reviews', lazy='dynamic'))

# Rental Item Model
class RentalItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    daily_rate = db.Column(db.Float, nullable=False)
    image_name = db.Column(db.String(200))
    category = db.Column(db.String(50))
    is_available = db.Column(db.Boolean, default=True)
    
    # Foreign key to service provider
    provider_username = db.Column(db.String(80), db.ForeignKey('service_provider.username'), nullable=False)
    
    # Relationship
    provider = db.relationship('Service_provider', backref=db.backref('rental_items', lazy='dynamic'))

# Rental Request Model
class RentalRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected, completed, cancelled
    total_price = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign keys
    item_id = db.Column(db.Integer, db.ForeignKey('rental_item.id'), nullable=False)
    user_username = db.Column(db.String(80), db.ForeignKey('user_registeration.username'), nullable=False)
    
    # Relationships
    item = db.relationship('RentalItem', backref=db.backref('rental_requests', lazy='dynamic'))
    user = db.relationship('User_registeration', backref=db.backref('rental_requests', lazy='dynamic'))
    
    def calculate_total_price(self):
        """Calculate the total price based on the rental duration and daily rate."""
        if not self.start_date or not self.end_date or not self.item:
            return 0
            
        # Calculate days difference
        days = (self.end_date - self.start_date).days
        if days < 1:
            days = 1  # Minimum 1 day rental
            
        return days * self.item.daily_rate

with app.app_context():
    db.create_all()
@login_manager.user_loader
def load_user(user_id):
    # Retrieve the user based on the user_id
    if(user_id=='1'):
        return AdminUser()
    else:
        user = Service_provider.query.get(user_id) or User_registeration.query.get(user_id)
        return user
         
    
@app.route('/')
@login_required
def home():
    print(session)
    if session['user_type'] == 'service_provider':
        # Get all service requests that are linked to the current provider
        service_requests = request_service.query.filter_by(Provider_username=session.get('username')).all()
        return render_template('provider_requests.html', requests=service_requests)
    elif session['user_type']=="user":
        user_request = request_service.query.filter_by(User_username=session.get('username')).all()
        return render_template('user_home.html',request=user_request)
    else:
        flash("You are not authorized to view this page", 'danger')
        return redirect(url_for('login'))

@app.route('/home')
def home_page():
    return render_template('home.html')
@app.route('/user_home')
def user_home():
    flash("hlo {{current_user.username}}")
    user_requests = request_service.query.filter_by(User_username=session.get('username')).all()
    return render_template('user_home.html',request=user_requests,user =current_user.Username)
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.user_type != 'admin':
            flash('Admin access required.', 'danger')
            return redirect(url_for('home'))
        return f(*args, **kwargs)
    return decorated_function

# Route to add a new service
@app.route('/add_service', methods=['GET', 'POST'])
@login_required
def add_service():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        price = request.form.get('price')
        if not name:
            flash('Service name is required!', 'danger')
            return redirect(url_for('add_service'))

        # Debug output to see the data being received
        print(f"Received name: {name}, description: {description}")
        new_service = Service(name=name, description=description,price = price)
        db.session.add(new_service)
        db.session.commit()
        flash('New service added!', 'success')
        return redirect(url_for('admin_dashboard'))
    return render_template('/add_service.html')

# Route to view all users with block/unblock option
@app.route('/manage_users', methods=['GET', 'POST'])
@login_required
def manage_users():
    # Get all users (service providers and regular users)

    if request.method == 'POST':
        action = request.form.get('action')
        username = request.form.get('username')
        user_type = request.form.get('user_type')
        # Block the user
        if action == 'block':
            user = User_registeration.query.filter_by(username=username).first() or Service_provider.query.filter_by(username=username).first()
            if user:
                user.is_blocked = True
                db.session.commit()

                # Add to BlockedUser table
                blocked_user = BlockedUser(username=username, user_type=user_type)
                db.session.add(blocked_user)
                db.session.commit()

                flash(f"User {username} has been blocked.", 'success')
            else:
                flash(f"User {username} not found.", 'danger')

        # Unblock the user
        elif action == 'unblock':
            blocked_user = BlockedUser.query.filter_by(username=username).first()
            if blocked_user:
                # Remove from BlockedUser table
                db.session.delete(blocked_user)
                db.session.commit()

                # Update the User table to unblock
                user = User.query.filter_by(username=username).first()
                if user:
                    user.is_blocked = False
                    db.session.commit()

                flash(f"User {username} has been unblocked.", 'success')
            else:
                flash(f"Blocked user {username} not found.", 'danger')

        return redirect(url_for('manage_users'))

    return render_template('manage_users.html')

# Admin Dashboard
@app.route('/admin')
@login_required
def admin_dashboard():
    # Get pending service providers
    pending_service_providers = Service_provider.query.filter_by(status='pending').all()
    
    # Get all services
    services = Service.query.all()
    
    # Count service providers by status
    provider_status = {
        'approved': Service_provider.query.filter_by(status='approved').count(),
        'pending': Service_provider.query.filter_by(status='pending').count(),
        'rejected': Service_provider.query.filter_by(status='rejected').count()
    }
    
    # Count total users and providers
    total_users = User_registeration.query.count()
    total_providers = Service_provider.query.count()
    
    # Count providers by service
    service_counts = {}
    for service in services:
        count = Service_provider.query.filter_by(service_name=service.name, status='approved').count()
        service_counts[service.name] = count
    
    # Get top-rated service providers
    top_providers = []
    approved_providers = Service_provider.query.filter_by(status='approved').all()
    
    for provider in approved_providers:
        reviews = Review.query.filter_by(service_provider_username=provider.username).all()
        completed_services = request_service.query.filter_by(
            Provider_username=provider.username, 
            status='completed_by_provider'
        ).count()
        
        avg_rating = 0
        if reviews:
            avg_rating = sum(review.rating for review in reviews) / len(reviews)
        
        provider_data = {
            'username': provider.username,
            'Fullname': provider.Fullname,
            'service_name': provider.service_name,
            'experience': provider.experience,
            'avg_rating': avg_rating,
            'completed_services': completed_services
        }
        top_providers.append(provider_data)
    
    # Sort providers by rating (descending)
    top_providers = sorted(top_providers, key=lambda x: (x['avg_rating'], x['completed_services']), reverse=True)[:10]
    
    # Calculate average rating by service category
    category_ratings = {}
    for service in services:
        providers = Service_provider.query.filter_by(service_name=service.name, status='approved').all()
        if providers:
            total_rating = 0
            rated_providers = 0
            
            for provider in providers:
                reviews = Review.query.filter_by(service_provider_username=provider.username).all()
                if reviews:
                    provider_avg = sum(review.rating for review in reviews) / len(reviews)
                    total_rating += provider_avg
                    rated_providers += 1
            
            if rated_providers > 0:
                category_ratings[service.name] = round(total_rating / rated_providers, 1)
            else:
                category_ratings[service.name] = 0
    
    # Get rental items stats
    total_rental_items = RentalItem.query.count()
    available_items = RentalItem.query.filter_by(is_available=True).count()
    rented_items = total_rental_items - available_items
    
    rental_status = {
        'available': available_items,
        'rented': rented_items
    }
    
    # Get rental items by category
    rental_categories = {}
    categories = db.session.query(RentalItem.category).distinct().all()
    
    for category_tuple in categories:
        category = category_tuple[0] or "Uncategorized"
        total = RentalItem.query.filter_by(category=category).count()
        available = RentalItem.query.filter_by(category=category, is_available=True).count()
        
        rental_categories[category] = {
            'total': total,
            'available': available,
            'rented': total - available
        }
    
    # Get most requested rental items
    top_rental_items = []
    all_items = RentalItem.query.all()
    
    for item in all_items:
        request_count = RentalRequest.query.filter_by(item_id=item.id).count()
        if request_count > 0:
            top_rental_items.append({
                'id': item.id,
                'name': item.name,
                'category': item.category or "Uncategorized",
                'request_count': request_count
            })
    
    # Sort by request count (descending)
    top_rental_items = sorted(top_rental_items, key=lambda x: x['request_count'], reverse=True)[:5]
    
    return render_template('admin_dashboard.html', 
                          service_providers=pending_service_providers,
                          services=services,
                          provider_status=provider_status,
                          total_users=total_users,
                          total_providers=total_providers,
                          service_counts=service_counts,
                          top_providers=top_providers,
                          category_ratings=category_ratings,
                          total_rental_items=total_rental_items,
                          rental_status=rental_status,
                          rental_categories=rental_categories,
                          top_rental_items=top_rental_items)

@app.route('/approve_service_provider/<username>', methods=['GET'])
@login_required
def approve_service_provider(username):
  

    service_provider = Service_provider.query.get(username)
    if service_provider and service_provider.status == 'pending':
        service_provider.status = 'approved'  # Change status to approved
        db.session.commit()
        flash(f'Service provider {username} approved.', 'success')
    else:
        flash('Service provider not found or already processed.', 'danger')

    return redirect(url_for('admin_dashboard'))

@app.route('/reject_service_provider/<username>', methods=['GET'])
@login_required
def reject_service_provider(username):

    service_provider = Service_provider.query.get(username)
    if service_provider and service_provider.status == 'pending':
        service_provider.status = 'rejected'  # Change status to rejected
        db.session.commit()
        flash(f'Service provider {username} rejected.', 'danger')
    else:
        flash('Service provider not found or already processed.', 'danger')

    return redirect(url_for('admin_dashboard'))

# Registration for Service Providers
@app.route('/register_Service_Provider', methods=['GET', 'POST'])
def registration_Service_Provider():
    if request.method == 'POST':
        Fullname = request.form['Fullname']
        username = request.form['username']
        password = request.form['password']
        service_name = request.form['service_name']
        experience = request.form['experience']
        address = request.form['address']
        pincode = request.form['pincode']
        document = request.files['document']
        hashed_password = generate_password_hash(password)

        if document and document.filename:
            document_name = document.filename
            document_data = document.read()  
        else:
            flash('Upload document', 'danger')
            return redirect(url_for('registration_Service_Provider'))
        result = Service.query.filter_by(name=service_name).first()
        if result:
            pass
        else:
            flash("This service is currently unavailable!!")
            return redirect(url_for('registration_Service_Provider'))
        new_service_provider = Service_provider(
            Fullname=Fullname,
            username=username,
            password=hashed_password,
            service_name=service_name,
            address=address,
            pincode=pincode,
            document_name=document_name,
            document_data=document_data,
            experience=experience,
            status='pending' 
        )
        db.session.add(new_service_provider)
        try:
            db.session.commit()
            flash(f'Service provider {username} registered successfully!', 'success')
            return redirect(url_for('home'))
        except Exception as e:
            db.session.rollback()
            flash('Username already exists. Please go to login_page', 'danger')
            return redirect(url_for('registration_Service_Provider'))
    return render_template('register_service_provider.html')
# User Registration
@app.route('/register_user', methods=['GET', 'POST'])
def user_registration():
    if request.method == 'POST':
        Fullname = request.form['Fullname']
        username = request.form['username']
        password = request.form['password']
        address = request.form['address']
        pincode = request.form['pincode']

        existing_user = User_registeration.query.filter_by(username=username).first()
        if existing_user:
            flash("User already exists. Please log in!", 'danger')
            return redirect(url_for('login'))

        hashed_password = generate_password_hash(password)
        new_user = User_registeration(
            Fullname=Fullname,
            username=username,
            password=hashed_password,
            address=address,
            pincode=pincode
        )

        db.session.add(new_user)
        try:
            db.session.commit()
            flash(f'User {username} registered successfully!', 'success')
            return redirect(url_for('home'))
        except Exception as e:
            db.session.rollback()
            flash('Username already exists. Please go to login_page', 'danger')
            return redirect(url_for('user_registration'))
    return render_template('register_user.html')
# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_type = request.form['user_type']
        print("here")
        
        if(BlockedUser.query.filter_by(username=username).first()):
            flash("You can not login!!")
            return redirect(url_for('home'))
        print(user_type)
        if (user_type == "admin"):
            if username =='Nitesh' and password=='Nitesh':
                admin=AdminUser()
                session['username'] = 'Nitesh'
                session['user_type'] = 'admin'
                login_user(admin)
                flash(f'Logged in successfully as {user_type}!', 'success')
                return redirect(url_for('admin_dashboard'))
            else:
                flash('Invalid creadentials','danger')
        elif(user_type=="Service_Provider"):
            service_provider=Service_provider.query.filter_by(username=username).first()
            if service_provider.status != 'approved':
                    flash('Your account is pending approval. Please wait for admin approval.', 'danger')
                    return redirect(url_for('home'))
            
            if service_provider and check_password_hash(service_provider.password,password):
                login_user(service_provider)
                session['username']=current_user.username
                session['user_type']="service_provider"
                flash(f'Logged in successfully as {user_type}! and as username {username}', 'success')
                return redirect(url_for('provider_requests'))
            else:
                flash('Invalid Password or username.Please try again.','danger')
                return redirect(url_for('home'))
        else:
             user_registration= User_registeration.query.filter_by(username=username).first()
             if user_registration and check_password_hash(user_registration.password, password):
            # Store username and user_type in session
                login_user(user_registration)
                session['username']=current_user.username
                session['user_type']="user"
                 # 'user' or 'service_provider'
                flash(f'Logged in successfully as {user_type}! and username as {username}', 'success')
                return redirect(url_for('home'))
             else:
                flash('Invalid username or password. Please try again.', 'danger')
        return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/service', methods=['POST', 'GET'])
@login_required
def service():
    items = Service_provider.query.all()
    return render_template('service.html', items=items)
# Request Service
@app.route('/request_service', methods=['POST', 'GET']) 
def request_service_view():
    if request.method == 'POST':
        print(f"Fullname: {request.form.get('Fullname')}")
        Fullname = request.form['Fullname']
        Service_required = request.form['Service_required']
        Description = request.form['Description']
        Provider_username=request.form['Provider_username']
        User_username=request.form['User_username']
        new_request=request_service(Fullname=Fullname,Service_required=Service_required,Description=Description,Provider_username=Provider_username,
                                    User_username=User_username)
        try:
            db.session.add(new_request)
            db.session.commit()
            flash("Service request submitted successfully!", "success")
            return redirect(url_for('home'))
        except Exception as e:
            print(f"Error: {e}")  # Log the error
            flash("An error occurred while submitting the request.", "danger")
            db.session.rollback()
            return redirect(url_for('request_service_view'))
    return render_template('request_service.html',current_user=current_user)
# End Service Request by User
@app.route('/end_request/<int:request_id>', methods=['POST'])
def end_request(request_id):
    service_request = request_service.query.get(request_id)
    if not service_request:
        flash("Service request not found", 'danger')
        return redirect(url_for('home'))
    # Ensure the logged-in user is the one who created the request
    if session.get('username') != service_request.Fullname:
        flash("You cannot end this request", 'danger')
        return redirect(url_for('home'))
    service_request.status = 'completed_by_user'
    db.session.commit()
    flash("Service request ended successfully", 'success')
    return redirect(url_for('home'))
# Provider Actions: Accept or Reject Request
@app.route('/provider_request_action/<int:request_id>', methods=['POST'])
def provider_request_action(request_id):
    service_request = request_service.query.get(request_id)
    action = request.form.get('action')

    # Ensure the logged-in user is a service provider
    if session.get('user_type') != 'service_provider':
        flash("You are not authorized to perform this action", 'danger')
        return redirect(url_for('provider_requests'))

    action = request.form.get('action')  # 'accept' or 'reject'

    if action == 'reject':
        service_request.status = 'rejected_by_provider'
        db.session.commit()
        flash("Service request rejected", 'danger')

    elif action == 'accept':
        service_request.status = 'accepted_by_provider'
        service_request.Service_provider_username = session.get('username')
        db.session.commit()
        flash("Service request accepted and will be completed by the provider", 'success')
    return redirect(url_for('provider_requests'))
# Provider Request List
@app.route('/provider_requests')
@login_required
def provider_requests():
    # Only service providers should access this route
    if session.get('user_type') == 'service_provider':
        # Get all service requests that are linked to the current provider
        service_requests = request_service.query.filter_by(Provider_username=session.get('username')).all()
        return render_template('provider_requests.html', requests=service_requests)
    else:
        flash("You are not authorized to view this page", 'danger')
        return redirect(url_for('home'))
# search-bar
@app.route('/search',methods=['GET','POST'])
@login_required
def search():
    query = request.form.get('query','').strip()
    if query:
        # Search in service providers
        service_providers = Service_provider.query.filter(
            (Service_provider.service_name.ilike(f"%{query}%")) | 
            (Service_provider.pincode.ilike(f"%{query}%")) |
            (Service_provider.Fullname.ilike(f"%{query}%")) |
            (Service_provider.address.ilike(f"%{query}%"))
        ).filter_by(status='approved').all()
        
        # Search in available services
        services = Service.query.filter(
            (Service.name.ilike(f"%{query}%")) |
            (Service.description.ilike(f"%{query}%"))
        ).all()
        
        # Search in rental items
        rental_items = RentalItem.query.filter(
            (RentalItem.name.ilike(f"%{query}%")) |
            (RentalItem.description.ilike(f"%{query}%")) |
            (RentalItem.category.ilike(f"%{query}%"))
        ).filter_by(is_available=True).all()
        
        # Get providers for these rental items to join them to search results
        for item in rental_items:
            if item.provider not in service_providers and item.provider.status == 'approved':
                if (item.provider.Fullname.lower().find(query.lower()) != -1 or
                    item.provider.service_name.lower().find(query.lower()) != -1):
                    service_providers.append(item.provider)
        
        return render_template('search_results.html', 
                              service_providers=service_providers,
                              services=services,
                              rental_items=rental_items,
                              query=query) 
    flash("Please enter a search term.", "warning")
    return redirect(url_for('home'))
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    item = request_service.query.get(id)
    if request.method == 'POST':
        new_description = request.form['description']
        item.Description = new_description  # Update the description
        db.session.commit()  # Commit changes to the database
        print("here")
        return redirect(url_for('home'))  # Redirect back to the index page with the updated table
    
    return render_template('edit_request.html', item=item) 
@app.route('/cancel_request/<int:id>', methods=['POST'])
def cancel_request(id):
    user = request_service.query.get(id)
    if user:
        # Update the status to 'Cancelled' (or whatever status you want)
        user.status = 'Cancelled_by_user'
        db.session.commit()
    
    # Redirect back to the user home or the relevant page
    return redirect(url_for('user_home')) 
@app.route('/complete_request/<int:id>', methods=['POST'])
def complete_request(id):
    user = request_service.query.get(id)
    if user:
        # Update the status to 'completed_by_provider'
        user.status = 'completed_by_provider'
        db.session.commit()  # Save the changes to the database

        flash('Request marked as completed by provider.', 'success')
    else:
        flash('Request not found.', 'danger')

    # Redirect back to the appropriate page (e.g., user home or provider requests)
    return redirect(url_for('home')) 
@app.route('/edit_services/<int:id>', methods=['GET', 'POST'])
def edit_service(id):
    service = Service.query.get_or_404(id)

    if request.method == 'POST':
        # Get the form data
        service.name = request.form['name']
        service.description = request.form['description']
        service.price = request.form['price']
        
        # Commit changes to the database
        try:
            db.session.commit()
            flash('Service updated successfully!', 'success')
            return redirect(url_for('admin_dashboard'))
        except:
            db.session.rollback()
            flash('Error updating service. Please try again.', 'danger')

    return render_template('edit_services.html', service=service)
@app.route('/delete_service/<int:id>', methods=['GET'])
def delete_service(id):
    service = Service.query.get_or_404(id)

    try:
        db.session.delete(service)
        db.session.commit()
        flash('Service deleted successfully!', 'success')
    except:
        db.session.rollback()
        flash('Error deleting service. Please try again.', 'danger')
    
    return redirect(url_for('admin_dashboard'))
# API endpoint to get provider info for maps
@app.route('/provider_info/<username>')
@login_required
def provider_info(username):
    provider = Service_provider.query.filter_by(username=username).first()
    if provider:
        return {
            'username': provider.username,
            'Fullname': provider.Fullname,
            'service_name': provider.service_name,
            'address': provider.address,
            'pincode': provider.pincode,
            'experience': provider.experience
        }
    return {'error': 'Provider not found'}, 404

# Route to view all reviews for a service provider
@app.route('/provider/<username>/reviews')
def provider_reviews(username):
    provider = Service_provider.query.filter_by(username=username).first_or_404()
    reviews = Review.query.filter_by(service_provider_username=username).order_by(Review.created_at.desc()).all()
    
    # Calculate average rating
    avg_rating = 0
    if reviews:
        total = sum(review.rating for review in reviews)
        avg_rating = round(total / len(reviews), 1)
    
    return render_template('provider_reviews.html', 
                           provider=provider, 
                           reviews=reviews, 
                           avg_rating=avg_rating)

# Route to add a new review
@app.route('/add_review/<provider_username>', methods=['GET', 'POST'])
@login_required
def add_review(provider_username):
    if session.get('user_type') != 'user':
        flash('Only users can submit reviews.', 'warning')
        return redirect(url_for('home'))
    
    provider = Service_provider.query.filter_by(username=provider_username).first_or_404()
    
    # Check if user has completed a service with this provider
    completed_requests = request_service.query.filter_by(
        User_username=session.get('username'),
        Provider_username=provider_username,
        status='completed_by_provider'
    ).all()
    
    if not completed_requests:
        flash('You can only review service providers after completing a service with them.', 'warning')
        return redirect(url_for('service'))
    
    # Check if user has already reviewed this provider
    existing_review = Review.query.filter_by(
        service_provider_username=provider_username,
        user_username=session.get('username')
    ).first()
    
    if existing_review:
        flash('You have already reviewed this service provider. You can edit your review instead.', 'info')
        return redirect(url_for('edit_review', review_id=existing_review.id))
    
    if request.method == 'POST':
        rating = int(request.form.get('rating'))
        comment = request.form.get('comment')
        
        if not 1 <= rating <= 5:
            flash('Rating must be between 1 and 5.', 'danger')
            return redirect(url_for('add_review', provider_username=provider_username))
        
        new_review = Review(
            rating=rating,
            comment=comment,
            service_provider_username=provider_username,
            user_username=session.get('username')
        )
        
        try:
            db.session.add(new_review)
            db.session.commit()
            flash('Your review has been submitted successfully!', 'success')
            return redirect(url_for('provider_reviews', username=provider_username))
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {str(e)}', 'danger')
    
    return render_template('add_review.html', provider=provider)

# Route to edit an existing review
@app.route('/edit_review/<int:review_id>', methods=['GET', 'POST'])
@login_required
def edit_review(review_id):
    review = Review.query.get_or_404(review_id)
    
    # Ensure the logged-in user is the one who created the review
    if session.get('username') != review.user_username:
        flash('You can only edit your own reviews.', 'danger')
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        rating = int(request.form.get('rating'))
        comment = request.form.get('comment')
        
        if not 1 <= rating <= 5:
            flash('Rating must be between 1 and 5.', 'danger')
            return redirect(url_for('edit_review', review_id=review_id))
        
        review.rating = rating
        review.comment = comment
        review.created_at = datetime.utcnow()
        
        try:
            db.session.commit()
            flash('Your review has been updated!', 'success')
            return redirect(url_for('provider_reviews', username=review.service_provider_username))
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {str(e)}', 'danger')
    
    return render_template('edit_review.html', review=review)

# Route to delete a review
@app.route('/delete_review/<int:review_id>', methods=['POST'])
@login_required
def delete_review(review_id):
    review = Review.query.get_or_404(review_id)
    provider_username = review.service_provider_username
    
    # Ensure the logged-in user is the one who created the review
    if session.get('username') != review.user_username:
        flash('You can only delete your own reviews.', 'danger')
        return redirect(url_for('home'))
    
    try:
        db.session.delete(review)
        db.session.commit()
        flash('Your review has been deleted.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred: {str(e)}', 'danger')
    
    return redirect(url_for('provider_reviews', username=provider_username))

# Service Provider Dashboard
@app.route('/provider_dashboard')
@login_required
def provider_dashboard():
    if session.get('user_type') != 'service_provider':
        flash("You are not authorized to view this page", 'danger')
        return redirect(url_for('home'))
    
    # Get the current provider username
    provider_username = session.get('username')
    provider = Service_provider.query.get(provider_username)
    
    # Get all service requests for this provider
    all_requests = request_service.query.filter_by(Provider_username=provider_username).all()
    
    # Calculate statistics
    total_requests = len(all_requests)
    completed_requests = sum(1 for req in all_requests if req.status == 'completed_by_provider')
    pending_requests = sum(1 for req in all_requests if req.status == 'pending')
    accepted_requests = sum(1 for req in all_requests if req.status == 'accepted_by_provider')
    rejected_requests = sum(1 for req in all_requests if req.status == 'rejected_by_provider')
    cancelled_requests = sum(1 for req in all_requests if req.status == 'Cancelled_by_user')
    
    # Calculate completion rate
    completion_rate = 0
    if total_requests > 0:
        completion_rate = round((completed_requests / total_requests) * 100)
    
    # Get recent requests (last 5)
    recent_requests = request_service.query.filter_by(Provider_username=provider_username).order_by(request_service.id.desc()).limit(5).all()
    
    # Get ratings and reviews
    reviews = Review.query.filter_by(service_provider_username=provider_username).order_by(Review.created_at.desc()).all()
    avg_rating = 0
    if reviews:
        avg_rating = round(sum(review.rating for review in reviews) / len(reviews), 1)
    
    # Get all time periods
    current_month = datetime.now().month
    current_year = datetime.now().year
    
    # Get monthly data for chart (if we had request dates)
    # For now, we'll use placeholder data
    monthly_data = {
        'January': 0,
        'February': 0,
        'March': 0,
        'April': 0,
        'May': 0,
        'June': 0,
        'July': 0,
        'August': 0,
        'September': 0,
        'October': 0,
        'November': 0,
        'December': 0,
    }
    
    return render_template('provider_dashboard.html',
                          provider=provider,
                          total_requests=total_requests,
                          completed_requests=completed_requests,
                          pending_requests=pending_requests,
                          accepted_requests=accepted_requests,
                          rejected_requests=rejected_requests,
                          cancelled_requests=cancelled_requests,
                          completion_rate=completion_rate,
                          recent_requests=recent_requests,
                          reviews=reviews,
                          avg_rating=avg_rating,
                          monthly_data=monthly_data)

# Logout
@app.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out', 'success')
    return redirect(url_for('home'))

# =============== RENTAL FEATURE ROUTES =============== #

# Route for users to browse rental items
@app.route('/rentals')
@login_required
def browse_rentals():
    category = request.args.get('category')
    
    if category:
        items = RentalItem.query.filter_by(category=category, is_available=True).all()
    else:
        items = RentalItem.query.filter_by(is_available=True).all()
    
    # Get unique categories for filter
    categories = db.session.query(RentalItem.category).distinct().all()
    categories = [c[0] for c in categories if c[0]]  # Remove None values
    
    return render_template('rental_browse.html', 
                          items=items, 
                          categories=categories,
                          selected_category=category)

# Route to view a specific rental item
@app.route('/rental-item/<int:item_id>')
@login_required
def view_rental_item(item_id):
    item = RentalItem.query.get_or_404(item_id)
    
    # Calculate next available date if item is not available
    next_available_date = datetime.utcnow()
    if not item.is_available:
        # Find the latest end date among approved rental requests
        latest_rental = RentalRequest.query.filter_by(
            item_id=item_id, 
            status='approved'
        ).order_by(RentalRequest.end_date.desc()).first()
        
        if latest_rental:
            next_available_date = latest_rental.end_date + datetime.timedelta(days=1)
    
    return render_template('rental_item.html', 
                          item=item, 
                          next_available_date=next_available_date,
                          datetime=datetime)

# Route to request a rental
@app.route('/request-rental/<int:item_id>', methods=['GET', 'POST'])
@login_required
def request_rental(item_id):
    if session.get('user_type') != 'user':
        flash('Only users can request rentals.', 'warning')
        return redirect(url_for('browse_rentals'))
    
    item = RentalItem.query.get_or_404(item_id)
    
    if not item.is_available:
        flash('This item is currently not available for rent.', 'warning')
        return redirect(url_for('view_rental_item', item_id=item_id))
    
    if request.method == 'POST':
        start_date_str = request.form.get('start_date')
        end_date_str = request.form.get('end_date')
        
        if not start_date_str or not end_date_str:
            flash('Please select both start and end dates.', 'danger')
            return redirect(url_for('request_rental', item_id=item_id))
        
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        
        # Validate dates
        if start_date < datetime.now().replace(hour=0, minute=0, second=0, microsecond=0):
            flash('Start date cannot be in the past.', 'danger')
            return redirect(url_for('request_rental', item_id=item_id))
        
        if end_date <= start_date:
            flash('End date must be after start date.', 'danger')
            return redirect(url_for('request_rental', item_id=item_id))
        
        # Check if item is already booked for these dates
        conflicting_rentals = RentalRequest.query.filter(
            RentalRequest.item_id == item_id,
            RentalRequest.status == 'approved',
            RentalRequest.start_date <= end_date,
            RentalRequest.end_date >= start_date
        ).all()
        
        if conflicting_rentals:
            flash('This item is not available for the selected dates.', 'danger')
            return redirect(url_for('request_rental', item_id=item_id))
        
        # Calculate total price
        days = (end_date - start_date).days
        if days < 1:
            days = 1
        total_price = days * item.daily_rate
        
        # Create rental request
        rental_request = RentalRequest(
            item_id=item_id,
            user_username=session.get('username'),
            start_date=start_date,
            end_date=end_date,
            total_price=total_price,
            status='pending'
        )
        
        try:
            db.session.add(rental_request)
            db.session.commit()
            flash('Your rental request has been submitted successfully!', 'success')
            return redirect(url_for('user_rentals'))
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {str(e)}', 'danger')
    
    return render_template('rental_request_form.html', 
                          item=item,
                          datetime=datetime)

# Route for users to view their rental requests
@app.route('/my-rentals')
@login_required
def user_rentals():
    if session.get('user_type') != 'user':
        flash('Only users can access rental requests.', 'warning')
        return redirect(url_for('home'))
    
    rental_requests = RentalRequest.query.filter_by(
        user_username=session.get('username')
    ).order_by(RentalRequest.created_at.desc()).all()
    
    return render_template('user_rentals.html', 
                          rental_requests=rental_requests,
                          current_date=datetime.utcnow().date())

# Route for users to cancel a rental request
@app.route('/cancel-rental-request/<int:request_id>', methods=['POST'])
@login_required
def cancel_rental_request(request_id):
    if session.get('user_type') != 'user':
        flash('Only users can cancel rental requests.', 'warning')
        return redirect(url_for('home'))
    
    rental_request = RentalRequest.query.get_or_404(request_id)
    
    # Verify ownership
    if rental_request.user_username != session.get('username'):
        flash('You can only cancel your own rental requests.', 'danger')
        return redirect(url_for('user_rentals'))
    
    # Can only cancel pending or approved (future) rentals
    if rental_request.status not in ['pending', 'approved']:
        flash('You cannot cancel this rental request.', 'danger')
        return redirect(url_for('user_rentals'))
    
    # For approved rentals, check if start date is in the future
    # Fix: Convert both to date objects before comparing
    if rental_request.status == 'approved' and rental_request.start_date.date() <= datetime.utcnow().date():
        flash('You cannot cancel an active rental. Please contact the provider.', 'danger')
        return redirect(url_for('user_rentals'))
    
    rental_request.status = 'cancelled'
    
    try:
        db.session.commit()
        
        # If the request was approved, make the item available again
        if rental_request.status == 'approved':
            item = RentalItem.query.get(rental_request.item_id)
            item.is_available = True
            db.session.commit()
        
        flash('Your rental request has been cancelled.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred: {str(e)}', 'danger')
    
    return redirect(url_for('user_rentals'))

# Routes for service providers to manage their rental items
@app.route('/provider/rental-items', methods=['GET', 'POST'])
@login_required
def provider_rental_items():
    if session.get('user_type') != 'service_provider':
        flash('Only service providers can manage rental items.', 'warning')
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        # Add new rental item
        name = request.form.get('name')
        description = request.form.get('description')
        daily_rate = float(request.form.get('daily_rate'))
        category = request.form.get('category')
        image = request.files.get('image')
        
        if not name or not daily_rate:
            flash('Name and daily rate are required.', 'danger')
            return redirect(url_for('provider_rental_items'))
        
        image_name = None
        if image and image.filename:
            # Generate a unique filename to avoid collisions
            _, ext = os.path.splitext(image.filename)
            image_name = f"{session.get('username')}_{int(time.time())}{ext}"
            image_path = os.path.join('static/rental_images', image_name)
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(image_path), exist_ok=True)
            
            # Save the image
            image.save(image_path)
        
        new_item = RentalItem(
            name=name,
            description=description,
            daily_rate=daily_rate,
            category=category,
            image_name=image_name,
            is_available=True,
            provider_username=session.get('username')
        )
        
        try:
            db.session.add(new_item)
            db.session.commit()
            flash('Your rental item has been added successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {str(e)}', 'danger')
    
    # Get all items for this provider
    items = RentalItem.query.filter_by(
        provider_username=session.get('username')
    ).order_by(RentalItem.id.desc()).all()
    
    return render_template('provider_rental_items.html', items=items)

# Route to edit a rental item
@app.route('/edit-rental-item/<int:item_id>', methods=['POST'])
@login_required
def edit_rental_item(item_id):
    if session.get('user_type') != 'service_provider':
        flash('Only service providers can edit rental items.', 'warning')
        return redirect(url_for('home'))
    
    item = RentalItem.query.get_or_404(item_id)
    
    # Verify ownership
    if item.provider_username != session.get('username'):
        flash('You can only edit your own rental items.', 'danger')
        return redirect(url_for('provider_rental_items'))
    
    # Update item details
    item.name = request.form.get('name')
    item.description = request.form.get('description')
    item.daily_rate = float(request.form.get('daily_rate'))
    item.category = request.form.get('category')
    
    try:
        db.session.commit()
        flash('Rental item updated successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred: {str(e)}', 'danger')
    
    return redirect(url_for('provider_rental_items'))

# Route to delete a rental item
@app.route('/delete-rental-item/<int:item_id>', methods=['POST'])
@login_required
def delete_rental_item(item_id):
    if session.get('user_type') != 'service_provider':
        flash('Only service providers can delete rental items.', 'warning')
        return redirect(url_for('home'))
    
    item = RentalItem.query.get_or_404(item_id)
    
    # Verify ownership
    if item.provider_username != session.get('username'):
        flash('You can only delete your own rental items.', 'danger')
        return redirect(url_for('provider_rental_items'))
    
    # Check if item has active rentals
    # Fix: Convert both to date objects before comparing
    active_rentals = RentalRequest.query.filter(
        RentalRequest.item_id == item_id,
        RentalRequest.status == 'approved',
        RentalRequest.end_date.date() >= datetime.utcnow().date()
    ).first()
    
    if active_rentals:
        flash('You cannot delete an item with active rentals.', 'danger')
        return redirect(url_for('provider_rental_items'))
    
    try:
        # Delete the item's image if it exists
        if item.image_name:
            image_path = os.path.join('static/rental_images', item.image_name)
            if os.path.exists(image_path):
                os.remove(image_path)
        
        db.session.delete(item)
        db.session.commit()
        flash('Rental item deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred: {str(e)}', 'danger')
    
    return redirect(url_for('provider_rental_items'))

# Route to update item availability
@app.route('/rental-item/<int:item_id>/availability', methods=['POST'])
@login_required
def update_item_availability(item_id):
    if session.get('user_type') != 'service_provider':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    item = RentalItem.query.get_or_404(item_id)
    
    # Verify ownership
    if item.provider_username != session.get('username'):
        return jsonify({'success': False, 'message': 'You can only update your own items'}), 403
    
    # Check if item has active rentals
    # Fix: Convert both to date objects before comparing
    active_rentals = RentalRequest.query.filter(
        RentalRequest.item_id == item_id,
        RentalRequest.status == 'approved',
        RentalRequest.end_date.date() >= datetime.utcnow().date()
    ).first()
    
    data = request.get_json()
    is_available = data.get('is_available', False)
    
    if active_rentals and not is_available:
        return jsonify({
            'success': False, 
            'message': 'Cannot mark as unavailable: Item has active rentals'
        }), 400
    
    item.is_available = is_available
    
    try:
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

# Route for providers to manage rental requests
@app.route('/provider/rental-requests')
@login_required
def provider_rental_requests():
    if session.get('user_type') != 'service_provider':
        flash('Only service providers can access this page.', 'warning')
        return redirect(url_for('home'))
    
    # Get all items for this provider
    provider_items = RentalItem.query.filter_by(
        provider_username=session.get('username')
    ).all()
    
    item_ids = [item.id for item in provider_items]
    
    # Get all rental requests for these items
    rental_requests = RentalRequest.query.filter(
        RentalRequest.item_id.in_(item_ids)
    ).order_by(RentalRequest.created_at.desc()).all()
    
    return render_template('provider_rental_requests.html', 
                          rental_requests=rental_requests,
                          current_date=datetime.utcnow().date())

# Route to approve a rental request
@app.route('/approve-rental-request/<int:request_id>', methods=['POST'])
@login_required
def approve_rental_request(request_id):
    if session.get('user_type') != 'service_provider':
        flash('Only service providers can approve rental requests.', 'warning')
        return redirect(url_for('home'))
    
    rental_request = RentalRequest.query.get_or_404(request_id)
    
    # Verify ownership of the item
    item = RentalItem.query.get(rental_request.item_id)
    if item.provider_username != session.get('username'):
        flash('You can only approve requests for your own items.', 'danger')
        return redirect(url_for('provider_rental_requests'))
    
    # Check if request is pending
    if rental_request.status != 'pending':
        flash('You can only approve pending requests.', 'danger')
        return redirect(url_for('provider_rental_requests'))
    
    # Check for date conflicts with other approved rentals
    conflicting_rentals = RentalRequest.query.filter(
        RentalRequest.item_id == rental_request.item_id,
        RentalRequest.id != rental_request.id,
        RentalRequest.status == 'approved',
        RentalRequest.start_date <= rental_request.end_date,
        RentalRequest.end_date >= rental_request.start_date
    ).all()
    
    if conflicting_rentals:
        flash('Cannot approve: Dates conflict with an existing approved rental.', 'danger')
        return redirect(url_for('provider_rental_requests'))
    
    # Approve the request
    rental_request.status = 'approved'
    
    # If the rental starts today or earlier, mark the item as unavailable
    # Fix: Convert both to date objects before comparing
    if rental_request.start_date.date() <= datetime.utcnow().date():
        item.is_available = False
    
    try:
        db.session.commit()
        flash('Rental request approved successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred: {str(e)}', 'danger')
    
    return redirect(url_for('provider_rental_requests'))

# Route to reject a rental request
@app.route('/reject-rental-request/<int:request_id>', methods=['POST'])
@login_required
def reject_rental_request(request_id):
    if session.get('user_type') != 'service_provider':
        flash('Only service providers can reject rental requests.', 'warning')
        return redirect(url_for('home'))
    
    rental_request = RentalRequest.query.get_or_404(request_id)
    
    # Verify ownership of the item
    item = RentalItem.query.get(rental_request.item_id)
    if item.provider_username != session.get('username'):
        flash('You can only reject requests for your own items.', 'danger')
        return redirect(url_for('provider_rental_requests'))
    
    # Check if request is pending
    if rental_request.status != 'pending':
        flash('You can only reject pending requests.', 'danger')
        return redirect(url_for('provider_rental_requests'))
    
    # Reject the request
    rental_request.status = 'rejected'
    
    try:
        db.session.commit()
        flash('Rental request rejected.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred: {str(e)}', 'danger')
    
    return redirect(url_for('provider_rental_requests'))

# Route to mark a rental as completed
@app.route('/complete-rental/<int:request_id>', methods=['POST'])
@login_required
def complete_rental(request_id):
    if session.get('user_type') != 'service_provider':
        flash('Only service providers can complete rentals.', 'warning')
        return redirect(url_for('home'))
    
    rental_request = RentalRequest.query.get_or_404(request_id)
    
    # Verify ownership of the item
    item = RentalItem.query.get(rental_request.item_id)
    if item.provider_username != session.get('username'):
        flash('You can only complete rentals for your own items.', 'danger')
        return redirect(url_for('provider_rental_requests'))
    
    # Check if request is approved
    if rental_request.status != 'approved':
        flash('You can only complete approved rentals.', 'danger')
        return redirect(url_for('provider_rental_requests'))
    
    # Mark as completed and make item available again
    rental_request.status = 'completed'
    item.is_available = True
    
    try:
        db.session.commit()
        flash('Rental marked as completed.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'An error occurred: {str(e)}', 'danger')
    
    return redirect(url_for('provider_rental_requests'))

if __name__ == '__main__':
    app.run(debug=True)
