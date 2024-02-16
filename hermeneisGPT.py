"""
hermeneisGPT is a tool and framework to translate messages and/or
text from hacktivist channels or forums from Russian to English
using Large Language Models.
"""

# flake8: noqa: E501

import argparse
import logging
import yaml
from dotenv import dotenv_values
from openai import OpenAI


# Set up logging
logger = logging.getLogger('hermeneis')
logger.setLevel(logging.DEBUG)

# Create file handler for logging to a file
file_handler = logging.FileHandler('logs/hermeneis.log')
file_handler.setLevel(logging.DEBUG)  # Log all levels to the file

# Create console handler for logging to the console
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)  # Log INFO and above to the console

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


def translate_mode_manual(client, config):
    """
    Run the LLM translation in manual interactive mode
    """
    try:
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
        parser.add_argument('-c',
                            '--yaml_config',
                            default='config_EXAMPLE.yml',
                            help='Path to the YAML file with challenge data')
        parser.add_argument('-e',
                            '--env',
                            default='.env',
                            help='Path to environment file (.env)')
        args = parser.parse_args()

        # Read YAML Configuration file
        config = load_and_parse_config(args.yaml_config)

        # Set the API key
        OPENAI_KEY = set_key(args.env)
        client = OpenAI(api_key=OPENAI_KEY)

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

    except Exception as err:
        logger.info("Exception in main()")
        logger.info(err)


if __name__ == "__main__":
    main()
