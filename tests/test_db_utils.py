# pylint: disable=missing-docstring
# pylint: disable=line-too-long
import pytest
import sys
import sqlite3
import tempfile
from os import path
from datetime import datetime
from os import remove
from unittest.mock import patch
from unittest.mock import MagicMock
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from lib.db_utils import get_db_connection
from lib.db_utils import check_channel_exists
from lib.db_utils import has_channel_messages
from lib.db_utils import check_table_exists
from lib.db_utils import read_sql_from_file
from lib.db_utils import create_tables_from_schema
from lib.db_utils import insert_translation_parameters
from lib.db_utils import get_channel_messages
from lib.db_utils import exists_translation_for_message
from lib.db_utils import upsert_message_translation


def test_get_db_connection_success():
    """Test successful DB connection."""
    db_path = ":memory:"  # Use an in-memory database for testing
    connection, cursor = get_db_connection(db_path)
    assert connection is not None
    assert isinstance(cursor, sqlite3.Cursor)
    connection.close()


def test_get_db_connection_failure():
    """Test failed DB connection with a bad path."""
    db_path = "/invalid/path/to/database.db"
    with pytest.raises(sqlite3.DatabaseError):
        get_db_connection(db_path)


@pytest.fixture
def setup_database():
    """Setup an in-memory database and return a cursor."""
    connection = sqlite3.connect(":memory:")
    cursor = connection.cursor()

    # Create the schema
    cursor.execute("CREATE TABLE channels (channel_id INTEGER PRIMARY KEY, channel_name TEXT UNIQUE)")
    cursor.execute("CREATE TABLE messages (message_id INTEGER PRIMARY KEY, channel_id INTEGER, message_text TEXT)")
    cursor.execute("CREATE TABLE translation_parameters (translation_parameters_id INTEGER PRIMARY KEY, translation_tool_name TEXT)")
    cursor.execute("CREATE TABLE message_translation (translation_id INTEGER PRIMARY KEY, message_id INTEGER, translation_parameters_id INTEGER, translation_text TEXT, translation_timestamp DATETIME, UNIQUE(message_id, translation_parameters_id), FOREIGN KEY (message_id) REFERENCES messages(message_id), FOREIGN KEY (translation_parameters_id) REFERENCES translation_parameters(translation_parameters_id))")

    # Insert test data
    cursor.execute("INSERT INTO channels (channel_name) VALUES ('test_channel')")
    cursor.execute("INSERT INTO channels (channel_name) VALUES ('existing_channel')")
    cursor.execute("INSERT INTO channels (channel_name) VALUES ('empty_channel')")
    channel_id = cursor.execute("SELECT channel_id FROM channels WHERE channel_name = 'existing_channel'").fetchone()[0]
    cursor.execute("INSERT INTO messages (channel_id, message_text) VALUES (?, 'Test message')", (channel_id,))
    message_id = cursor.lastrowid
    cursor.execute("INSERT INTO translation_parameters (translation_tool_name) VALUES ('Test tool')")
    translation_parameters_id = cursor.lastrowid
    cursor.execute("INSERT INTO message_translation (message_id, translation_parameters_id, translation_text) VALUES (?, ?, 'Translated text')", (message_id, translation_parameters_id))

    yield cursor

    connection.close()


def test_check_channel_exists(setup_database):
    """
    Test that check_channel_exists returns the correct
    channel_id when the channel exists.
    """
    cursor = setup_database
    cursor.execute("SELECT channel_id FROM channels WHERE channel_name = ?", ('test_channel',))
    expected_channel_id = cursor.fetchone()
    actual_channel_id = check_channel_exists(cursor, 'test_channel')
    assert actual_channel_id == expected_channel_id[0]


def test_check_channel_does_not_exist(setup_database):
    """
    Test that check_channel_exists returns None when the
    channel does not exist.
    """
    cursor = setup_database
    assert check_channel_exists(cursor, 'nonexistent_channel') is None


@pytest.mark.parametrize("exception", [
    sqlite3.OperationalError,
    sqlite3.IntegrityError,
    sqlite3.ProgrammingError,
    sqlite3.DatabaseError
])
def test_check_channel_exceptions(exception):
    """
    Test that check_channel_exists correctly raises sqlite3 exceptions.
    """
    cursor = MagicMock()
    channel_name = 'test_channel'

    # Mock  to return a valid channel ID
    with patch('lib.db_utils.check_channel_exists', return_value=1):
        # Then mock cursor.execute to raise the specified exception
        cursor.execute.side_effect = exception

        with pytest.raises(exception):
            has_channel_messages(cursor, channel_name)


