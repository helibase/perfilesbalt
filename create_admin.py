from app_init import create_app, db
from models import AdminUser
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

app = create_app()

with app.app_context():
    # Verificar si el usuario admin ya existe
    admin = AdminUser.query.filter_by(username='admin').first()

    if admin:
        print("El usuario admin ya existe. Actualizando contraseña...")
        admin.set_password('admin123')
    else:
        print("Creando nuevo usuario admin...")
        admin = AdminUser(
            username='admin',
            email='admin@example.com'
        )
        admin.set_password('admin123')
        db.session.add(admin)

    db.session.commit()
    print("Usuario admin creado/actualizado con éxito.")
