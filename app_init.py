import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Inicializar extensiones
db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__, static_folder='static')

    # Configuración desde variables de entorno o valores por defecto
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'supersecretflaskskey')

    # Configuración de la base de datos
    database_url = os.environ.get('DATABASE_URL', 'sqlite:///perfilesbalt.db')

    # Heroku cambia 'postgres://' a 'postgresql://' en SQLAlchemy 1.4+
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)

    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Configuración del logo
    def get_logo_url():
        custom_logo_path = os.path.join(app.root_path, 'static', 'logo.png')
        if os.path.exists(custom_logo_path):
            # Check if file is not empty
            if os.stat(custom_logo_path).st_size > 0:
                return '/static/logo.png'
        return 'https://placehold.co/300x300?text=logo'

    app.config['LOGO_URL'] = get_logo_url()

    # Set default theme
    app.config['THEME'] = os.environ.get('APP_THEME', 'lofi')

    # Set default app title
    app.config['APP_TITLE'] = os.environ.get('APP_TITLE', 'Perfiles Balt')

    # Registrar filtros Jinja2
    @app.template_filter('nl2br')
    def nl2br_filter(s):
        if s is None:
            return ""
        return s.replace('\n', '<br>')

    # Inicializar extensiones con la aplicación
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    # Context processor to inject theme and app title into all templates
    @app.context_processor
    def inject_theme_and_title():
        return dict(
            theme=app.config['THEME'],
            app_title=app.config['APP_TITLE'],
            logo_url=app.config['LOGO_URL']
        )

    # Registrar blueprints
    with app.app_context():
        from routes import main_bp, auth_bp, admin_bp
        app.register_blueprint(main_bp)
        app.register_blueprint(auth_bp)
        app.register_blueprint(admin_bp)

    return app
