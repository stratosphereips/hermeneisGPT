# pylint: disable=missing-docstring
import sys
import pytest
import logging
from os import path
from unittest.mock import patch

sys.path.append( path.dirname(path.dirname( path.abspath(__file__) ) ))
from hermeneisGPT import load_and_parse_config


def test_load_and_parse_config_success(tmp_path):
    directory = tmp_path / "sub"
    directory.mkdir()
    path = directory / "config.yaml"
    path.write_text("""
    personality:
      type: test_type
      prompt: test_prompt
      model: test_model
      temperature: 0.5
      max_tokens: 100
      log: output.log
    """, encoding='utf-8')

    # Patch 'logging.Logger.info' and 'logging.Logger.error'
    with patch.object(logging.Logger, 'info') as mock_info, \
         patch.object(logging.Logger, 'error') as mock_error:
        config = load_and_parse_config(str(path))

    # Check if 'info' was called at least once
    mock_info.assert_called()
    # Check if 'error' was not called, indicating no errors occurred
    mock_error.assert_not_called()
    assert config == {
        'type': 'test_type',
        'prompt': 'test_prompt',
        'model': 'test_model',
        'temperature': 0.5,
        'max_tokens': 100,
        'log': 'output.log'
    }


# Example of a failure to load due to file not found or other IO issues
def test_load_and_parse_config_failure(tmp_path):
    non_existent_file_path = tmp_path / "does_not_exist.yaml"

    # Patch 'logging.Logger.error'
    with patch.object(logging.Logger, 'error') as mock_error, \
         pytest.raises(FileNotFoundError):
        load_and_parse_config(str(non_existent_file_path))

    # Check if 'error' was called at least once
    mock_error.assert_called_once()
