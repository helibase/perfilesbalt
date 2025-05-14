import os
import logging
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

db = SQLAlchemy()

class ContactMessage(db.Model):
    __tablename__ = 'contact_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    subject = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    
    def __repr__(self):
        return f'<ContactMessage {self.email}>'

class AdminUser(db.Model):
    __tablename__ = 'admin_users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')
    
    def check_password(self, password):
        import logging
        import binascii
        logger = logging.getLogger(__name__)
        
        logger.debug(f"Stored password hash: {self.password_hash}")
        logger.debug(f"Attempting to verify password: {password}")
        
        try:
            result = check_password_hash(self.password_hash, password)
            
            logger.debug(f"Password verification result: {result}")
            
            # Additional detailed logging
            stored_hash_parts = self.password_hash.split('$')
            logger.debug(f"Stored hash parts: {stored_hash_parts}")
            
            # Log hash details
            if len(stored_hash_parts) >= 3:
                salt = stored_hash_parts[2]
                logger.debug(f"Salt used: {salt}")
            
            return result
        except Exception as e:
            logger.error(f"Error during password verification: {str(e)}")
            return False

class NewsletterSubscription(db.Model):
    __tablename__ = 'newsletter_subscriptions'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    
    def __repr__(self):
        return f'<NewsletterSubscription {self.email}>'
