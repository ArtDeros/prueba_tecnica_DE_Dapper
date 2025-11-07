-- Script para crear la tabla regulations en la base de datos de Airflow
-- Ejecutar este script en la base de datos 'airflow' de Postgres

-- Crear la tabla regulations si no existe
CREATE TABLE IF NOT EXISTS regulations (
    id SERIAL PRIMARY KEY,
    created_at VARCHAR(255),
    update_at VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    title VARCHAR(255),
    gtype VARCHAR(50),
    entity VARCHAR(255),
    external_link TEXT,
    rtype_id INTEGER,
    summary TEXT,
    classification_id INTEGER
);

-- Crear la tabla regulations_component si no existe
CREATE TABLE IF NOT EXISTS regulations_component (
    id SERIAL PRIMARY KEY,
    regulations_id INTEGER REFERENCES regulations(id),
    components_id INTEGER
);

-- Crear índices para mejorar el rendimiento
CREATE INDEX IF NOT EXISTS idx_regulations_entity ON regulations(entity);
CREATE INDEX IF NOT EXISTS idx_regulations_created_at ON regulations(created_at);
CREATE INDEX IF NOT EXISTS idx_regulations_title ON regulations(title);
CREATE INDEX IF NOT EXISTS idx_regulations_external_link ON regulations(external_link);
CREATE INDEX IF NOT EXISTS idx_regulations_component_regulations_id ON regulations_component(regulations_id);

-- Comentarios en las tablas
COMMENT ON TABLE regulations IS 'Tabla para almacenar normativas extraídas de ANI';
COMMENT ON TABLE regulations_component IS 'Tabla de relación entre regulaciones y componentes';

