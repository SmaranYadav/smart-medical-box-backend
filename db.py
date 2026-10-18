import psycopg2
from config import DATABASE_URL


def get_connection():
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL is missing.")
    return psycopg2.connect(DATABASE_URL, connect_timeout=10)


if __name__ == "__main__":
    try:
        connection = get_connection()
        print("PostgreSQL connected successfully!")
        connection.close()
    except psycopg2.Error as error:
        print("Database connection failed:", error)