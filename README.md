# hermeneisGPT
[![Auto Tag](https://github.com/stratosphereips/hermeneisGPT/actions/workflows/autotag.yml/badge.svg)](https://github.com/stratosphereips/hermeneisGPT/actions/workflows/autotag.yml)
[![Validate Python](https://github.com/stratosphereips/hermeneisGPT/actions/workflows/validate_python.yml/badge.svg)](https://github.com/stratosphereips/hermeneisGPT/actions/workflows/validate_python.yml)
[![Validate Yaml](https://github.com/stratosphereips/hermeneisGPT/actions/workflows/validate_yaml.yml/badge.svg)](https://github.com/stratosphereips/hermeneisGPT/actions/workflows/validate_yaml.yml)


HermeneisGPT is a framework to translate hacking messages from Russian to English using LLM models.
<img width="2379" alt="image" src="https://github.com/stratosphereips/hermeneisGPT/assets/2458879/f2d22244-e900-465a-ae0a-324d29faea38">


<details>
  <summary><h2>Expand for Installation Instructions</h2></summary>   
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

<details>
  <summary><h2>Expand for Execution Instructions</h2></summary>

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
