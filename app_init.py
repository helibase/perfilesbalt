import os
import logging
from flask import Flask
from sqlalchemy.engine import Engine
from sqlalchemy import event
from abilities import apply_sqlite_migrations
from models import db
 
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

app = Flask(__name__, static_folder='static')

import os

# Set Flask secret key
app.config['SECRET_KEY'] = 'supersecretflaskskey'

def get_logo_url():
    custom_logo_path = os.path.join(app.root_path, 'static', 'logo.png')
    if os.path.exists(custom_logo_path):
        # Check if file is not empty
        if os.stat(custom_logo_path).st_size > 0:
            return '/static/logo.png'
    return 'https://placehold.co/300x300?text=logo'

app.config['LOGO_URL'] = get_logo_url()

# Set default theme
app.config['THEME'] = 'lofi'

# Initialize database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///your_database.db'
db.init_app(app)

# Set default app title
app.config['APP_TITLE'] = 'My App'

# Context processor to inject theme and app title into all templates
@app.context_processor
def inject_theme_and_title():
    return dict(theme=app.config['THEME'], app_title=app.config['APP_TITLE'])

# Apply database migrations
with app.app_context():
    apply_sqlite_migrations(db.engine, db.Model, 'migrations')
