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


def check_channel_exists(cursor, channel_name):
    """
    Check if a given channel_name exists on the DB.

    Args:
    cursor (sqlite3.Cursor)
    channel_name (str)

    Returns:
    channel_id

    Raises:
    sqlite3 errors
    """
    try:
        query = "SELECT channel_id FROM channels WHERE channel_name = ?"
        cursor.execute(query, (channel_name,))
        result = cursor.fetchone()

        if result:
            return result[0]
        else:
            return None
    except sqlite3.OperationalError as e:
        raise sqlite3.OperationalError(e)
    except sqlite3.IntegrityError as e:
        raise sqlite3.IntegrityError(e)
    except sqlite3.ProgrammingError as e:
        raise sqlite3.ProgrammingError(e)
    except sqlite3.DatabaseError as e:
        raise sqlite3.DatabaseError(e)


def has_channel_messages(cursor, channel_name):
    """
    Check if there are any messages for the given channel.

    Args:
    cursor (sqlite3.Cursor)
    channel_name (str)

    Returns:
    bool

    Raises:
    sqlite3 errors
    """
    try:
        channel_id = check_channel_exists(cursor, channel_name)

        if channel_id is None:
            return False

        query = "SELECT count(*) FROM messages WHERE channel_id= ?"
        cursor.execute(query, (channel_id,))
        result = cursor.fetchone()

        return bool(result) and result[0] > 0
    except sqlite3.OperationalError as e:
        raise sqlite3.OperationalError(e)
    except sqlite3.IntegrityError as e:
        raise sqlite3.IntegrityError(e)
    except sqlite3.ProgrammingError as e:
        raise sqlite3.ProgrammingError(e)
    except sqlite3.DatabaseError as e:
        raise sqlite3.DatabaseError(e)
