"""
HermeneisGPT is a tool and framework to translate messages and/or
text from hacktivist channels or forums from Russian to English
using Large Language Models.
"""

# flake8: noqa: E501

import argparse
import logging
import yaml

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


def load_and_parse_config(yaml_config_path):
    """
    Takes a config yaml and loads it to a variable for later use.
    """
    try:
        with open(yaml_config_path, 'r', encoding="utf-8") as configuration_yaml:
            yaml_config = yaml.safe_load(configuration_yaml)
        logger.info("Loaded data from YAML file: %s", yaml_config_path)
    except Exception as e:
        logger.error("Error reading YAML file: %s", e)
        raise

    config = {
        'type': yaml_config['personality']['type'],
        'prompt': yaml_config['personality']['prompt'],
        'model': yaml_config['personality']['model'],
        'temperature': yaml_config['personality']['temperature'],
        'max_tokens': yaml_config['personality']['max_tokens'],
        'log': yaml_config['personality']['log']
    }

    return config

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

        # TODO Add main logic here

    except Exception as err:
        logger.info("Exception in main()")


if __name__ == "__main__":
    main()
