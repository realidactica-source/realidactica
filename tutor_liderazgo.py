import os
import re
import json
import time
from flask import Blueprint, request, jsonify, session
from google import genai
from google.genai import types

tutor_clase_bp = Blueprint('tutor_clase', __name__)

client = genai.Client(api_key="AIzaSyDNrJOrLtCvfBuvPzxs9MfktQ5w9QAeIls")

# ─────────────────────────────────────────────────────────────────────────────
# CACHÉ EN MEMORIA
# ─────────────────────────────────────────────────────────────────────────────
_cache_archivos: dict[str, str] = {}

ARCHIVOS_CLASE = [
    "static/clases/liderazgo/1.4 Comunicación organizacional.pdf",
    "static/clases/liderazgo/Tipos de comunicación organizacional  Comunicación empresarial - LearnFree en Español (720p, h264, youtube).mp4",
]

MIME_MAP = {
    ".pdf":  "application/pdf",
    ".mp4":  "video/mp4",
    ".mov":  "video/quicktime",
    ".avi":  "video/x-msvideo",
    ".png":  "image/png",
    ".jpg":  "image/jpeg",
    ".jpeg": "image/jpeg",
    ".webp": "image/webp",
}


def _mime(path: str) -> str:
    ext = os.path.splitext(path)[1].lower()
    return MIME_MAP.get(ext, "application/octet-stream")


def _subir_o_recuperar(path: str) -> str | None:
    if not os.path.exists(path):
        print(f"[tutor] Archivo no encontrado: {path}")
        return None

    if path in _cache_archivos:
        print(f"[tutor] Reutilizando URI cacheado: {os.path.basename(path)}")
        return _cache_archivos[path]

    print(f"[tutor] Subiendo a Gemini: {os.path.basename(path)}")
    mime = _mime(path)
    archivo_gemini = client.files.upload(
        file=path,
        config=types.UploadFileConfig(mime_type=mime),
    )

    if mime.startswith("video/"):
        intentos = 0
        while archivo_gemini.state.name == "PROCESSING" and intentos < 30:
            time.sleep(5)
            archivo_gemini = client.files.get(name=archivo_gemini.name)
            intentos += 1
            print(f"[tutor] Procesando video... intento {intentos}")

        if archivo_gemini.state.name != "ACTIVE":
            print(f"[tutor] Error: video en estado {archivo_gemini.state.name}")
            return None

    _cache_archivos[path] = archivo_gemini.uri
    return archivo_gemini.uri


def _partes_archivos() -> list:
    """Devuelve las partes de los archivos de clase para el contexto."""
    partes = []
    for ruta in ARCHIVOS_CLASE:
        uri = _subir_o_recuperar(ruta)
        if uri:
            partes.append(types.Part.from_uri(file_uri=uri, mime_type=_mime(ruta)))
    return partes


