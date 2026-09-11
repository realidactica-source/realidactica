from __future__ import annotations

import os
import time
from pathlib import Path

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
        connection.commit()
        cursor.close()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()
    print(f"Esquema verificado: {len(statements)} sentencias aplicadas.")


if __name__ == "__main__":
    main()