def test_has_channel_messages_true(setup_database):
    """Test that has_channel_messages returns True when messages exist."""
    cursor = setup_database
    assert has_channel_messages(cursor, 'existing_channel') is True


def test_has_channel_messages_false(setup_database):
    """Test that has_channel_messages returns False when no messages exist."""
    cursor = setup_database
    assert has_channel_messages(cursor, 'empty_channel') is False


def test_has_channel_messages_nonexistent_channel(setup_database):
    """
    Test that has_channel_messages returns False for a nonexistent channel.
    """
    cursor = setup_database
    assert has_channel_messages(cursor, 'nonexistent_channel') is False


@pytest.mark.parametrize("exception", [
    sqlite3.OperationalError,
    sqlite3.IntegrityError,
    sqlite3.ProgrammingError,
    sqlite3.DatabaseError
])
def test_has_channel_messages_exceptions(exception):
    """
    Test that has_channel_messages correctly raises sqlite3 exceptions.
    """
    cursor = MagicMock()
    channel_name = 'existing_channel'

    # Mock check_channel_exists to return a valid channel ID
    with patch('lib.db_utils.has_channel_messages', return_value=1):
        # Then mock cursor.execute to raise the specified exception
        cursor.execute.side_effect = exception

        with pytest.raises(exception):
            has_channel_messages(cursor, channel_name)


def test_schema_validity():
    # Connect to an in-memory SQLite database
    conn = sqlite3.connect(':memory:')
    cursor = conn.cursor()

    # Schema location assets/schema.sql
    schema_file_path = 'assets/schema.sql'

    # Read and execute the schema SQL
    with open(schema_file_path, 'r') as schema_file:
        schema_sql = schema_file.read()
        cursor.executescript(schema_sql)

    # Verify tables were created correctly
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    assert ('translation_parameters',) in tables
    assert ('message_translation',) in tables

    # Verify foreign key constraints
    cursor.execute("PRAGMA foreign_key_list('message_translation')")
    fks = cursor.fetchall()
    assert len(fks) > 0, "Foreign key constraints not found"


def test_check_table_exists_true(setup_database):
    cursor = setup_database
    assert check_table_exists(cursor, "channels") is True, "Should return True for existing table"


def test_check_table_exists_false(setup_database):
    cursor = setup_database
    assert check_table_exists(cursor, "non_existent_table") is False, "Should return False for non-existent table"


def test_read_sql_from_file():
    # Create a temporary file with known SQL content
    expected_sql_content = "CREATE TABLE test (id INTEGER PRIMARY KEY, name TEXT);"
    with tempfile.NamedTemporaryFile(delete=False, mode='w') as tmpfile:
        tmpfile_name = tmpfile.name
        tmpfile.write(expected_sql_content)
        tmpfile.flush()  # Ensure content is written to disk

    # Use the function to read back the file content
    try:
        actual_sql_content = read_sql_from_file(tmpfile_name)
        # Assert that the content read matches what was written
        assert actual_sql_content == expected_sql_content, "SQL content read does not match expected content"
    finally:
        # Clean up - remove the temporary file
        remove(tmpfile_name)


def test_create_tables_from_schema(setup_database):
    connection = sqlite3.connect(":memory:")
    cursor = setup_database

    # Create a temporary schema file
    schema_content = """
    CREATE TABLE IF NOT EXISTS new_table (id INTEGER PRIMARY KEY, name TEXT);
    """
    with tempfile.NamedTemporaryFile(delete=False, mode='w') as tmpfile:
        tmpfile_name = tmpfile.name
        tmpfile.write(schema_content)
        tmpfile.flush()

    try:
        # Test the function
        create_tables_from_schema(connection, cursor, tmpfile_name)
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='new_table'")
        table_exists = cursor.fetchone()
        assert table_exists is not None, "Table 'new_table' should have been created but was not found."
    finally:
        # Clean up - remove the temporary file and close the database connection
        remove(tmpfile_name)
        connection.close()


