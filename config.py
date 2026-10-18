
import os
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST", os.getenv("MYSQLHOST", "localhost")),
    "user": os.getenv("DB_USER", os.getenv("MYSQLUSER", "root")),
    "password": os.getenv("DB_PASSWORD", os.getenv("MYSQLPASSWORD", "")),
    "database": os.getenv(
        "DB_NAME", os.getenv("MYSQLDATABASE", "smart_medical_box")
    ),
    "port": int(os.getenv("DB_PORT", os.getenv("MYSQLPORT", "3306"))),
}
