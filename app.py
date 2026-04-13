from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_mysqldb import MySQL
from flask_cors import CORS
from google import genai
from google.genai import types # Importante para configurar la búsqueda en internet
import MySQLdb.cursors
import bcrypt
import os

app = Flask(__name__)
CORS(app)

# Ruta absoluta al directorio del proyecto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Clave secreta para manejar sesiones y cookies de forma segura
app.secret_key = 'realidactica_2026_secure' 
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_mysqldb import MySQL
from flask_cors import CORS
from google import genai
from google.genai import types # Importante para configurar la búsqueda en internet
import MySQLdb.cursors
import bcrypt
import os
import secrets                          # Para generar el token seguro
import smtplib                          # Para enviar correos via Gmail
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

app = Flask(__name__)
CORS(app)

# Ruta absoluta al directorio del proyecto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Clave secreta para manejar sesiones y cookies de forma segura
app.secret_key = 'realidactica_2026_secure' 

# --- CONFIGURACIÓN DE BASE DE DATOS ---
app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'u515719198_realidactica'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

# --- CONFIGURACIÓN DE CORREO GMAIL ---
# ⚠️  Reemplaza estos valores con los tuyos:
#     GMAIL_USER  → tu cuenta Gmail completa
#     GMAIL_PASS  → Contraseña de aplicación de 16 dígitos (NO tu contraseña normal)
#     Para generarla: myaccount.google.com → Seguridad → Contraseñas de aplicación
GMAIL_USER = "vladimirades@gmail.com"       # ← cambia esto
GMAIL_PASS = "zhhn bnqt jocm zsau"     # ← contraseña de aplicación de 16 dígitos
BASE_URL   = "http://localhost:8080"   # ← cambia a tu dominio en producción

