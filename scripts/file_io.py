"""
File IO functions
"""
from pathlib import Path

from demjson import decode


def load_json(path: Path, encoding=None) -> dict:
    """
    Load a json file into a dict.
    :param path: the path to the file.
    :param encoding: encoding used for the file, optional.
    :return: the json file as a dict.
    """
    with path.open(encoding=encoding) as f:
        content = f.read()
    return decode(content, encoding=encoding)
