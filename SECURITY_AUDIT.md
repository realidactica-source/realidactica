# Auditoría de seguridad de Realidáctica

Fecha: 30 de agosto de 2026

## Estado

El código fue endurecido para retirar secretos, separar permisos de alumnos y docentes, validar solicitudes y evitar que contenido generado por IA se ejecute como HTML.

## Hallazgos críticos corregidos

- Credenciales de MySQL, una contraseña de aplicación de Gmail y varias claves de Gemini estaban incluidas directamente en el repositorio. Fueron retiradas y sustituidas por variables de entorno.
- Flask se ejecutaba con `debug=True` y escuchaba en todas las interfaces. Ahora el modo de depuración está desactivado por defecto y el host predeterminado es local.
- CORS estaba abierto para cualquier origen aunque la aplicación es de mismo origen. Se eliminó.
- `/test_db` exponía nombres, apellidos y roles sin autenticación. Se eliminó.
- Cualquier persona podía registrarse como maestro. El registro público ahora crea únicamente alumnos.
- Las rutas docentes no comprobaban el rol. Ahora requieren sesión y rol `maestro`.
- Las operaciones POST carecían de CSRF. Se añadió un token de sesión a formularios y solicitudes `fetch`.
- El chat y los tests insertaban texto de la IA con `innerHTML`. La nueva interfaz construye nodos y usa `textContent`.
- El generador de tests aceptaba rutas de archivos controladas por el cliente. Ahora usa un catálogo fijo del servidor.
- Los mensajes de error devolvían excepciones internas. Ahora se registran en el servidor y el cliente recibe mensajes genéricos.
- Las cookies de sesión ahora son `HttpOnly`, `SameSite=Lax` y `Secure` en producción.
- Se añadieron CSP, `X-Content-Type-Options`, política de permisos, protección de marcos y política de referencia.
- La carga docente simulaba éxito sin subir nada. Ahora valida PDF, límite, grupo, nombre seguro y persiste la asignación.
- La encuesta estaba incompleta y redirigía a una ruta inexistente. Ahora contiene ocho preguntas y guarda un único perfil por alumno.
- Los videos de Google Drive estaban bloqueados por permisos del propietario. Se retiraron de la vista activa hasta publicar fuentes embebibles verificadas; los PDF continúan disponibles.

## Acciones externas obligatorias

Los secretos aparecieron en Git y deben considerarse comprometidos aunque ya no estén en la versión actual:

1. Rotar la contraseña del usuario MySQL de Railway y evitar el usuario `root` para la aplicación.
2. Revocar la contraseña de aplicación de Gmail expuesta y crear una nueva.
3. Revocar todas las claves de Gemini que estuvieron en `app.py` y en los antiguos módulos de tutores.
4. Crear una clave nueva de OpenAI con alcance de proyecto, límites de gasto y alertas.
5. Configurar las variables del archivo `.env.example` en el entorno de despliegue; nunca confirmar `.env` en Git.
6. Si el repositorio fue público, considerar limpiar el historial con una herramienta especializada después de rotar los secretos. La rotación es prioritaria.

## Riesgos residuales y recomendaciones

- El rate limiting de inicio de sesión es local al proceso. En producción con varias instancias debe migrarse a Redis o al proxy/WAF.
- Los documentos subidos se guardan en disco local. En despliegues efímeros conviene usar almacenamiento de objetos privado y análisis antimalware.
- Debe aplicarse `migrations/001_security_hardening.sql` a la base existente antes de activar registro, encuesta y asignación de materiales.
- Es recomendable ejecutar análisis de dependencias en CI y fijar versiones después de validar una compilación reproducible.
- Las cuentas de maestro deben crearse o promoverse únicamente mediante un flujo administrativo separado.
