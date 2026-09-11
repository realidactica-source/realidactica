from __future__ import annotations

import os
import time
from pathlib import Path

import bcrypt
import MySQLdb


BASE_DIR = Path(__file__).resolve().parents[1]
REQUIRED_VARIABLES = (
    "MYSQL_HOST",
    "MYSQL_PORT",
    "MYSQL_USER",
    "MYSQL_PASSWORD",
    "MYSQL_DB",
)


def connect_with_retry(attempts: int = 20) -> MySQLdb.Connection:
    missing = [name for name in REQUIRED_VARIABLES if not os.getenv(name)]
    if missing:
        raise RuntimeError(f"Faltan variables de base de datos: {', '.join(missing)}")

    last_error: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            return MySQLdb.connect(
                host=os.environ["MYSQL_HOST"],
                port=int(os.environ["MYSQL_PORT"]),
                user=os.environ["MYSQL_USER"],
                passwd=os.environ["MYSQL_PASSWORD"],
                db=os.environ["MYSQL_DB"],
                charset="utf8mb4",
                connect_timeout=10,
            )
        except MySQLdb.Error as error:
            last_error = error
            if attempt < attempts:
                time.sleep(min(attempt, 5))
    raise RuntimeError("MySQL no estuvo disponible durante el arranque") from last_error


def seed_demo_user(connection: MySQLdb.Connection) -> bool:
    password = os.getenv("BOOTSTRAP_DEMO_PASSWORD", "")
    if not password:
        return False
    if len(password) < 16:
        raise RuntimeError("BOOTSTRAP_DEMO_PASSWORD debe tener al menos 16 caracteres")

    username = os.getenv("BOOTSTRAP_DEMO_USERNAME", "alumno.demo").strip()[:50]
    email = os.getenv("BOOTSTRAP_DEMO_EMAIL", "alumno.demo@realidactica.local").strip().lower()[:150]
    role = os.getenv("BOOTSTRAP_DEMO_ROLE", "alumno").strip().lower()
    if role not in {"alumno", "maestro"}:
        raise RuntimeError("BOOTSTRAP_DEMO_ROLE debe ser alumno o maestro")

    first_name = "Docente" if role == "maestro" else "Alex"
    password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    cursor = connection.cursor()
    cursor.execute(
        "SELECT id FROM usuarios WHERE usuario = %s OR correo = %s LIMIT 1",
        (username, email),
    )
    existing = cursor.fetchone()
    if existing:
        cursor.execute(
            "UPDATE usuarios SET nombre=%s, apellido=%s, correo=%s, usuario=%s, pass_hash=%s, "
            "rol=%s, activo=1, token_confirmacion=NULL, token_creado=NULL WHERE id=%s",
            (first_name, "Demo", email, username, password_hash, role, existing[0]),
        )
    else:
        cursor.execute(
            "INSERT INTO usuarios (nombre, apellido, correo, usuario, pass_hash, rol, activo) "
            "VALUES (%s, %s, %s, %s, %s, %s, 1)",
            (first_name, "Demo", email, username, password_hash, role),
        )
    cursor.close()
    return True


def main() -> None:
    statements = [
        statement.strip()
        for statement in (BASE_DIR / "schema.sql").read_text(encoding="utf-8").split(";")
        if statement.strip()
    ]
    connection = connect_with_retry()
    try:
        cursor = connection.cursor()
        for statement in statements:
            cursor.execute(statement)
        cursor.close()
        seeded = seed_demo_user(connection)
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()
    print(f"Esquema verificado: {len(statements)} sentencias aplicadas.")
    if seeded:
        print("Cuenta de demostración verificada.")


if __name__ == "__main__":
    main()
