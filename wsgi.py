from pathlib import Path

from app import app
from db import get_connection
from scheduler import start_scheduler

schema = Path(__file__).with_name("schema.sql").read_text(encoding="utf-8")
connection = get_connection()
cursor = connection.cursor()
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

start_scheduler()
