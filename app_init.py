import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv
from werkzeug.middleware.proxy_fix import ProxyFix

# Cargar variables de entorno (.env para desarrollo local)
load_dotenv()

# Configurar logging básico
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Inicializar extensiones (sin aplicación todavía)
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
csrf = CSRFProtect()

def create_app():
    app = Flask(__name__, static_folder='static')

    # Soporte para proxies inversos (Heroku)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

    # Configuración de claves y base de datos
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'supersecretflaskskey')

    database_url = os.environ.get('DATABASE_URL', 'sqlite:///perfilesbalt.db')
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)

    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Configuración visual del sitio
    def get_logo_url():
        logo_path = os.path.join(app.root_path, 'static', 'logo.png')
        if os.path.exists(logo_path) and os.stat(logo_path).st_size > 0:
            return '/static/logo.png'
        return 'https://placehold.co/300x300?text=logo'

    app.config['LOGO_URL'] = get_logo_url()
    app.config['THEME'] = os.environ.get('APP_THEME', 'lofi')
    app.config['APP_TITLE'] = os.environ.get('APP_TITLE', 'Perfiles Balt')

    # Filtro personalizado: convierte saltos de línea en <br>
    @app.template_filter('nl2br')
    def nl2br_filter(s):
        if s is None:
            return ''
        return s.replace('\n', '<br>')

    # Inicializar extensiones con la app
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    migrate.init_app(app, db)
    
    login_manager.login_view = 'auth.login'

    # Variables globales para los templates
    @app.context_processor
    def inject_globals():
        return dict(
            theme=app.config['THEME'],
            app_title=app.config['APP_TITLE'],
            logo_url=app.config['LOGO_URL']
        )

    # Registro de blueprints
    with app.app_context():
        from routes import main_bp, auth_bp, admin_bp
        app.register_blueprint(main_bp)
        app.register_blueprint(auth_bp)
        app.register_blueprint(admin_bp)

    return app
