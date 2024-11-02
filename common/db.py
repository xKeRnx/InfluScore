# common/db.py
import mysql.connector
from common.config import DB_CONFIG

def get_db_connection():
    """Establishes a connection to the database."""
    return mysql.connector.connect(**DB_CONFIG)
