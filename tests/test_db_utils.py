# pylint: disable=missing-docstring
# pylint: disable=line-too-long
import pytest
import sys
import sqlite3
from os import path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from lib.db_utils import get_db_connection
from lib.db_utils import check_channel_exists
from lib.db_utils import has_channel_messages


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
    cursor.execute("CREATE TABLE messages (message_id INTEGER PRIMARY KEY, channel_id INTEGER, message TEXT)")

    # Insert test data
    cursor.execute("INSERT INTO channels (channel_name) VALUES ('test_channel')")
    cursor.execute("INSERT INTO channels (channel_name) VALUES ('existing_channel')")
    cursor.execute("INSERT INTO channels (channel_name) VALUES ('empty_channel')")
    channel_id = cursor.execute("SELECT channel_id FROM channels WHERE channel_name = 'existing_channel'").fetchone()[0]
    cursor.execute("INSERT INTO messages (channel_id, message) VALUES (?, 'Test message')", (channel_id,))

    yield cursor

    connection.close()


def test_channel_exists(setup_database):
    """
    Test that check_channel_exists returns the correct
    channel_id when the channel exists.
    """
    cursor = setup_database
    cursor.execute("SELECT channel_id FROM channels WHERE channel_name = ?", ('test_channel',))
    expected_channel_id = cursor.fetchone()
    actual_channel_id = check_channel_exists(cursor, 'test_channel')
    assert actual_channel_id == expected_channel_id[0]


def test_channel_does_not_exist(setup_database):
    """
    Test that check_channel_exists returns None when the
    channel does not exist.
    """
    cursor = setup_database
    assert check_channel_exists(cursor, 'nonexistent_channel') is None


def test_has_channel_messages_true(setup_database):
    """Test that has_channel_messages returns True when messages exist."""
    cursor = setup_database
    assert has_channel_messages(cursor, 'existing_channel') is True


def test_has_channel_messages_false(setup_database):
    """Test that has_channel_messages returns False when no messages exist."""
    cursor = setup_database
    assert has_channel_messages(cursor, 'empty_channel') is False


def test_has_channel_messages_nonexistent_channel(setup_database):
    """Test that has_channel_messages returns False for a nonexistent channel."""
    cursor = setup_database
    assert has_channel_messages(cursor, 'nonexistent_channel') is False
