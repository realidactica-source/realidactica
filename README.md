# Realidáctica

Plataforma educativa Flask con paneles para estudiantes y docentes, tutoría con OpenAI y temas claro/oscuro.

## Configuración local

1. Crea un entorno virtual e instala `requirements.txt`.
2. Copia `.env.example` a `.env` y asigna secretos nuevos.
3. Crea la base de datos con `schema.sql`. Para una base existente, revisa y aplica `migrations/001_security_hardening.sql` después de generar un respaldo.
4. Exporta las variables de `.env` en el entorno donde se ejecuta Flask.
5. Inicia con `python app.py` para desarrollo o con un servidor WSGI en producción.

La aplicación usa `gpt-5.6-luna` mediante OpenAI Responses API. La clave se lee únicamente desde `OPENAI_API_KEY`.

## Despliegue en Railway

El `Dockerfile` ejecuta `scripts/init_db.py` antes de iniciar Gunicorn. Configura `APP_ENV=production`, una `SECRET_KEY` aleatoria y las variables `MYSQL_*` mediante referencias privadas al servicio MySQL de Railway. `OPENAI_API_KEY` y las variables de Gmail son opcionales para el arranque, pero necesarias para la tutoría y el correo de confirmación.

## Seguridad

Consulta `SECURITY_AUDIT.md`. Antes de desplegar, rota las credenciales que aparecieron en versiones anteriores del repositorio.
