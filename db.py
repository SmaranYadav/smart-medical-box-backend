import ssl
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlsplit

import psycopg2
import pymysql
from psycopg2.extras import RealDictCursor
from pymysql.cursors import DictCursor

from config import DATABASE_URL, MYSQL_URL


def get_connection():
    if MYSQL_URL:
        parsed = urlsplit(MYSQL_URL)
        if parsed.scheme not in ("mysql", "mysql+pymysql"):
            raise RuntimeError(
                "MYSQL_URL must use the mysql:// or mysql+pymysql:// scheme."
            )

        database_name = unquote(parsed.path.lstrip("/"))
        if not parsed.hostname or not parsed.username or not database_name:
            raise RuntimeError(
                "MYSQL_URL must include a host, username, and database name."
            )

        query = parse_qs(parsed.query)
        ssl_mode = query.get("ssl-mode", query.get("ssl_mode", [""]))[0].lower()
        ssl_enabled = (
            ssl_mode in ("required", "verify_ca", "verify_identity") or
            query.get("ssl", [""])[0].lower() in ("1", "true", "yes")
        )
        ssl_ca = query.get("ssl-ca", query.get("ssl_ca", [None]))[0]
        ssl_options = (
            ssl.create_default_context(cafile=ssl_ca)
            if ssl_enabled and ssl_ca else
            ssl.create_default_context()
            if ssl_enabled else
            None
        )

        return pymysql.connect(
            host=parsed.hostname,
            port=parsed.port or 3306,
            user=unquote(parsed.username),
            password=unquote(parsed.password or ""),
            database=database_name,
            charset="utf8mb4",
            cursorclass=DictCursor,
            connect_timeout=10,
            ssl=ssl_options,
        )

    if not DATABASE_URL:
        raise RuntimeError("Set MYSQL_URL or DATABASE_URL to connect to a database.")

    return psycopg2.connect(DATABASE_URL, connect_timeout=10)


def get_cursor(connection):
    if MYSQL_URL:
        return connection.cursor()
    return connection.cursor(cursor_factory=RealDictCursor)


def initialize_database():
    schema_file = "schema.mysql.sql" if MYSQL_URL else "schema.sql"
    schema = Path(__file__).with_name(schema_file).read_text(encoding="utf-8")
    connection = get_connection()
    cursor = get_cursor(connection)

    try:
        for statement in schema.split(";"):
            if statement.strip():
                cursor.execute(statement)
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        cursor.close()
        connection.close()


if __name__ == "__main__":
    try:
        connection = get_connection()
        print(f"{'MySQL' if MYSQL_URL else 'PostgreSQL'} connected successfully!")
        connection.close()
        initialize_database()
        print("Database schema initialized successfully!")
    except (pymysql.MySQLError, psycopg2.Error) as error:
        print("Database connection failed:", error)
