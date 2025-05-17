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

    # Configuración general
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'supersecretflaskskey')

    # Leer DATABASE_URL desde .env o Heroku
    database_url = os.environ.get('DATABASE_URL', 'sqlite:///perfilesbalt.db')

    # Heroku usa postgres://, SQLAlchemy requiere postgresql://
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)

    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Configuración de logo
    def get_logo_url():
        custom_logo_path = os.path.join(app.root_path, 'static', 'logo.png')
        if os.path.exists(custom_logo_path) and os.stat(custom_logo_path).st_size > 0:
            return '/static/logo.png'
        return 'https://placehold.co/300x300?text=logo'

    app.config['LOGO_URL'] = get_logo_url()
    app.config['THEME'] = os.environ.get('APP_THEME', 'lofi')
    app.config['APP_TITLE'] = os.environ.get('APP_TITLE', 'Perfiles Balt')

    # Filtro personalizado
    @app.template_filter('nl2br')
    def nl2br_filter(s):
        if s is None:
            return ""
        return s.replace('\n', '<br>')

    # Inicializar extensiones
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    # Variables globales para templates
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
