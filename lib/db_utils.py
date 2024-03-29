"""
HermeneisGPT library of functions to handle SQLite DB transactions.
"""

import sqlite3
from datetime import datetime


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


def insert_translation_parameters(cursor, translation_tool_name, translation_tool_commit, translation_model, translation_config_sha256, translation_config):
    """
    Inserts a new entry into the translation_parameters table.

    Parameters:
    cursor
    translation_tool_name
    translation_tool_commit
    translation_model
    translation_config_sha256
    translation_config

    Returns:
    lastrowid
    """
    insert_query = """
    INSERT OR IGNORE INTO translation_parameters
    (translation_tool_name, translation_tool_commit, translation_model, translation_config_sha256, translation_config)
    VALUES (?, ?, ?, ?, ?)
    """
    try:
        cursor.execute(insert_query, (translation_tool_name, translation_tool_commit, translation_model, translation_config_sha256, translation_config))
        # Retrieve the ID of the existing or newly inserted row
        select_query = """
        SELECT translation_parameters_id FROM translation_parameters
        WHERE translation_tool_name=? AND translation_tool_commit=? AND translation_model=? AND translation_config_sha256=? AND translation_config=?
        """
        cursor.execute(select_query, (translation_tool_name, translation_tool_commit, translation_model, translation_config_sha256, translation_config))
        translation_parameters_id = cursor.fetchone()[0]

        return translation_parameters_id
    except sqlite3.IntegrityError as e:
        raise sqlite3.IntegrityError(f"Integrity error inserting into database: {e}")
    except sqlite3.OperationalError as e:
        raise sqlite3.OperationalError(f"Operational error inserting into database: {e}")


def get_channel_messages(cursor, channel_name):
    """
    Function to retrieve messages from DB matching a channel name.

    Parameters:
    cursor
    channel_name

    Returns:
    messages

    Raises:
    sqlerrors various
    """
    query = """
    SELECT m.message_id, m.message_text
    FROM messages m
    JOIN channels c ON m.channel_id = c.channel_id
    WHERE c.channel_name = ?
    """

    try:
        cursor.execute(query, (channel_name,))
        messages = cursor.fetchall()
        return messages
    except sqlite3.IntegrityError:
        raise
    except sqlite3.OperationalError:
        raise
    except sqlite3.ProgrammingError:
        raise
    except sqlite3.DatabaseError:
        raise


def exists_translation_for_message(cursor, message_id, translation_parameters_id):
    """
    Check if a translation exists for the message with given
    translation_parameters_id.

    Parameters:
    cursor
    message_id
    translation_parameters_id

    Returns:
    bool

    Raises:
    sqlerrors various
    """
    query = """
    SELECT COUNT(*)
    FROM message_translation
    WHERE message_id = ? AND translation_parameters_id = ?
    """

    try:
        cursor.execute(query, (message_id, translation_parameters_id,))
        return bool(cursor.fetchone()[0] > 0)
    except sqlite3.IntegrityError:
        raise
    except sqlite3.OperationalError:
        raise
    except sqlite3.ProgrammingError:
        raise
    except sqlite3.DatabaseError:
        raise


def upsert_message_translation(cursor, message_id, translation_parameters_id, translation_text):
    """
    Inserts or updates a translation in the message_translations table
    based on the uniqueness of message_id and translation_parameters_id.

    Parameters:
    cursor
    message_id
    translation_parameters_id
    translation_text

    Returns:


    Raises:
    sqlerrors various
    """
    translation_timestamp = datetime.utcnow().isoformat()

    query = """
    INSERT OR REPLACE INTO message_translation (translation_id, message_id, translation_parameters_id, translation_text, translation_timestamp)
    VALUES (
        (SELECT translation_id FROM message_translation WHERE message_id = ? AND translation_parameters_id = ?),
        ?, ?, ?, ?
    )
    """
    try:
        params = (
            message_id,
            translation_parameters_id,
            message_id,
            translation_parameters_id,
            translation_text,
            translation_timestamp
        )
        cursor.execute(query, params)

        return cursor.lastrowid
    except sqlite3.IntegrityError:
        raise
    except sqlite3.OperationalError:
        raise
    except sqlite3.DatabaseError:
        raise
