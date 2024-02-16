"""
Various utilities associated with hermeneisGPT.
"""

import subprocess
import hashlib


def get_current_commit():
    """
    Function uses subprocess to retrieve the last commit of the tool.
    """
    try:
        commit_hash = subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode('utf-8').strip()
        return commit_hash
    except subprocess.CalledProcessError:
        raise subprocess.CalledProcessError


def get_file_sha256(file_path):
    """
    Calculate the sha256 of a given file and return it.
    """
    sha256_hash = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except FileNotFoundError:
        raise FileNotFoundError

