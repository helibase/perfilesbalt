from app_init import app, db
from flask import render_template, request, jsonify, redirect, url_for, session
from models import ContactMessage, AdminUser, NewsletterSubscription
import re
from abilities import flask_app_authenticator
import logging

logger = logging.getLogger(__name__)

# Apply authentication to all routes except home and API endpoints
@app.before_request
def auth_check():
    public_endpoints = ['home_route', 'static', 'contact', 'newsletter_subscribe', 'admin_login']
    if request.endpoint not in public_endpoints and not request.path.startswith('/static/'):
        # Ensure API routes are public
        if request.path.startswith('/api/'):
            return None
        return flask_app_authenticator(allowed_users=['admin@example.com'])()

@app.route("/")
def home_route():
    return render_template("home.html")

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        admin_user = AdminUser.query.filter_by(username=username).first()
        
        logger.info(f"Login attempt for username: {username}")
        
        if admin_user:
            logger.info("User found, checking password")
            logger.debug(f"Stored hash: {admin_user.password_hash}")
            logger.debug(f"Provided password: {password}")
            
            try:
                if admin_user.check_password(password):
                    session['admin_logged_in'] = True
                    logger.info("Login successful")
                    return redirect(url_for('admin_dashboard'))
                else:
                    logger.warning("Invalid password")
                    logger.warning(f"Password verification failed for user: {username}")
                    return render_template("admin_login.html", error="Invalid credentials")
            except Exception as e:
                logger.error(f"Authentication error: {str(e)}")
                return render_template("admin_login.html", error="Authentication system error")
        else:
            logger.warning(f"User not found: {username}")
            return render_template("admin_login.html", error="Invalid credentials")
    
    return render_template("admin_login.html")

@app.route("/admin/dashboard")
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    contact_messages = ContactMessage.query.order_by(ContactMessage.created_at.desc()).all()
    newsletter_emails = NewsletterSubscription.query.order_by(NewsletterSubscription.created_at.desc()).all()
    
    return render_template("admin_dashboard.html", 
                           contact_messages=contact_messages, 
                           newsletter_emails=newsletter_emails)

@app.route("/admin/delete_message/<int:message_id>", methods=["POST"])
def delete_message(message_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    message = ContactMessage.query.get_or_404(message_id)
    db.session.delete(message)
    db.session.commit()
    
    return redirect(url_for('admin_dashboard'))

@app.route("/admin/logout")
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('home_route'))

@app.route("/api/contact", methods=["POST"])
def contact():
    logger.info("Contact form submission received")
    try:
        data = request.get_json()
        logger.debug(f"Received contact form data: {data}")
    except Exception as e:
        logger.error(f"Error parsing JSON: {str(e)}")
        return jsonify({"error": "Invalid JSON payload"}), 400
    
    # Validate required fields
    required_fields = ['name', 'email', 'subject', 'message']
    for field in required_fields:
        if not data.get(field):
            logger.warning(f"Missing required field: {field}")
            return jsonify({"error": f"{field.capitalize()} is required"}), 400
    
    # Validate email format
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_regex, data['email']):
        logger.warning(f"Invalid email format: {data['email']}")
        return jsonify({"error": "Invalid email format"}), 400
    
    # Validate message length
    if len(data['message']) < 10:
        logger.warning("Message too short")
        return jsonify({"error": "Message must be at least 10 characters long"}), 400
    
    try:
        # Create new contact message
        contact_message = ContactMessage(
            name=data['name'],
            email=data['email'],
            subject=data['subject'],
            message=data['message']
        )
        
        # Save to database
        db.session.add(contact_message)
        db.session.commit()
        logger.info(f"Contact message saved successfully for {data['email']}")
        
        return jsonify({"message": "Message sent successfully"}), 200
        
    except Exception as e:
        logger.error(f"Error saving contact message: {str(e)}")
        db.session.rollback()
        return jsonify({"error": "An error occurred while saving your message"}), 500

@app.route("/api/newsletter", methods=["POST"])
def newsletter_subscribe():
    logger.info("Newsletter subscription received")
    try:
        data = request.get_json()
        logger.debug(f"Received newsletter data: {data}")
    except Exception as e:
        logger.error(f"Error parsing JSON: {str(e)}")
        return jsonify({"error": "Invalid JSON payload"}), 400
    
    if not data or not data.get('email'):
        logger.warning("Missing email in newsletter subscription")
        return jsonify({"error": "Email is required"}), 400
    
    email = data['email']
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(email_regex, email):
        logger.warning(f"Invalid email format in newsletter: {email}")
        return jsonify({"error": "Invalid email format"}), 400
    
    try:
        # Check if email already exists
        existing_subscription = NewsletterSubscription.query.filter_by(email=email).first()
        if existing_subscription:
            logger.info(f"Email already subscribed: {email}")
            return jsonify({"message": "You are already subscribed!"}), 200
        
        # Create new subscription
        subscription = NewsletterSubscription(email=email)
        db.session.add(subscription)
        db.session.commit()
        logger.info(f"Newsletter subscription saved for {email}")
        
        return jsonify({"message": "Successfully subscribed to newsletter!"}), 200
        
    except Exception as e:
        logger.error(f"Error saving newsletter subscription: {str(e)}")
        db.session.rollback()
        return jsonify({"error": "An error occurred while subscribing"}), 500