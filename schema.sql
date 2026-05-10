-- ============================================================
--  SISTEMA DE REPARTO DE REGALOS - DÍA DE LA MADRE
--  Ejecutar este script en MySQL antes de iniciar la app
-- ============================================================

CREATE DATABASE IF NOT EXISTS reparto_regalos
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE reparto_regalos;

CREATE TABLE IF NOT EXISTS beneficiarias (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    dni           CHAR(8)      NOT NULL UNIQUE,
    nombres       VARCHAR(100) NOT NULL,
    apellidos     VARCHAR(100) NOT NULL DEFAULT '',
    ya_recibio    TINYINT(1)   NOT NULL DEFAULT 0,
    fecha_entrega DATETIME     NULL,
    registrado_en DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Vista rápida de entregas del día
CREATE OR REPLACE VIEW entregas_hoy AS
SELECT
    dni,
    nombres,
    apellidos,
    fecha_entrega
FROM beneficiarias
WHERE DATE(fecha_entrega) = CURDATE()
ORDER BY fecha_entrega DESC;

-- Índice para búsquedas por DNI (ya tiene UNIQUE, pero por si acaso)
CREATE INDEX IF NOT EXISTS idx_dni ON beneficiarias(dni);

-- Usuario de sólo-lectura para reportes (opcional)
-- CREATE USER IF NOT EXISTS 'reporte'@'localhost' IDENTIFIED BY 'solo_lectura';
-- GRANT SELECT ON reparto_regalos.* TO 'reporte'@'localhost';

-- Datos de prueba (puedes borrarlos)
-- INSERT INTO beneficiarias (dni, nombres, apellidos, ya_recibio) VALUES
-- ('12345678', 'MARÍA', 'QUISPE MAMANI', 0),
-- ('87654321', 'ANA', 'FLORES HUANCA',  0);
