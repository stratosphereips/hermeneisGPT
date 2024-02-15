"""
HermeneisGPT library of functions to handle SQLite DB transactions.
"""

import sqlite3


def get_db_connection(db_path):
    """
    Create SQLite DB connection.

    Args:
    db_path (str)

    Returns:
    connection
    cursor

    Raises:
    sqlite3.DatabaseError
    """
    try:
        # Connect to the SQLite database
        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()
        return connection, cursor
    except sqlite3.DatabaseError as e:
        print(f"Database error: {e}")
        raise
