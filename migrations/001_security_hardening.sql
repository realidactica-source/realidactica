-- Ejecuta este archivo una sola vez sobre una base existente y revisa cualquier
-- índice duplicado antes de continuar. Crea un respaldo primero.

ALTER TABLE usuarios
  ADD COLUMN IF NOT EXISTS token_confirmacion VARCHAR(64) NULL AFTER activo,
  ADD COLUMN IF NOT EXISTS token_creado DATETIME NULL AFTER token_confirmacion;

ALTER TABLE usuarios
  MODIFY rol ENUM('alumno', 'maestro') NOT NULL DEFAULT 'alumno',
  MODIFY activo TINYINT(1) NOT NULL DEFAULT 0;

ALTER TABLE perfiles_aprendizaje
  ADD UNIQUE KEY uq_perfiles_alumno (id_alumno);

CREATE TABLE IF NOT EXISTS asignaciones_materiales (
  id_archivo INT NOT NULL,
  id_grupo INT NOT NULL,
  asignado TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id_archivo, id_grupo),
  CONSTRAINT fk_asignacion_archivo
    FOREIGN KEY (id_archivo) REFERENCES archivos_docentes(id_archivo)
    ON DELETE CASCADE,
  CONSTRAINT fk_asignacion_grupo
    FOREIGN KEY (id_grupo) REFERENCES grupos(id_grupo)
    ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
