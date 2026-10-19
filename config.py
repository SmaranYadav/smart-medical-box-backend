
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
MYSQL_URL = os.getenv("MYSQL_URL")