def enviar_correo_confirmacion(nombre, correo_destino, token):
    """Envía el correo de confirmación de cuenta al nuevo usuario."""
    link = f"{BASE_URL}/confirmar/{token}"

    html = f"""
    <div style="font-family:Arial,sans-serif; max-width:520px; margin:auto;
                border:1px solid #e0e0e0; border-radius:12px; overflow:hidden;">
      <div style="background:#0fd3c7; padding:28px; text-align:center;">
        <h1 style="color:#fff; margin:0; font-size:26px;">Realidáctica</h1>
        <p style="color:#fff; margin:6px 0 0; font-size:14px;">Plataforma educativa inteligente</p>
      </div>
      <div style="padding:32px;">
        <h2 style="color:#333; margin-top:0;">¡Hola, {nombre}! 👋</h2>
        <p style="color:#555; line-height:1.6;">
          Gracias por registrarte. Para activar tu cuenta y poder iniciar sesión,
          haz clic en el botón de abajo:
        </p>
        <div style="text-align:center; margin:32px 0;">
          <a href="{link}"
             style="background:#0fd3c7; color:#fff; text-decoration:none;
                    padding:14px 36px; border-radius:8px; font-size:16px;
                    font-weight:bold; display:inline-block;">
            ✅ Confirmar mi cuenta
          </a>
        </div>
        <p style="color:#999; font-size:12px;">
          Si no creaste una cuenta en Realidáctica, ignora este correo.<br>
          El enlace es válido por 24 horas.
        </p>
        <hr style="border:none; border-top:1px solid #eee; margin:24px 0;">
        <p style="color:#bbb; font-size:11px; text-align:center;">
          Si el botón no funciona, copia este enlace en tu navegador:<br>
          <a href="{link}" style="color:#0fd3c7;">{link}</a>
        </p>
      </div>
    </div>
    """

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "Confirma tu cuenta en Realidáctica"
        msg["From"]    = f"Realidáctica <{GMAIL_USER}>"
        msg["To"]      = correo_destino
        msg.attach(MIMEText(html, "html"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(GMAIL_USER, GMAIL_PASS)
            server.sendmail(GMAIL_USER, correo_destino, msg.as_string())

        print(f"[mail] ✓ Correo enviado a {correo_destino}")
        return True
    except Exception as e:
        print(f"[mail] ✗ Error al enviar correo: {e}")
        return False

# --- CONFIGURACIÓN IA GEMINI ---
# Se utiliza la API Key proporcionada para el proyecto Realidáctica
client = genai.Client(api_key="AIzaSyC-Cjkzjc9tgXgw6HtZ0CmzXullIP1K-_s")

# --- RUTA DEL CHAT INTELIGENTE (KADY GENERAL) ---
@app.route("/consulta", methods=["POST"])
def consulta():
    if 'loggedin' not in session:
        return jsonify({"mensaje": "Debes iniciar sesión."}), 401

    texto_usuario = request.form.get("consulta")
    if not texto_usuario:
        return jsonify({"mensaje": "No escribiste nada..."}), 400

    try:
        # 1. OBTENER INFORMACIÓN DEL ALUMNO (CONTEXTO)
        user_id = session.get('user_id')
        cursor = mysql.connection.cursor()
        
        # Obtenemos el nombre real del usuario desde la tabla 'usuarios'
        cursor.execute("SELECT nombre, apellido FROM usuarios WHERE id = %s", (user_id,))
        user_data = cursor.fetchone()
        
        # Obtenemos las materias y maestros registrados en 'materias'
        cursor.execute("SELECT materia, maestro, grado, grupo FROM materias")
        materias_data = cursor.fetchall()
        cursor.close()

        # Construimos la lista de materias para la IA
        lista_materias = ""
        for m in materias_data:
            lista_materias += f"- {m['materia']} (Prof. {m['maestro']}, {m['grado']}° {m['grupo']})\n"

        # --- NUEVO: LEER MEMORIA COMPARTIDA POR EL TUTOR DE CLASE ---
        notas_clase = session.get('notas_estudiante', '')
        contexto_extra = ""
        if notas_clase:
            contexto_extra = f"\nINFORMACIÓN RECIENTE DE SUS CLASES ESPECÍFICAS (Menciónalo sutilmente si es relevante): {notas_clase}"

        # 2. CONFIGURAR EL SYSTEM PROMPT (LA PERSONALIDAD)
        # Esto le dice a la IA quién es y qué sabe sobre el alumno
        system_instruction = f"""
        Se breve con tus respuestas
        Eres 'Kady', el asistente inteligente de la plataforma educativa Realidáctica.
        Estás conversando con el alumno {user_data['nombre']} {user_data['apellido']}.
        {contexto_extra}
        
        Tu contexto educativo actual:
        - Materias disponibles: 
        {lista_materias}
        
        Eres un asistente académico inteligente dentro de la plataforma educativa Realidáctica. 
Tu función es ayudar a los estudiantes a organizar su aprendizaje, resolver dudas y mejorar su progreso académico.

Tu comportamiento debe ser el de un tutor amigable, motivador y claro.

INSTRUCCIONES GENERALES:

1. Ayuda al estudiante a organizar sus actividades académicas.
2. Informa sobre tareas pendientes, recordatorios y fechas de entrega cuando el estudiante lo solicite.
3. Ofrece apoyo en diferentes materias cuando el estudiante tenga dudas.
4. Motiva al estudiante a continuar aprendiendo y mejorar su desempeño.
5. Mantén siempre un tono claro, amigable y educativo.

GESTIÓN DE TAREAS Y RECORDATORIOS:

1. Si el estudiante pregunta por tareas pendientes, muestra una lista clara de las tareas activas.
2. Indica la materia, la descripción y la fecha de entrega.
3. Si una tarea está próxima a vencer, advierte al estudiante.
4. Si el estudiante no tiene tareas pendientes, infórmalo y sugiere actividades de repaso.

EJEMPLO:

"Tienes 2 tareas pendientes:
• Redes: Configuración de router básico (entrega mañana)
• Cálculo: Ejercicios de derivadas (entrega en 3 días)"

SUGERENCIAS DE ESTUDIO:

1. Analiza el progreso del estudiante cuando sea posible.
2. Sugiere formas de mejorar su rendimiento.
3. Recomienda prácticas, ejercicios o recursos educativos.

EJEMPLO:

"Noté que has trabajado poco en cálculo esta semana. 
Te recomiendo practicar algunos ejercicios de derivadas para reforzar el tema."

DINÁMICAS DE APRENDIZAJE:

Cuando sea posible, genera actividades como:

• preguntas rápidas
• mini quizzes
• retos de aprendizaje
• ejercicios prácticos
• reflexiones sobre el tema

Ejemplo:

"Vamos a hacer un reto rápido:
¿Sabes qué capa del modelo OSI se encarga de dirigir los paquetes de datos entre redes?"

ADAPTACIÓN AL ESTUDIANTE:

1. Recuerda el tipo de aprendizaje del estudiante si está disponible (visual, auditivo, kinestésico).
2. Ajusta las explicaciones según su estilo de aprendizaje.

Ejemplo:

Si es visual:
"Te explicaré este concepto con un ejemplo y una estructura sencilla."

Si es práctico:
"Vamos a resolver un ejercicio paso a paso."

RESPUESTAS:

1. Mantén las respuestas claras y fáciles de entender.
2. Usa ejemplos cuando sea necesario.
3. Evita respuestas demasiado largas.
4. Prioriza ayudar al estudiante a aprender, no solo dar la respuesta.

OBJETIVO FINAL:

Tu objetivo es acompañar al estudiante en su proceso de aprendizaje, ayudarle a organizar sus estudios y mejorar su comprensión de los temas académicos.
        
        """

        # 3. MANEJAR LA MEMORIA (HISTORIAL DE SESIÓN)
        # Si no existe el historial en la sesión, lo inicializamos
        if 'chat_history' not in session:
            session['chat_history'] = []

        # Estructuramos el mensaje del usuario para la API de Gemini
        mensaje_usuario = {"role": "user", "parts": [{"text": texto_usuario}]}
        
        # Creamos el paquete de 'contents' que incluye: Instrucciones + Historial + Pregunta Actual
        # Limitamos el historial a los últimos 6 mensajes para no saturar la memoria
        historial_reciente = session['chat_history'][-6:]
        
        payload_ia = [
            {"role": "user", "parts": [{"text": f"INSTRUCCIONES DE SISTEMA: {system_instruction}"}]},
            *historial_reciente,
            mensaje_usuario
        ]

        # 4. LLAMADA A LA IA
        response = client.models.generate_content(
            model="gemini-2.5-flash", 
            contents=payload_ia
        )
        
        # 5. ACTUALIZAR MEMORIA
        # Guardamos la pregunta y la respuesta en la sesión del navegador
        session['chat_history'].append(mensaje_usuario)
        session['chat_history'].append({"role": "model", "parts": [{"text": response.text}]})
        session.modified = True # Forzamos a Flask a guardar los cambios en la sesión
        
        return jsonify({"mensaje": response.text})

    except Exception as e:
        print(f"Error detallado en Gemini: {e}")
        return jsonify({"mensaje": "Lo siento, tuve un problema interno al procesar tu duda."}), 500

# --- RUTA DEL CHAT ESPECÍFICO DE CLASES (CON ARCHIVOS + INTERNET) ---
@app.route("/consulta_clase", methods=["POST"])
def consulta_clase():
    if 'loggedin' not in session:
        return jsonify({"mensaje": "Debes iniciar sesión."}), 401

    import time

    texto_usuario = request.form.get("consulta", "").strip()
    materia = request.form.get("materia", "General")

    if not texto_usuario:
        return jsonify({"mensaje": "No escribiste nada..."}), 400

    try:
        user_name = session.get('user_name', 'Estudiante')

        # Rutas absolutas — funcionan sin importar desde dónde se corra Flask
        ARCHIVOS_CLASE = [
            os.path.join(BASE_DIR, "static", "clases", "liderazgo", "1.4 Comunicación organizacional.pdf"),
            os.path.join(BASE_DIR, "static", "clases", "liderazgo", "Tipos de comunicación organizacional  Comunicación empresarial - LearnFree en Español (720p, h264, youtube).mp4"),
        ]
        MIME_MAP = {".pdf": "application/pdf", ".mp4": "video/mp4", ".mov": "video/quicktime"}

        def _mime(p):
            return MIME_MAP.get(os.path.splitext(p)[1].lower(), "application/octet-stream")

        # Subir archivos a Gemini para que Kady los pueda leer
        partes_archivos = []
        for ruta in ARCHIVOS_CLASE:
            if os.path.exists(ruta):
                try:
                    archivo = client.files.upload(
                        file=ruta,
                        config=types.UploadFileConfig(mime_type=_mime(ruta))
                    )
                    # Los videos necesitan tiempo de procesamiento
                    if _mime(ruta).startswith("video/"):
                        intentos = 0
                        while getattr(archivo.state, 'name', '') == "PROCESSING" and intentos < 30:
                            time.sleep(5)
                            archivo = client.files.get(name=archivo.name)
                            intentos += 1
                    partes_archivos.append(
                        types.Part.from_uri(file_uri=archivo.uri, mime_type=_mime(ruta))
                    )
                    print(f"[clase] ✓ Archivo subido: {os.path.basename(ruta)}")
                except Exception as e:
                    print(f"[clase] ✗ No se pudo subir {os.path.basename(ruta)}: {e}")
            else:
                print(f"[clase] ✗ Archivo no encontrado: {ruta}")

        notas_clase = session.get('notas_estudiante', '')
        system_instruction = f"""
Eres Kady, tutora académica experta en {materia}. Hablas con {user_name}.
Tienes acceso al PDF "Comunicación Organizacional" y al video de la clase.
Úsalos siempre para fundamentar tus respuestas.

Instrucciones:
- Resumen del PDF: estructura la respuesta por secciones del documento.
- Resumen del video: incluye los temas por minutaje aproximado.
- Resumen de ambos: primero video, luego PDF, luego síntesis de 2-3 líneas.
- Conceptos clave: lista 6-8 conceptos del PDF y video con definición breve.
- Preguntas libres: responde basándote en los archivos y búsqueda web.
- Usa viñetas para mayor claridad. Sé concisa pero profunda.
{f"Nota del estudiante: {notas_clase}" if notas_clase else ""}
"""
        partes = (
            [types.Part.from_text(text=system_instruction)]
            + partes_archivos
            + [types.Part.from_text(text=texto_usuario)]
        )
        contenido = [types.Content(role="user", parts=partes)]
        config = types.GenerateContentConfig(
            tools=[{"google_search": {}}],
            temperature=0.7
        )
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=contenido,
            config=config
        )

        if any(p in texto_usuario.lower() for p in ["difícil", "no entiendo", "no comprendo", "ayuda", "confuso"]):
            session['notas_estudiante'] = f"El estudiante tuvo dificultades en {materia}."
            session.modified = True

        return jsonify({"mensaje": response.text})

    except Exception as e:
        print(f"[clase] Error: {e}")
        return jsonify({"mensaje": f"Hubo un problema al procesar tu consulta: {str(e)}"}), 500

# --- RUTAS DE LOGIN Y NAVEGACIÓN ---
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario_input = request.form.get("usuario", "").strip()
        password_input = request.form.get("password", "")

        cursor = mysql.connection.cursor()
        # Buscamos por matrícula, correo o nombre de usuario (los 3 son válidos)
        cursor.execute(
            "SELECT * FROM usuarios WHERE matricula = %s OR correo = %s OR usuario = %s",
            (usuario_input, usuario_input, usuario_input)
        )
        user = cursor.fetchone()
        cursor.close()

        if user:
            # Verificar que la cuenta esté confirmada (activo = 1)
            if not user['activo']:
                flash(
                    "Tu cuenta aún no está confirmada. "
                    "Revisa tu correo y haz clic en el enlace de activación.",
                    "danger"
                )
            else:
                # Compatibilidad de hashes: convertimos $2y$ (PHP) a $2b$ (Python)
                hash_db = user['pass_hash'].replace('$2y$', '$2b$')
                if bcrypt.checkpw(password_input.encode('utf-8'), hash_db.encode('utf-8')):
                    session['loggedin']  = True
                    session['user_id']   = user['id']
                    session['user_name'] = user['nombre']
                    session['user_rol']  = user['rol']
                    session['chat_history'] = []
                    # Redirige según rol
                    if user['rol'] == 'maestro':
                        return redirect(url_for('maestro_prin'))
                    return redirect(url_for('prin'))
                else:
                    flash("Contraseña incorrecta", "danger")
        else:
            flash("Usuario, matrícula o correo no encontrado", "danger")

    return render_template("login.html")

@app.route("/prin")
def prin():
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    return render_template("prin_a.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/portal_alumno')
def portal_alumno():
    return redirect(url_for('alumno_portal'))
    
    # Tu portal-alumno.html espera una variable 'info' con los estilos de aprendizaje.
    # Por ahora pasamos un diccionario simulado, pero luego lo conectarás a MySQL.
    info_alumno = {
        'resultado_final': 'Visual', 
        'visual': 50, 'auditivo': 30, 'kinestesico': 20
    }
    return render_template("portal-alumno.html", info=info_alumno)

@app.route("/portal-maestro")
def maestro_portal(): 
    # En gestion.html haces referencia a url_for('maestro_portal')
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    return render_template("portal_m.html", alumnos=[]) 

@app.route("/encuesta")
def encuesta():
    return render_template("encuesta.html")
    
@app.route("/gestion")
def gestion():
    # Tu gestion.html espera listas de 'carreras' y 'grupos_lista' para mostrarlas
    return render_template("gestion.html", carreras=[], grupos_lista=[])
    
@app.route('/clase_calculo')
def clase_calculo():
    clase_data = {'id': 1, 'titulo': 'Cálculo de Varias Variables'}
    return render_template('clase_calculo.html', clase=clase_data)

@app.route('/clase_frameworks')
def clase_frameworks():
    clase_data = {'id': 2, 'titulo': 'Frameworks'}
    # Fíjate que el archivo se llama "clase_franworks.html", así lo definiste
    return render_template('clase_franworks.html', clase=clase_data)

@app.route("/generar_test", methods=["POST"])
def generar_test():
    if 'loggedin' not in session:
        return jsonify({"error": "Debes iniciar sesión."}), 401

    import re, json, time

    # Recibir la materia y archivos desde el HTML que hace el request
    carpeta = request.form.get("carpeta", "liderazgo")
    pdf     = request.form.get("pdf",     "1.4 Comunicación organizacional.pdf")
    video   = request.form.get("video",   "Tipos de comunicación organizacional  Comunicación empresarial - LearnFree en Español (720p, h264, youtube).mp4")
    materia = request.form.get("materia", "la clase")

    ARCHIVOS_CLASE = [
        os.path.join(BASE_DIR, "static", "clases", carpeta, pdf),
        os.path.join(BASE_DIR, "static", "clases", carpeta, video),
    ]
    MIME_MAP = {".pdf": "application/pdf", ".mp4": "video/mp4", ".mov": "video/quicktime"}

    def _mime(p):
        return MIME_MAP.get(os.path.splitext(p)[1].lower(), "application/octet-stream")

    partes = []
    for ruta in ARCHIVOS_CLASE:
        if os.path.exists(ruta):
            try:
                archivo = client.files.upload(
                    file=ruta,
                    config=types.UploadFileConfig(mime_type=_mime(ruta))
                )
                if _mime(ruta).startswith("video/"):
                    intentos = 0
                    while getattr(archivo.state, 'name', '') == "PROCESSING" and intentos < 30:
                        time.sleep(5)
                        archivo = client.files.get(name=archivo.name)
                        intentos += 1
                partes.append(types.Part.from_uri(file_uri=archivo.uri, mime_type=_mime(ruta)))
                print(f"[test] ✓ {os.path.basename(ruta)}")
            except Exception as e:
                print(f"[test] ✗ Error subiendo {os.path.basename(ruta)}: {e}")
        else:
            print(f"[test] ✗ No encontrado: {ruta}")

    prompt_test = f"""
Eres un evaluador académico especializado en {materia}.
Basándote ÚNICAMENTE en los materiales proporcionados (PDF y video),
genera un test de exactamente 5 preguntas de opción múltiple sobre {materia}.

Responde ÚNICAMENTE con JSON válido, sin texto adicional, sin bloques de código markdown.

Formato exacto:
{{
  "titulo": "Test: {materia}",
  "preguntas": [
    {{
      "id": 1,
      "pregunta": "Texto de la pregunta",
      "opciones": {{"A": "...", "B": "...", "C": "...", "D": "..."}},
      "correcta": "B",
      "explicacion": "Explicación breve de por qué esta opción es correcta."
    }}
  ]
}}

Genera exactamente 5 preguntas variadas que evalúen comprensión y aplicación de {materia}.
"""

    try:
        partes_completas = [types.Part.from_text(text=prompt_test)] + partes
        contenido = [types.Content(role="user", parts=partes_completas)]
        config = types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.4
        )
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=contenido,
            config=config
        )
        raw = response.text.strip()
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)
        test_data = json.loads(raw)
        return jsonify(test_data)

    except json.JSONDecodeError as e:
        print(f"[test] JSON inválido: {e} | Respuesta: {response.text[:400]}")
        return jsonify({"error": "Gemini no devolvió formato válido. Intenta de nuevo."}), 500
    except Exception as e:
        print(f"[test] Error: {e}")
        return jsonify({"error": f"Error al generar el test: {str(e)}"}), 500


