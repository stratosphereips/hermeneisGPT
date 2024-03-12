![hermeneisGPT](https://github.com/stratosphereips/hermeneisGPT/assets/2458879/4ce8d9c3-be30-4398-80f4-297273dcca58)
# hermeneisGPT
[![Auto Tag](https://github.com/stratosphereips/hermeneisGPT/actions/workflows/autotag.yml/badge.svg)](https://github.com/stratosphereips/hermeneisGPT/actions/workflows/autotag.yml)
[![Validate Python](https://github.com/stratosphereips/hermeneisGPT/actions/workflows/validate_python.yml/badge.svg)](https://github.com/stratosphereips/hermeneisGPT/actions/workflows/validate_python.yml)
[![Validate Yaml](https://github.com/stratosphereips/hermeneisGPT/actions/workflows/validate_yaml.yml/badge.svg)](https://github.com/stratosphereips/hermeneisGPT/actions/workflows/validate_yaml.yml)


HermeneisGPT is a framework to translate messages using Large Language Models (LLM). The tool was initially created to help translate messages from Russian to English from hacktivist Telegram channels. However, it can be used for any application or language. The instructions can be specified through a YAML configuration file. Currently it supports two modes, manual and automatic. 

## Installation

<details>
  <summary>Expand for Installation Instructions</summary>

To configure and run the tool, follow the next steps:

```bash
:~$ git clone https://github.com/stratosphereips/hermeneisGPT.git
:~$ 
:~$ cd hermeneisGPT
:~$ 
:~$ python3 -m pip install -r requirements.txt
:~$ 
:~$ cp env_EXAMPLE .env
:~$ 
:~$ # Edit the .env file to add your OpenAI API Key
:~$ vim .env
```
</details>

## Execution

<details>
  <summary>Expand for Execution Instructions</summary>

Run hermeneisGPT help:

```bash 
python3 hermeneisGPT.py --help
```

Run hermeneisGPT in manual interactive mode: 

```bash
python3 hermeneisGPT.py -m manual
```

Run hermeneisGPT in automatic mode using the example SQLite DB: 
```bash
python3 hermeneisGPT.py -m auto-sqlite --channel_name noname05716 --sqlite_db assets/sample.sqlite -d
```
</details>

# About

HermeneisGPT was created in 2024 at the Stratosphere Laboratory, AI Center, FEE, Czech Technical University in Prague.
