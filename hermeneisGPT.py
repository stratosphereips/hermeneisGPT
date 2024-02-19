"""
hermeneisGPT is a tool and framework to translate messages and/or
text from hacktivist channels or forums from Russian to English
using Large Language Models.
"""

# flake8: noqa: E501

import argparse
import logging
import os
import yaml
from dotenv import dotenv_values
from openai import OpenAI
from lib.utils import get_current_commit
from lib.utils import get_file_sha256
from lib.utils import get_file_content
from lib.db_utils import get_db_connection
from lib.db_utils import create_tables_from_schema
from lib.db_utils import has_channel_messages
from lib.db_utils import insert_translation_parameters


# Set up logging
logger = logging.getLogger('hermeneis')
logger.setLevel(logging.DEBUG)

# Create file handler for logging to a file
file_handler = logging.FileHandler('logs/hermeneis.log')
file_handler.setLevel(logging.DEBUG)  # Log all levels to the file

# Create console handler for logging to the console
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.ERROR)  # Log INFO and above to the console

# Create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add the handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)


def set_key(env_path):
    "Reads the OpenAI API key and sets it"

    env = dotenv_values(env_path)
    return env["OPENAI_API_KEY"]


def load_and_parse_config(yaml_config_path):
    """
    Takes a config yaml and loads it to a variable for later use.
    """
    try:
        with open(yaml_config_path, 'r', encoding="utf-8") as configuration_yaml:
            yaml_config = yaml.safe_load(configuration_yaml)
        logger.debug("Loaded data from YAML file: %s", yaml_config_path)
    except Exception as e:
        logger.error("Error reading YAML file: %s", e)
        raise

    config = {
        'system': yaml_config['personality']['system'].strip(),
        'user': yaml_config['personality']['user'],
        'model': yaml_config['personality']['model'].strip(),
        'temperature': float(yaml_config['personality']['temperature'].strip()),
        'max_tokens': int(yaml_config['personality']['max_tokens'].strip()),
        'log': yaml_config['personality']['log'].strip()
    }

    return config


def translate_mode_automatic(client, config, args):
    """
    Run the LLM translation in automatic mode using a
    SQLite database. Translations will be written on
    the same DB.
    """
    translation_tool_name = os.path.basename(__file__)
    translation_tool_commit = get_current_commit()
    translation_model = config['model']
    translation_config_sha256 = get_file_sha256(args.yaml_config)
    translation_config = get_file_content(args.yaml_config)
    try:
        logger.debug("Starting automatic translation")

        logger.debug("Connecting to DB: %s", args.sqlite_db)
        connection, cursor = get_db_connection(args.sqlite_db)

        logger.debug("Creating tables needed for translation using schema: %s", args.sqlite_schema)
        create_tables_from_schema(connection, cursor, args.sqlite_schema)

        has_messages = has_channel_messages(cursor, args.channel_name)
        logger.debug("Checking if there are messages for channel %s: %s", args.channel_name, has_messages)

        logger.debug("Retrieving translation parameters based on user input")
        logger.debug("Retrieving the tool name: %s", translation_tool_name)
        logger.debug("Retrieving the tool current commit: %s", translation_tool_commit)
        logger.debug("Retrieving the LLM model: %s", translation_model)
        logger.debug("Retrieving the YAML config file SHA256: %s", translation_config_sha256)
        logger.debug("Retrieving the YAML config file: %s bytes", len(translation_config))

        translation_parameters_id = insert_translation_parameters(cursor,
                                                                 translation_tool_name,
                                                                 translation_tool_commit,
                                                                 translation_model,
                                                                 translation_config_sha256,
                                                                 translation_config)

        logger.debug("Storing translation parameters to DB and retrieving ID: %s", translation_parameter_id)
        connection.commit()
        connection.close()
    except KeyboardInterrupt:
        connection.commit()
        connection.close()
        return


