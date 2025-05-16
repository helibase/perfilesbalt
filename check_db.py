import os
from dotenv import load_dotenv
import psycopg2

# Cargar variables de entorno
load_dotenv()

# Obtener la URL de la base de datos
db_url = os.environ.get('DATABASE_URL')
print(f"URL de la base de datos: {db_url}")

try:
    # Extraer los componentes de la URL
    # Formato: postgresql://usuario:contraseña@host/nombre_db
    parts = db_url.replace('postgresql://', '').split('@')
    user_pass = parts[0].split(':')
    host_db = parts[1].split('/')

    user = user_pass[0]
    password = user_pass[1]
    host = host_db[0]
    dbname = host_db[1]

    # Intentar conectar a la base de datos
    conn = psycopg2.connect(
        dbname=dbname,
        user=user,
        password=password,
        host=host
    )

    print("Conexión exitosa a la base de datos PostgreSQL")

    # Verificar si la tabla admin_user existe
    cursor = conn.cursor()
    cursor.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'admin_user');")
    table_exists = cursor.fetchone()[0]

    if table_exists:
        print("La tabla admin_user existe")

        # Verificar si hay usuarios admin
        cursor.execute("SELECT * FROM admin_user WHERE username = 'admin';")
        admin_user = cursor.fetchone()

        if admin_user:
            print(f"Usuario admin encontrado: {admin_user}")
        else:
            print("No se encontró el usuario admin")
    else:
        print("La tabla admin_user no existe")

    conn.close()

except Exception as e:
    print(f"Error al conectar a la base de datos: {str(e)}")
