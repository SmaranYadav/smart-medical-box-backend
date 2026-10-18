import mysql.connector
from config import DB_CONFIG


def get_connection():
    return mysql.connector.connect(**DB_CONFIG)


if __name__ == "__main__":
    try:
        connection = get_connection()
        print("MySQL connected successfully!")
        connection.close()
    except mysql.connector.Error as error:
        print("Database connection failed:", error)