@app.route('/clase_liderazgo')
def clase_liderazgo():
    clase_data = {'id': 3, 'titulo': 'Liderazgo y Equipos de Alto Rendimiento', 'modulo': 'Módulo 1'}
    return render_template('clase_Liderazgo.html', clase=clase_data, lista=[clase_data])  # ← agrega lista

@app.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        nombre    = request.form.get("nombre",    "").strip()
        apellido1 = request.form.get("apellido1", "").strip()
        apellido2 = request.form.get("apellido2", "").strip()
        matricula = request.form.get("matricula", "").strip()
        correo    = request.form.get("correo",    "").strip()
        telefono  = request.form.get("celular",   "").strip()
        rol       = request.form.get("rol",       "alumno")
        password  = request.form.get("password",  "")
        password2 = request.form.get("password2", "")

        # El campo 'usuario' será la matrícula si existe, o la parte local del correo
        usuario = matricula if matricula else correo.split("@")[0]

        # --- VALIDACIONES ---
        if password != password2:
            flash("Las contraseñas no coinciden", "danger")
            return render_template("registro.html")

        if len(password) < 6:
            flash("La contraseña debe tener al menos 6 caracteres", "danger")
            return render_template("registro.html")

        try:
            cursor = mysql.connection.cursor()

            # Verificar usuario duplicado (UNIQUE en DB)
            cursor.execute("SELECT id FROM usuarios WHERE usuario = %s", (usuario,))
            if cursor.fetchone():
                cursor.close()
                flash(f"El usuario '{usuario}' ya está registrado. Elige otro.", "danger")
                return render_template("registro.html")

            # Verificar correo duplicado (UNIQUE en DB)
            cursor.execute("SELECT id FROM usuarios WHERE correo = %s", (correo,))
            if cursor.fetchone():
                cursor.close()
                flash("Ese correo electrónico ya está registrado.", "danger")
                return render_template("registro.html")

            # Generar token único de confirmación (64 caracteres hexadecimales)
            token = secrets.token_hex(32)

            # Hashear contraseña con bcrypt
            pass_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

            # INSERT — activo=0 hasta que confirme el correo, se guarda el token
            cursor.execute("""
                INSERT INTO usuarios
                    (nombre, apellido, apellido2, matricula, correo, usuario,
                     pass_hash, telefono, rol, activo, token_confirmacion)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 0, %s)
            """, (nombre, apellido1, apellido2, matricula or None, correo,
                  usuario, pass_hash, telefono, rol, token))
            mysql.connection.commit()
            cursor.close()

        except Exception as e:
            print(f"[registro] Error DB: {e}")
            flash("Error al guardar el registro. Intenta de nuevo.", "danger")
            return render_template("registro.html")

        # Enviar correo de confirmación
        correo_enviado = enviar_correo_confirmacion(nombre, correo, token)
        if correo_enviado:
            flash(
                f"¡Registro exitoso! Te enviamos un correo a {correo}. "
                "Revisa tu bandeja (y la carpeta de spam) para confirmar tu cuenta.",
                "success"
            )
        else:
            flash(
                "Cuenta creada, pero no pudimos enviarte el correo de confirmación. "
                "Contacta al administrador.",
                "danger"
            )
        return redirect(url_for('login'))

    return render_template("registro.html")