@pytest.fixture
def db_cursor():
    # Create an in-memory SQLite database and cursor
    connection = sqlite3.connect(":memory:")
    cursor = connection.cursor()
    # Create the table needed for the test
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS translation_parameters (
        translation_parameters_id   INTEGER PRIMARY KEY,
        translation_tool_name       TEXT,
        translation_tool_commit     TEXT,
        translation_model           TEXT,
        translation_config_sha256   TEXT,
        translation_config          TEXT,
        UNIQUE(translation_tool_name, translation_tool_commit, translation_model, translation_config_sha256, translation_config)
    )
    """)
    yield cursor
    # No need to close the connection for in-memory databases as they are discarded


def test_insert_translation_parameters(db_cursor):
    # Example data to insert
    translation_tool_name = "hermeneisGPT.py"
    translation_tool_commit = "da8fb669caef4a111b80b365a6966c34bd48021c"
    translation_model = "gpt-3.5-turbo-1106"
    translation_config_sha256 = "6834cfe6d13e0e8bbddc21a30a84a6bf7de7dbb6f6624947dd0a51a9684c69cf"
    translation_config = """
    personality:
    system: |
      You are a Language Translator Bot specialized in translating from Russian to English.
    """

    # Insert data into the database
    translation_parameters_id = insert_translation_parameters(db_cursor, translation_tool_name, translation_tool_commit, translation_model, translation_config_sha256, translation_config)

    # Query the database to verify the insertion
    db_cursor.execute("SELECT * FROM translation_parameters WHERE translation_parameters_id=?", (translation_parameters_id,))

    result = db_cursor.fetchone()

    assert result is not None, "The data was not inserted into the database."
    assert result[1] == translation_tool_name
    assert result[2] == translation_tool_commit
    assert result[3] == translation_model
    assert result[4] == translation_config_sha256
    assert result[5] == translation_config


def test_get_channel_messages(setup_database):
    """Test that get_channel_messages returns the correct messages for a channel."""
    cursor = setup_database
    messages = get_channel_messages(cursor, 'existing_channel')
    assert messages == [(1, 'Test message')], "The messages retrieved do not match expected values."


def test_get_channel_messages_no_channel(setup_database):
    """Test that get_channel_messages returns an empty list for a non-existent channel."""
    cursor = setup_database
    messages = get_channel_messages(cursor, 'nonexistent_channel')
    assert messages == [], "Messages were retrieved for a non-existent channel."


def test_exists_translation_for_message_true(setup_database):
    """Test that exists_translation_for_message returns True when a translation exists."""
    cursor = setup_database
    message_id = 1  # Assuming the first inserted message has ID 1
    translation_parameters_id = 1  # Assuming the first inserted translation parameters has ID 1
    assert exists_translation_for_message(cursor, message_id, translation_parameters_id) is True, "Translation should exist but was not found."


def test_exists_translation_for_message_false(setup_database):
    """Test that exists_translation_for_message returns False when a translation does not exist."""
    cursor = setup_database
    message_id = 1  # Assuming the first inserted message has ID 1
    translation_parameters_id = 999  # Using a non-existent translation_parameters_id
    assert exists_translation_for_message(cursor, message_id, translation_parameters_id) is False, "Translation should not exist but was reported as found."



def test_insert_new_translation(setup_database):
    """Test inserting a new translation."""
    cursor = setup_database
    message_id = 22
    translation_parameters_id = 22
    translation_text = "Translated Text"
    new_translation_id = upsert_message_translation(cursor, message_id, translation_parameters_id, translation_text)

    cursor.execute("SELECT COUNT(*) FROM message_translation WHERE message_id = ? AND translation_parameters_id = ?", (message_id, translation_parameters_id))
    count = cursor.fetchone()[0]
    assert count == 1, "Translation should have been inserted."
    assert new_translation_id > 0, "Translation ID should be returned and greater than 0."


def test_update_existing_translation(setup_database):
    """Test updating an existing translation."""
    cursor = setup_database
    # First, insert a translation to update
    message_id = 1
    translation_parameters_id = 1

    # Now, update the translation
    updated_translation_text = "Updated translation"
    upsert_message_translation(cursor, message_id, translation_parameters_id, updated_translation_text)

    cursor.execute("SELECT translation_text FROM message_translation WHERE message_id = ? AND translation_parameters_id = ?", (message_id, translation_parameters_id))
    translation_text = cursor.fetchone()[0]
    assert translation_text == updated_translation_text, "Translation text should have been updated."
