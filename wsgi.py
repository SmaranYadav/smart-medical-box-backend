from app import app
from db import initialize_database
from scheduler import start_scheduler

initialize_database()
start_scheduler()