@app.route("/confirmar/<token>")
def confirmar_cuenta(token):
    """Activa la cuenta del usuario cuando hace clic en el enlace del correo."""
    cursor = mysql.connection.cursor()
    cursor.execute(
        "SELECT id, nombre, activo FROM usuarios WHERE token_confirmacion = %s",
        (token,)
    )
    user = cursor.fetchone()

    if not user:
        cursor.close()
        flash("El enlace de confirmación no es válido o ya fue usado.", "danger")
        return redirect(url_for('login'))

    if user['activo'] == 1:
        cursor.close()
        flash("Tu cuenta ya estaba confirmada. Puedes iniciar sesión.", "success")
        return redirect(url_for('login'))

    # Activar cuenta y limpiar el token (ya no se necesita)
    cursor.execute(
        "UPDATE usuarios SET activo = 1, token_confirmacion = NULL WHERE id = %s",
        (user['id'],)
    )
    mysql.connection.commit()
    cursor.close()

    flash(f"¡Cuenta confirmada! Bienvenido/a, {user['nombre']}. Ya puedes iniciar sesión.", "success")
    return redirect(url_for('login'))

@app.route("/prin_m")
def maestro_prin():
    return render_template("prin_m.html")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/test_db")
def test_db():
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT id, nombre, apellido, rol FROM usuarios")
        usuarios = cursor.fetchall()
        cursor.close()
        return jsonify(usuarios)  # Verás los datos en el navegador como JSON
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # El servidor corre en el puerto 8080 con modo debug para desarrollo
    app.run(host="0.0.0.0", port=8080, debug=True)
