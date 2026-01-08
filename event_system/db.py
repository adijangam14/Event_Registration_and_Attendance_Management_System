# db.py
# Handles the connection to the Oracle database.

import oracledb
from .config import DB_CONFIG

def get_connection():
    """
    Establishes a connection to the Oracle database using THIN mode.
    No Oracle Instant Client is required.
    """
    try:
        connection = oracledb.connect(
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            dsn=DB_CONFIG["dsn"]
        )
        return connection

    except oracledb.DatabaseError as e:
        print(f"Error connecting to Oracle Database: {e}")
        return None


# Test block
if __name__ == "__main__":
    conn = get_connection()
    if conn:
        print("Successfully connected to Oracle Database.")
        print("Oracle Database version:", conn.version)
        conn.close()
    else:
        print("Failed to connect to the database.")