def translate_mode_manual(client, config):
    """
    Run the LLM translation in manual interactive mode
    """
    try:
        logger.debug("Starting manual translation")
        while True:
            print("Input your message to translate:")
            input_lang_ru=input().strip()

            translate_messages = [{"role":"system", "content": config['system']},
                                  {"role":"user", "content": config['user']+input_lang_ru}]

            # Initialize the OpenAI LLM (Language Learning Model)
            llm_response = client.chat.completions.create(
                model = config['model'],
                messages = translate_messages,
                max_tokens = config['max_tokens'],
                temperature = config['temperature'],
            )
            print(llm_response.choices[0].message.content)
    except KeyboardInterrupt:
        return

def main():
    """
    Take a message input and use the data from the yaml file to translate
    the text from Russian to English.

    Command-line arguments:
        yaml_config: Path to the configuration file (.yaml)
        env: Path to the .env file with secrets (API keys, etc)
    """
    try:
        # Set up the argument parser
        parser = argparse.ArgumentParser(
            description='HermeneisGPT: Translate hacking messages from '
                        'Russian to English using LLMs.')
        parser.add_argument('-v',
                            '--verbose',
                            action='store_true',
                            help='run hermeneisGPT in verbose mode')
        parser.add_argument('-d',
                            '--debug',
                            action='store_true',
                            help='run hermeneisGPT in debug mode')
        parser.add_argument('-c',
                            '--yaml_config',
                            default='config_EXAMPLE.yml',
                            help='path to the YAML file with challenge data (default=config_EXAMPLE.yml)')
        parser.add_argument('-e',
                            '--env',
                            default='.env',
                            help='path to environment file (.env)')
        parser.add_argument('-m',
                            '--mode',
                            choices=['manual', 'auto-sqlite'],
                            default='manual',
                            help='select the mode (manual or auto-sqlite)')

        parser.add_argument('--channel_name',
                            help='name of the hacktivist telegram channel to translate')

        parser.add_argument('--sqlite_db',
                            help='path to SQLite database with messages to translate')
        parser.add_argument('--sqlite_schema',
                            default='assets/schema.sql',
                            help='path to SQLite database schema for translations')
        parser.add_argument('--sqlite_chn_table',
                            default='channels',
                            help='DB table where channels are stored (default="channels")')
        parser.add_argument('--sqlite_chn_field',
                            default='channel_name',
                            help='field on channels table that contains name of the channel (default="channel_name")')
        parser.add_argument('--sqlite_msg_table',
                            default='messages',
                            help='DB table where messages are stored (default="messages")')
        parser.add_argument('--sqlite_msg_field',
                            default='message_text',
                            help='field on messages table that contains message text (default="message_text")')
        args = parser.parse_args()

        if args.verbose:
            console_handler.setLevel(logging.INFO)
        if args.debug:
            console_handler.setLevel(logging.DEBUG)

        # Read YAML Configuration file
        config = load_and_parse_config(args.yaml_config)

        # Set the API key
        openai_key = set_key(args.env)
        client = OpenAI(api_key=openai_key)

        # Match the mode to run on
        match args.mode:
            case "manual":
                logger.info("hermeneisGPT on manual mode")

                # If a DB is provided, make sure the user knows it will be ignored
                if args.sqlite_db:
                    logger.info("Running on manual mode, ignoring the DB file '%s'", args.sqlite_db)

                # Run interactive manual mode
                translate_mode_manual(client, config)

            case "auto-sqlite":
                logger.info("hermeneisGPT on automatic SQLite mode")

                # Automatic DB mode requires the database arg to be passes/
                if not args.sqlite_db:
                    logger.error("--sqlite_db is required when running on automatic SQLite mode")
                    return
                # Automatic DB mode requires the hacktivist channel_name to translate messages from
                if not args.channel_name:
                    logger.error("--channel_name is required when running on automatic SQLite mode")
                    return

                # Run automatic mode with sqlite db
                translate_mode_automatic(client, config, args)

    except Exception as err:
        logger.info("Exception in main()")
        logger.info(err)


if __name__ == "__main__":
    main()