# --- CONFIGURACIÓN DE BASE DE DATOS ---
app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'u515719198_realidactica'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

# --- CONFIGURACIÓN IA GEMINI ---
# Se utiliza la API Key proporcionada para el proyecto Realidáctica
client = genai.Client(api_key="AIzaSyC-Cjkzjc9tgXgw6HtZ0CmzXullIP1K-_s")

# --- RUTA DEL CHAT INTELIGENTE (KADY GENERAL) ---
@app.route("/consulta", methods=["POST"])
def consulta():
    if 'loggedin' not in session:
        return jsonify({"mensaje": "Debes iniciar sesión."}), 401

    texto_usuario = request.form.get("consulta")
    if not texto_usuario:
        return jsonify({"mensaje": "No escribiste nada..."}), 400

    try:
        # 1. OBTENER INFORMACIÓN DEL ALUMNO (CONTEXTO)
        user_id = session.get('user_id')
        cursor = mysql.connection.cursor()
        
        # Obtenemos el nombre real del usuario desde la tabla 'usuarios'
        cursor.execute("SELECT nombre, apellido FROM usuarios WHERE id = %s", (user_id,))
        user_data = cursor.fetchone()
        
        # Obtenemos las materias y maestros registrados en 'materias'
        cursor.execute("SELECT materia, maestro, grado, grupo FROM materias")
        materias_data = cursor.fetchall()
        cursor.close()

        # Construimos la lista de materias para la IA
        lista_materias = ""
        for m in materias_data:
            lista_materias += f"- {m['materia']} (Prof. {m['maestro']}, {m['grado']}° {m['grupo']})\n"

        # --- NUEVO: LEER MEMORIA COMPARTIDA POR EL TUTOR DE CLASE ---
        notas_clase = session.get('notas_estudiante', '')
        contexto_extra = ""
        if notas_clase:
            contexto_extra = f"\nINFORMACIÓN RECIENTE DE SUS CLASES ESPECÍFICAS (Menciónalo sutilmente si es relevante): {notas_clase}"

        # 2. CONFIGURAR EL SYSTEM PROMPT (LA PERSONALIDAD)
        # Esto le dice a la IA quién es y qué sabe sobre el alumno
        system_instruction = f"""
        Se breve con tus respuestas
        Eres 'Kady', el asistente inteligente de la plataforma educativa Realidáctica.
        Estás conversando con el alumno {user_data['nombre']} {user_data['apellido']}.
        {contexto_extra}
        
        Tu contexto educativo actual:
        - Materias disponibles: 
        {lista_materias}
        
        Eres un asistente académico inteligente dentro de la plataforma educativa Realidáctica. 
Tu función es ayudar a los estudiantes a organizar su aprendizaje, resolver dudas y mejorar su progreso académico.

Tu comportamiento debe ser el de un tutor amigable, motivador y claro.

INSTRUCCIONES GENERALES:

1. Ayuda al estudiante a organizar sus actividades académicas.
2. Informa sobre tareas pendientes, recordatorios y fechas de entrega cuando el estudiante lo solicite.
3. Ofrece apoyo en diferentes materias cuando el estudiante tenga dudas.
4. Motiva al estudiante a continuar aprendiendo y mejorar su desempeño.
5. Mantén siempre un tono claro, amigable y educativo.

GESTIÓN DE TAREAS Y RECORDATORIOS:

1. Si el estudiante pregunta por tareas pendientes, muestra una lista clara de las tareas activas.
2. Indica la materia, la descripción y la fecha de entrega.
3. Si una tarea está próxima a vencer, advierte al estudiante.
4. Si el estudiante no tiene tareas pendientes, infórmalo y sugiere actividades de repaso.

EJEMPLO:

"Tienes 2 tareas pendientes:
• Redes: Configuración de router básico (entrega mañana)
• Cálculo: Ejercicios de derivadas (entrega en 3 días)"

SUGERENCIAS DE ESTUDIO:

1. Analiza el progreso del estudiante cuando sea posible.
2. Sugiere formas de mejorar su rendimiento.
3. Recomienda prácticas, ejercicios o recursos educativos.

EJEMPLO:

"Noté que has trabajado poco en cálculo esta semana. 
Te recomiendo practicar algunos ejercicios de derivadas para reforzar el tema."

DINÁMICAS DE APRENDIZAJE:

Cuando sea posible, genera actividades como:

• preguntas rápidas
• mini quizzes
• retos de aprendizaje
• ejercicios prácticos
• reflexiones sobre el tema

Ejemplo:

"Vamos a hacer un reto rápido:
¿Sabes qué capa del modelo OSI se encarga de dirigir los paquetes de datos entre redes?"

ADAPTACIÓN AL ESTUDIANTE:

1. Recuerda el tipo de aprendizaje del estudiante si está disponible (visual, auditivo, kinestésico).
2. Ajusta las explicaciones según su estilo de aprendizaje.

Ejemplo:

Si es visual:
"Te explicaré este concepto con un ejemplo y una estructura sencilla."

Si es práctico:
"Vamos a resolver un ejercicio paso a paso."

RESPUESTAS:

1. Mantén las respuestas claras y fáciles de entender.
2. Usa ejemplos cuando sea necesario.
3. Evita respuestas demasiado largas.
4. Prioriza ayudar al estudiante a aprender, no solo dar la respuesta.

OBJETIVO FINAL:

Tu objetivo es acompañar al estudiante en su proceso de aprendizaje, ayudarle a organizar sus estudios y mejorar su comprensión de los temas académicos.
        
        """

        # 3. MANEJAR LA MEMORIA (HISTORIAL DE SESIÓN)
        # Si no existe el historial en la sesión, lo inicializamos
        if 'chat_history' not in session:
            session['chat_history'] = []

        # Estructuramos el mensaje del usuario para la API de Gemini
        mensaje_usuario = {"role": "user", "parts": [{"text": texto_usuario}]}
        
        # Creamos el paquete de 'contents' que incluye: Instrucciones + Historial + Pregunta Actual
        # Limitamos el historial a los últimos 6 mensajes para no saturar la memoria
        historial_reciente = session['chat_history'][-6:]
        
        payload_ia = [
            {"role": "user", "parts": [{"text": f"INSTRUCCIONES DE SISTEMA: {system_instruction}"}]},
            *historial_reciente,
            mensaje_usuario
        ]

        # 4. LLAMADA A LA IA
        response = client.models.generate_content(
            model="gemini-2.5-flash", 
            contents=payload_ia
        )
        
        # 5. ACTUALIZAR MEMORIA
        # Guardamos la pregunta y la respuesta en la sesión del navegador
        session['chat_history'].append(mensaje_usuario)
        session['chat_history'].append({"role": "model", "parts": [{"text": response.text}]})
        session.modified = True # Forzamos a Flask a guardar los cambios en la sesión
        
        return jsonify({"mensaje": response.text})

    except Exception as e:
        print(f"Error detallado en Gemini: {e}")
        return jsonify({"mensaje": "Lo siento, tuve un problema interno al procesar tu duda."}), 500

