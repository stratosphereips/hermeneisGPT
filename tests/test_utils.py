# pylint: disable=missing-docstring
# pylint: disable=line-too-long
import pytest
from unittest.mock import patch, MagicMock
import subprocess
import sys
from os import path

sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from lib.utils import get_current_commit


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

