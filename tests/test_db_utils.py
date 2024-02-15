# pylint: disable=missing-docstring
import pytest
import sys
import sqlite3
from os import path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from lib.db_utils import get_db_connection


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