# --- RUTA DEL CHAT ESPECÍFICO DE CLASES (CON ARCHIVOS + INTERNET) ---
@app.route("/consulta_clase", methods=["POST"])
def consulta_clase():
    if 'loggedin' not in session:
        return jsonify({"mensaje": "Debes iniciar sesión."}), 401

    import time

    texto_usuario = request.form.get("consulta", "").strip()
    materia = request.form.get("materia", "General")

    if not texto_usuario:
        return jsonify({"mensaje": "No escribiste nada..."}), 400

    try:
        user_name = session.get('user_name', 'Estudiante')

        # Rutas absolutas — funcionan sin importar desde dónde se corra Flask
        ARCHIVOS_CLASE = [
            os.path.join(BASE_DIR, "static", "clases", "liderazgo", "1.4 Comunicación organizacional.pdf"),
            os.path.join(BASE_DIR, "static", "clases", "liderazgo", "Tipos de comunicación organizacional  Comunicación empresarial - LearnFree en Español (720p, h264, youtube).mp4"),
        ]
        MIME_MAP = {".pdf": "application/pdf", ".mp4": "video/mp4", ".mov": "video/quicktime"}

        def _mime(p):
            return MIME_MAP.get(os.path.splitext(p)[1].lower(), "application/octet-stream")

        # Subir archivos a Gemini para que Kady los pueda leer
        partes_archivos = []
        for ruta in ARCHIVOS_CLASE:
            if os.path.exists(ruta):
                try:
                    archivo = client.files.upload(
                        file=ruta,
                        config=types.UploadFileConfig(mime_type=_mime(ruta))
                    )
                    # Los videos necesitan tiempo de procesamiento
                    if _mime(ruta).startswith("video/"):
                        intentos = 0
                        while getattr(archivo.state, 'name', '') == "PROCESSING" and intentos < 30:
                            time.sleep(5)
                            archivo = client.files.get(name=archivo.name)
                            intentos += 1
                    partes_archivos.append(
                        types.Part.from_uri(file_uri=archivo.uri, mime_type=_mime(ruta))
                    )
                    print(f"[clase] ✓ Archivo subido: {os.path.basename(ruta)}")
                except Exception as e:
                    print(f"[clase] ✗ No se pudo subir {os.path.basename(ruta)}: {e}")
            else:
                print(f"[clase] ✗ Archivo no encontrado: {ruta}")

        notas_clase = session.get('notas_estudiante', '')
        system_instruction = f"""
Eres Kady, tutora académica experta en {materia}. Hablas con {user_name}.
Tienes acceso al PDF "Comunicación Organizacional" y al video de la clase.
Úsalos siempre para fundamentar tus respuestas.

Instrucciones:
- Resumen del PDF: estructura la respuesta por secciones del documento.
- Resumen del video: incluye los temas por minutaje aproximado.
- Resumen de ambos: primero video, luego PDF, luego síntesis de 2-3 líneas.
- Conceptos clave: lista 6-8 conceptos del PDF y video con definición breve.
- Preguntas libres: responde basándote en los archivos y búsqueda web.
- Usa viñetas para mayor claridad. Sé concisa pero profunda.
{f"Nota del estudiante: {notas_clase}" if notas_clase else ""}
"""
        partes = (
            [types.Part.from_text(text=system_instruction)]
            + partes_archivos
            + [types.Part.from_text(text=texto_usuario)]
        )
        contenido = [types.Content(role="user", parts=partes)]
        config = types.GenerateContentConfig(
            tools=[{"google_search": {}}],
            temperature=0.7
        )
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=contenido,
            config=config
        )

        if any(p in texto_usuario.lower() for p in ["difícil", "no entiendo", "no comprendo", "ayuda", "confuso"]):
            session['notas_estudiante'] = f"El estudiante tuvo dificultades en {materia}."
            session.modified = True

        return jsonify({"mensaje": response.text})

    except Exception as e:
        print(f"[clase] Error: {e}")
        return jsonify({"mensaje": f"Hubo un problema al procesar tu consulta: {str(e)}"}), 500

