"""
Various utilities associated with hermeneisGPT.
"""

import subprocess


def get_current_commit():
    """
    Function uses subprocess to retrieve the last commit of the tool.
    """
    try:
        commit_hash = subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode('utf-8').strip()
        return commit_hash
    except subprocess.CalledProcessError:
        raise subprocess.CalledProcessError

