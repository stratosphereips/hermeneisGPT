# pylint: disable=missing-docstring
import argparse
import sys
import pytest
import logging
from os import path
from unittest.mock import patch
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from hermeneisGPT import load_and_parse_config
from hermeneisGPT import main


def test_load_and_parse_config_success(tmp_path):
    directory = tmp_path / "sub"
    directory.mkdir()
    path = directory / "config.yaml"
    path.write_text("""
    personality:
      system: system_prompt
      user: user_prompt
      model: test_model
      temperature: "0.5"
      max_tokens: "100"
      log: output.log
    """, encoding='utf-8')

    # Patch 'logging.Logger.debug' and 'logging.Logger.error'
    with patch.object(logging.Logger, 'debug') as mock_debug, \
         patch.object(logging.Logger, 'error') as mock_error:
        config = load_and_parse_config(str(path))

    # Check if 'debug' was called at least once
    mock_debug.assert_called()
    # Check if 'error' was not called, indicating no errors occurred
    mock_error.assert_not_called()
    assert config == {
        'system': 'system_prompt',
        'user': 'user_prompt',
        'model': 'test_model',
        'temperature': 0.5,
        'max_tokens': 100,
        'log': 'output.log',
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


def test_argument_parsing():
    test_args = [
        "hermeneisGPT.py",
        "--verbose",
        "--debug",
        "--yaml_config", "path/to/config.yml",
        "--env", "path/to/.env",
        "--mode", "auto-sqlite",
        "--channel_name", "example_channel",
        "--max_limit", "5",
        "--sqlite_db", "path/to/database.db",
        "--sqlite_schema", "path/to/schema.sql",
        "--sqlite_chn_table", "custom_channels",
        "--sqlite_chn_field", "custom_channel_name",
        "--sqlite_msg_table", "custom_messages",
        "--sqlite_msg_field", "custom_message_text"
    ]

    with patch('sys.argv', test_args):
        with patch('argparse.ArgumentParser.parse_args') as mock_parse:
            # Set the return value of parse_args to simulate parsed arguments
            mock_parse.return_value = argparse.Namespace(
                                                        verbose=True,
                                                        debug=True,
                                                        yaml_config="path/to/config.yml",
                                                        env="path/to/.env",
                                                        mode="auto-sqlite",
                                                        channel_name="example_channel",
                                                        max_limit="5",
                                                        sqlite_db="path/to/database.db",
                                                        sqlite_schema="path/to/schema.sql",
                                                        sqlite_chn_table="custom_channels",
                                                        sqlite_chn_field="custom_channel_name",
                                                        sqlite_msg_table="custom_messages",
                                                        sqlite_msg_field="custom_messages_text",
                                                        )
            main()

            # Verify parse_args was called indicating arguments were parsed
            mock_parse.assert_called()