# --- RUTAS DE LOGIN Y NAVEGACIÓN ---
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario_input = request.form.get("usuario")
        password_input = request.form.get("password")

        cursor = mysql.connection.cursor()
        # Buscamos al usuario por su nombre de usuario único
        cursor.execute("SELECT * FROM usuarios WHERE usuario = %s", (usuario_input,))
        user = cursor.fetchone()
        cursor.close()

        if user:
            # Compatibilidad de hashes: convertimos $2y$ (PHP) a $2b$ (Python)
            hash_db = user['pass_hash'].replace('$2y$', '$2b$')
            if bcrypt.checkpw(password_input.encode('utf-8'), hash_db.encode('utf-8')):
                session['loggedin'] = True
                session['user_id'] = user['id']
                session['user_name'] = user['nombre']
                # Limpiamos el chat al iniciar una nueva sesión
                session['chat_history'] = [] 
                return redirect(url_for('prin'))
            else:
                flash("Contraseña incorrecta", "danger")
        else:
            flash("Usuario no encontrado", "danger")
            
    return render_template("login.html")

@app.route("/prin")
def prin():
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    return render_template("prin_a.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/portal_alumno')
def portal_alumno():
    return redirect(url_for('alumno_portal'))
    
    # Tu portal-alumno.html espera una variable 'info' con los estilos de aprendizaje.
    # Por ahora pasamos un diccionario simulado, pero luego lo conectarás a MySQL.
    info_alumno = {
        'resultado_final': 'Visual', 
        'visual': 50, 'auditivo': 30, 'kinestesico': 20
    }
    return render_template("portal-alumno.html", info=info_alumno)

@app.route("/portal-maestro")
def maestro_portal(): 
    # En gestion.html haces referencia a url_for('maestro_portal')
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    return render_template("portal_m.html", alumnos=[]) 

@app.route("/encuesta")
def encuesta():
    return render_template("encuesta.html")
    
@app.route("/gestion")
def gestion():
    # Tu gestion.html espera listas de 'carreras' y 'grupos_lista' para mostrarlas
    return render_template("gestion.html", carreras=[], grupos_lista=[])
    
@app.route('/clase_calculo')
def clase_calculo():
    clase_data = {'id': 1, 'titulo': 'Cálculo de Varias Variables'}
    return render_template('clase_calculo.html', clase=clase_data)

@app.route('/clase_frameworks')
def clase_frameworks():
    clase_data = {'id': 2, 'titulo': 'Frameworks'}
    # Fíjate que el archivo se llama "clase_franworks.html", así lo definiste
    return render_template('clase_franworks.html', clase=clase_data)

@app.route("/generar_test", methods=["POST"])
def generar_test():
    if 'loggedin' not in session:
        return jsonify({"error": "Debes iniciar sesión."}), 401

    import re, json, time

    # Recibir la materia y archivos desde el HTML que hace el request
    carpeta = request.form.get("carpeta", "liderazgo")
    pdf     = request.form.get("pdf",     "1.4 Comunicación organizacional.pdf")
    video   = request.form.get("video",   "Tipos de comunicación organizacional  Comunicación empresarial - LearnFree en Español (720p, h264, youtube).mp4")
    materia = request.form.get("materia", "la clase")

    ARCHIVOS_CLASE = [
        os.path.join(BASE_DIR, "static", "clases", carpeta, pdf),
        os.path.join(BASE_DIR, "static", "clases", carpeta, video),
    ]
    MIME_MAP = {".pdf": "application/pdf", ".mp4": "video/mp4", ".mov": "video/quicktime"}

    def _mime(p):
        return MIME_MAP.get(os.path.splitext(p)[1].lower(), "application/octet-stream")

    partes = []
    for ruta in ARCHIVOS_CLASE:
        if os.path.exists(ruta):
            try:
                archivo = client.files.upload(
                    file=ruta,
                    config=types.UploadFileConfig(mime_type=_mime(ruta))
                )
                if _mime(ruta).startswith("video/"):
                    intentos = 0
                    while getattr(archivo.state, 'name', '') == "PROCESSING" and intentos < 30:
                        time.sleep(5)
                        archivo = client.files.get(name=archivo.name)
                        intentos += 1
                partes.append(types.Part.from_uri(file_uri=archivo.uri, mime_type=_mime(ruta)))
                print(f"[test] ✓ {os.path.basename(ruta)}")
            except Exception as e:
                print(f"[test] ✗ Error subiendo {os.path.basename(ruta)}: {e}")
        else:
            print(f"[test] ✗ No encontrado: {ruta}")

    prompt_test = f"""
Eres un evaluador académico especializado en {materia}.
Basándote ÚNICAMENTE en los materiales proporcionados (PDF y video),
genera un test de exactamente 5 preguntas de opción múltiple sobre {materia}.

Responde ÚNICAMENTE con JSON válido, sin texto adicional, sin bloques de código markdown.

Formato exacto:
{{
  "titulo": "Test: {materia}",
  "preguntas": [
    {{
      "id": 1,
      "pregunta": "Texto de la pregunta",
      "opciones": {{"A": "...", "B": "...", "C": "...", "D": "..."}},
      "correcta": "B",
      "explicacion": "Explicación breve de por qué esta opción es correcta."
    }}
  ]
}}

Genera exactamente 5 preguntas variadas que evalúen comprensión y aplicación de {materia}.
"""

    try:
        partes_completas = [types.Part.from_text(text=prompt_test)] + partes
        contenido = [types.Content(role="user", parts=partes_completas)]
        config = types.GenerateContentConfig(
            response_mime_type="application/json",
            temperature=0.4
        )
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=contenido,
            config=config
        )
        raw = response.text.strip()
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)
        test_data = json.loads(raw)
        return jsonify(test_data)

    except json.JSONDecodeError as e:
        print(f"[test] JSON inválido: {e} | Respuesta: {response.text[:400]}")
        return jsonify({"error": "Gemini no devolvió formato válido. Intenta de nuevo."}), 500
    except Exception as e:
        print(f"[test] Error: {e}")
        return jsonify({"error": f"Error al generar el test: {str(e)}"}), 500


