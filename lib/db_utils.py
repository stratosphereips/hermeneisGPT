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


def check_table_exists(cursor, table_name):
    """
    Check a table exists in the SQLite database.

    Parameters:
    cursor
    table_name

    Returns:
    bool

    Raises:
    sqlite3.OperationalError
    """
    try:
        cursor.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name=?", (table_name,))

        # fetchone() returns a tuple (n, ) where n is 0 if the table does not exist, and 1 if it does.
        return bool(cursor.fetchone()[0] == 1)
    except sqlite3.OperationalError as e:
        raise sqlite3.OperationalError(e)


def read_sql_from_file(file_path):
    """
    Read SQL commands from a file.
    """
    with open(file_path, 'r') as sql_file:
        return sql_file.read()


def create_tables_from_schema(connection, cursor, schema_file_path):
    """
    Create tables from a schema file. Assumes 'if not exist'
    intruction in the sql schema.

    Parameters:
    cursor
    schema_file_path
    """
    schema_sql = read_sql_from_file(schema_file_path)
    try:
        cursor.executescript(schema_sql)
        connection.commit()
    except sqlite3.OperationalError as e:
        connection.rollback()
        raise sqlite3.OperationalError(e)
