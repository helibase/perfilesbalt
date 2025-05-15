import os
import logging
import re
import sqlite3
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from urllib.parse import urlparse

def is_sqlite_url(db_url):
    """Determina si la URL es para SQLite"""
    return db_url.startswith('sqlite:')

def is_postgres_url(db_url):
    """Determina si la URL es para PostgreSQL"""
    return db_url.startswith('postgresql:') or db_url.startswith('postgres:')

def apply_migrations(db_url, migrations_folder):
    """Aplica migraciones según el tipo de base de datos"""
    if is_sqlite_url(db_url):
        apply_sqlite_migrations(db_url, migrations_folder)
    elif is_postgres_url(db_url):
        apply_postgres_migrations(db_url, migrations_folder)
    else:
        logging.error(f"Tipo de base de datos no soportado: {db_url}")
        raise ValueError(f"Tipo de base de datos no soportado: {db_url}")

def apply_sqlite_migrations(db_url, migrations_folder):
    """Aplica migraciones SQL para SQLite"""
    logging.info("Aplicando migraciones SQLite...")

    # Extraer la ruta del archivo de la URL
    db_path = db_url.replace('sqlite:///', '')

    # Obtener conexión directa a SQLite
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Crear tabla de migraciones si no existe
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS migrations (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Obtener migraciones ya aplicadas
    cursor.execute('SELECT name FROM migrations')
    applied_migrations = set(row[0] for row in cursor.fetchall())

    # Obtener archivos de migración ordenados
    migration_files = []
    for filename in os.listdir(migrations_folder):
        if filename.endswith('.sql'):
            match = re.match(r'(\d+)_(.+)\.sql', filename)
            if match:
                order = int(match.group(1))
                migration_files.append((order, filename))

    migration_files.sort()  # Ordenar por número

    # Aplicar migraciones pendientes
    for _, filename in migration_files:
        if filename not in applied_migrations:
            logging.info(f"Aplicando migración: {filename}")

            with open(os.path.join(migrations_folder, filename), 'r') as f:
                sql = f.read()

            try:
                cursor.executescript(sql)
                cursor.execute('INSERT INTO migrations (name) VALUES (?)', (filename,))
                conn.commit()
                logging.info(f"Migración aplicada: {filename}")
            except Exception as e:
                conn.rollback()
                logging.error(f"Error al aplicar migración {filename}: {str(e)}")
                raise

    conn.close()
    logging.info("Migraciones SQLite completadas")

def apply_postgres_migrations(db_url, migrations_folder):
    """Aplica migraciones SQL para PostgreSQL"""
    logging.info("Aplicando migraciones PostgreSQL...")

    try:
        # Conectar a PostgreSQL
        conn = psycopg2.connect(db_url)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        # Crear tabla de migraciones si no existe
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS migrations (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        # Obtener migraciones ya aplicadas
        cursor.execute('SELECT name FROM migrations')
        applied_migrations = set(row[0] for row in cursor.fetchall())

        # Obtener archivos de migración ordenados
        migration_files = []
        for filename in os.listdir(migrations_folder):
            if filename.endswith('.sql'):
                match = re.match(r'(\d+)_(.+)\.sql', filename)
                if match:
                    order = int(match.group(1))
                    migration_files.append((order, filename))

        migration_files.sort()  # Ordenar por número

        # Aplicar migraciones pendientes
        for _, filename in migration_files:
            if filename not in applied_migrations:
                logging.info(f"Aplicando migración: {filename}")

                with open(os.path.join(migrations_folder, filename), 'r') as f:
                    sql = f.read()

                try:
                    cursor.execute(sql)
                    cursor.execute('INSERT INTO migrations (name) VALUES (%s)', (filename,))
                    logging.info(f"Migración aplicada: {filename}")
                except Exception as e:
                    logging.error(f"Error al aplicar migración {filename}: {str(e)}")
                    raise

        conn.close()
        logging.info("Migraciones PostgreSQL completadas")
    except Exception as e:
        logging.error(f"Error al conectar con PostgreSQL: {str(e)}")
        raise

def ensure_database_exists(db_url):
    """Asegura que la base de datos exista, la crea si no existe"""
    if is_sqlite_url(db_url):
        # Para SQLite, no necesitamos hacer nada especial
        db_path = db_url.replace('sqlite:///', '')
        logging.info(f"Usando base de datos SQLite en: {db_path}")
        return

    elif is_postgres_url(db_url):
        try:
            # Extraer nombre de la base de datos de la URL
            parsed_url = urlparse(db_url)
            db_name = parsed_url.path.strip('/')

            # Crear una conexión al servidor PostgreSQL sin especificar base de datos
            conn_params = {
                'user': parsed_url.username,
                'password': parsed_url.password,
                'host': parsed_url.hostname,
                'port': parsed_url.port or 5432
            }

            conn = psycopg2.connect(**conn_params, database='postgres')
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cursor = conn.cursor()

            # Verificar si la base de datos existe
            cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
            exists = cursor.fetchone()

            if not exists:
                logging.info(f"Creando base de datos: {db_name}")
                cursor.execute(f"CREATE DATABASE {db_name}")
                logging.info(f"Base de datos {db_name} creada")
            else:
                logging.info(f"Base de datos {db_name} ya existe")

            cursor.close()
            conn.close()
        except Exception as e:
            logging.error(f"Error al verificar/crear la base de datos: {str(e)}")
            # No lanzamos la excepción para permitir que la aplicación continúe
            # en caso de que la base de datos ya exista pero no podamos verificarlo
    else:
        logging.error(f"Tipo de base de datos no soportado: {db_url}")
