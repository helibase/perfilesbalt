from app_init import create_app, db, login_manager
import os
from dotenv import load_dotenv
from abilities import ensure_database_exists, apply_migrations
import logging
from models import AdminUser

# Cargar variables de entorno desde .env
load_dotenv()

# Crear la aplicación
app = create_app()

# Configurar login manager
@login_manager.user_loader
def load_user(user_id):
    return AdminUser.query.get(int(user_id))

# Asegurar que la base de datos existe y aplicar migraciones
with app.app_context():
    try:
        # Asegurar que la base de datos existe
        db_url = app.config['SQLALCHEMY_DATABASE_URI']
        ensure_database_exists(db_url)

        # Crear todas las tablas definidas en los modelos
        db.create_all()

        # Aplicar migraciones SQL
        apply_migrations(db_url, 'migrations')

        # Crear usuario admin por defecto si no existe
        admin = AdminUser.query.filter_by(username='admin').first()
        if not admin:
            logging.info("Creando usuario admin por defecto")
            admin = AdminUser(
                username='admin',
                email='admin@example.com'
            )
            admin.set_password('admin123')  # Cambiar en producción
            db.session.add(admin)
            db.session.commit()
            logging.info("Usuario admin creado")
    except Exception as e:
        logging.error(f"Error al inicializar la base de datos: {str(e)}")

if __name__ == '__main__':
    debug = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=debug, host='0.0.0.0', port=port)
