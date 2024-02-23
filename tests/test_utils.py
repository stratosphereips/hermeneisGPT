# pylint: disable=missing-docstring
# pylint: disable=line-too-long
import pytest
import hashlib
import subprocess
import sys
from unittest.mock import patch, MagicMock
from os import path

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from lib.utils import get_current_commit
from lib.utils import get_file_sha256
from lib.utils import get_file_content


def test_get_current_commit_success():
    with patch('subprocess.check_output') as mocked_check_output:
        mocked_check_output.return_value = b'abc123\n'
        commit = get_current_commit()
        mocked_check_output.assert_called_once_with(['git', 'rev-parse', 'HEAD'])
        assert commit == 'abc123'


def test_get_current_commit_failure():
    with patch('subprocess.check_output') as mocked_check_output:
        mocked_check_output.side_effect = subprocess.CalledProcessError(1, 'git')
        with pytest.raises(subprocess.CalledProcessError):
            get_current_commit()


def test_get_file_sha256_file_not_found():
    # Use a non-existent file path
    non_existent_file = "non_existent_file.txt"
    with pytest.raises(FileNotFoundError):
        get_file_sha256(non_existent_file)


def test_get_file_sha256_success(tmp_path):
    # Create a temporary file with known content
    test_file = tmp_path / "test_file.txt"
    test_content = b"Hello, pytest!"
    test_file.write_bytes(test_content)

    # Calculate the expected SHA256 hash for the test content
    expected_sha256_hash = hashlib.sha256(test_content).hexdigest()

    # Call the function and verify the result
    calculated_sha256_hash = get_file_sha256(test_file)
    assert calculated_sha256_hash == expected_sha256_hash


def test_get_file_sha256_empty_file(tmp_path):
    # Create an empty temporary file
    empty_file = tmp_path / "empty_file.txt"
    empty_file.write_text('')

    # The SHA256 hash of an empty file
    expected_sha256_hash = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"

    # Call the function with the empty file and verify the result
    calculated_sha256_hash = get_file_sha256(empty_file)
    assert calculated_sha256_hash == expected_sha256_hash


def test_get_file_sha256_permission_error(tmp_path):
    # Create a temporary file and restrict its permissions
    restricted_file = tmp_path / "restricted_file.txt"
    restricted_file.write_text("Restricted content")
    restricted_file.chmod(0o000)

    # Attempt to read the file and expect a permission error
    with pytest.raises(PermissionError):
        get_file_sha256(restricted_file)

    # Cleanup: Reset permissions so the file can be deleted
    restricted_file.chmod(0o644)


def test_get_file_content_success(tmp_path):
    # Setup: Create a file with known content
    test_file = tmp_path / "test_file.txt"
    test_content = "Hello, pytest!"
    test_file.write_text(test_content, encoding='utf-8')

    # Exercise: Read the file content using the function
    content = get_file_content(test_file)

    # Verify: Check if the content read matches the expected content
    assert content == test_content


def test_get_file_content_file_not_found():
    # Setup: Define a path for a non-existent file
    non_existent_file = "non_existent_file.txt"

    # Exercise & Verify: Expect a FileNotFoundError
    with pytest.raises(FileNotFoundError) as e:
        get_file_content(non_existent_file)

    # Additional Verify: Optionally check the error message
    assert f"File not found: {non_existent_file}" in str(e.value)


def test_get_file_content_permission_error(tmp_path):
    # Setup: Create a file and restrict its permissions
    restricted_file = tmp_path / "restricted_file.txt"
    restricted_file.write_text("Restricted content", encoding='utf-8')
    restricted_file.chmod(0o000)  # No permissions

    # Exercise & Verify: Expect a PermissionError
    with pytest.raises(PermissionError) as e:
        get_file_content(restricted_file)

    # Additional Verify: Optionally check the error message
    assert f"Permission denied: {restricted_file}" in str(e.value)

    # Cleanup: Reset permissions so the file can be deleted
    restricted_file.chmod(0o644)
