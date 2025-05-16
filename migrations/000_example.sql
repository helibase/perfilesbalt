-- Migración inicial para crear tablas básicas
-- Esta migración se ejecutará si no existe la tabla

-- Tabla para mensajes de contacto
CREATE TABLE IF NOT EXISTS contact_message (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL,
    message TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla para suscriptores del newsletter
CREATE TABLE IF NOT EXISTS newsletter_subscriber (
    id SERIAL PRIMARY KEY,
    email VARCHAR(100) NOT NULL UNIQUE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla para configuraciones del sitio
CREATE TABLE IF NOT EXISTS site_config (
    id SERIAL PRIMARY KEY,
    key VARCHAR(50) NOT NULL UNIQUE,
    value TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insertar algunas configuraciones iniciales
INSERT INTO site_config (key, value)
VALUES ('site_title', 'PerfilesBalt')
ON CONFLICT (key) DO NOTHING;

INSERT INTO site_config (key, value)
VALUES ('contact_email', 'info@perfilesbalt.com')
ON CONFLICT (key) DO NOTHING;

INSERT INTO site_config (key, value)
VALUES ('contact_phone', '+123 456 7890')
ON CONFLICT (key) DO NOTHING;

INSERT INTO site_config (key, value)
VALUES ('contact_address', 'Av. Principal 123, Ciudad Empresarial')
ON CONFLICT (key) DO NOTHING;
