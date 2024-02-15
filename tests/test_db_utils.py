# pylint: disable=missing-docstring
import pytest
import sys
import sqlite3
from os import path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from lib.db_utils import get_db_connection
from lib.db_utils import check_channel_exists


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
    # Use an in-memory database for testing
    connection = sqlite3.connect(":memory:")
    cursor = connection.cursor()

    # Setup schema and test data
    cursor.execute("CREATE TABLE channels (channel_id INTEGER PRIMARY KEY, channel_name TEXT)")
    # Insert a test channel
    cursor.execute("INSERT INTO channels (channel_name) VALUES ('test_channel')")

    yield cursor

    # Teardown - close the connection
    connection.close()


def test_channel_exists(setup_database):
    """
    Test that check_channel_exists returns the correct
    channel_id when the channel exists.
    """
    cursor = setup_database
    # We inserted one channel, so channel_id =1
    assert check_channel_exists(cursor, 'test_channel') == 1