@app.route('/clase_liderazgo')
def clase_liderazgo():
    clase_data = {'id': 3, 'titulo': 'Liderazgo y Equipos de Alto Rendimiento', 'modulo': 'Módulo 1'}
    return render_template('clase_Liderazgo.html', clase=clase_data, lista=[clase_data])  # ← agrega lista

@app.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        nombre    = request.form.get("nombre")
        apellido1 = request.form.get("apellido1")
        apellido2 = request.form.get("apellido2")
        matricula = request.form.get("matricula")
        correo    = request.form.get("correo")
        celular   = request.form.get("celular")
        rol       = request.form.get("rol")

        # Intentar guardar en DB (opcional por ahora)
        try:
            cursor = mysql.connection.cursor()
            cursor.execute("""
                INSERT INTO usuarios (nombre, apellido, matricula, correo, celular, rol)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (nombre, f"{apellido1} {apellido2}", matricula, correo, celular, rol))
            mysql.connection.commit()
            cursor.close()
        except Exception as e:
            print(f"[registro] Error DB (se ignora por ahora): {e}")

        # ✅ Redirige SIEMPRE según el rol, con o sin DB
        if rol == "maestro":
            return redirect(url_for('maestro_prin'))
        else:
            return redirect(url_for('prin'))

    return render_template("registro.html")

@app.route("/prin_m")
def maestro_prin():
    return render_template("prin_m.html")

@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    # El servidor corre en el puerto 8080 con modo debug para desarrollo
    app.run(port=8080, debug=True)