# ─────────────────────────────────────────────────────────────────────────────
# RUTA 1: Chat general
# ─────────────────────────────────────────────────────────────────────────────
@tutor_clase_bp.route("/consulta_clase", methods=["POST"])
def consulta_clase():
    if 'loggedin' not in session:
        return jsonify({"mensaje": "Debes iniciar sesión."}), 401

    texto_usuario = request.form.get("consulta", "").strip()
    materia = request.form.get("materia", "General")

    if not texto_usuario:
        return jsonify({"mensaje": "No escribiste nada..."}), 400

    try:
        user_name = session.get('user_name', 'Estudiante')

        system_instruction = f"""
Eres Kady, un tutor académico experto en Liderazgo y Equipos de Alto Rendimiento.
Estás ayudando a {user_name}.

Personalidad: analítico, fomenta el pensamiento crítico y relaciona la teoría con 
ejemplos del mundo real y del ámbito profesional/tecnológico.

Instrucciones generales:
- Responde dudas sobre {materia}.
- Tienes acceso al PDF "Comunicación Organizacional" y al video de la clase.
- Úsalos para fundamentar tus respuestas (cita minutaje o sección cuando aplique).
- Sé conciso pero profundo. Usa viñetas para mayor claridad.
- Si el estudiante pregunta algo fuera del temario, redirige amablemente.

Instrucciones para RESÚMENES:
- "resumen de ambos": resume VIDEO (minutaje) + PDF (secciones) + síntesis final.
- "resumen del PDF": solo el documento, estructurado por secciones.
- "resumen del video": solo el video, con momentos clave y minutaje.

PALABRAS CLAVE:
- "concepto clave / conceptos clave / dame el concepto clave del tema":
    Lista 6-8 conceptos del PDF Y del video.
    Formato: 🔑 **Nombre** (fuente: PDF / Video / Ambos) — definición breve + ejemplo.
"""
        notas = session.get('notas_estudiante', '')
        if notas:
            system_instruction += f"\nNota sobre el estudiante: {notas}"

        partes_contexto = [types.Part.from_text(text=system_instruction)] + _partes_archivos()
        partes_pregunta = [types.Part.from_text(text=texto_usuario)]

        contenido = [
            types.Content(role="user", parts=partes_contexto),
            types.Content(role="user", parts=partes_pregunta),
        ]

        configuracion = types.GenerateContentConfig(
            tools=[{"google_search": {}}],
            temperature=0.7,
        )

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=contenido,
            config=configuracion,
        )

        palabras_dificultad = ["difícil", "no entiendo", "no comprendo", "ayuda", "confuso"]
        if any(p in texto_usuario.lower() for p in palabras_dificultad):
            session['notas_estudiante'] = f"El estudiante tuvo dificultades recientes con temas de {materia}."
            session.modified = True

        return jsonify({"mensaje": response.text})

    except Exception as e:
        print(f"[tutor] Error: {e}")
        return jsonify({"mensaje": f"Error al procesar tu consulta: {str(e)}"}), 500


# ─────────────────────────────────────────────────────────────────────────────
# RUTA 2: Generar test — devuelve JSON estructurado para el frontend dinámico
# ─────────────────────────────────────────────────────────────────────────────
@tutor_clase_bp.route("/generar_test", methods=["POST"])
def generar_test():
    if 'loggedin' not in session:
        return jsonify({"error": "Debes iniciar sesión."}), 401

    try:
        prompt_test = """
Eres un evaluador académico. Basándote ÚNICAMENTE en el PDF y el video proporcionados,
genera un test de exactamente 5 preguntas de opción múltiple.

RESPONDE ÚNICAMENTE con JSON válido. Sin texto extra, sin bloques de código, sin comillas triples.

Formato exacto:
{
  "titulo": "Test: Liderazgo y Comunicación Organizacional",
  "preguntas": [
    {
      "id": 1,
      "pregunta": "Texto de la pregunta",
      "opciones": {
        "A": "Primera opción",
        "B": "Segunda opción",
        "C": "Tercera opción",
        "D": "Cuarta opción"
      },
      "correcta": "B",
      "explicacion": "Explicación breve de por qué esta opción es correcta."
    }
  ]
}

Genera exactamente 5 preguntas variadas que cubran diferentes temas.
Evalúa comprensión y aplicación, no solo memorización.
"""
        partes = [types.Part.from_text(text=prompt_test)] + _partes_archivos()
        contenido = [types.Content(role="user", parts=partes)]
        configuracion = types.GenerateContentConfig(temperature=0.5)

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=contenido,
            config=configuracion,
        )

        raw = response.text.strip()
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)

        test_data = json.loads(raw)
        return jsonify(test_data)

    except json.JSONDecodeError as e:
        print(f"[test] Error JSON: {e}")
        return jsonify({"error": "No se pudo generar el test. Intenta de nuevo."}), 500
    except Exception as e:
        print(f"[test] Error: {e}")
        return jsonify({"error": f"Error: {str(e)}"}), 500