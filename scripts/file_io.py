"""
Functions for file io
"""
import json
from io import TextIOBase
from pathlib import Path

from yaml import safe_dump, safe_load


def read_json(fp: TextIOBase, keep_open: bool = False) -> dict:
    """
    Read a json file into a dictionary
    :param fp: the file pointer
    :param keep_open: keep file open (default False)
    :return: the dictionary
    """
    if fp is not None:
        data = json.load(fp)
        if not keep_open:
            fp.close()
        return data
    return {}


def write_json(fp: TextIOBase, data: dict, keep_open: bool = False):
    """
    Write a dictionary into a json file
    :param fp: The json file
    :param data: The dictionary
    :param keep_open: keep file open (default False)
    """
    if fp is not None:
        json.dump(data, fp)
        if not keep_open:
            fp.close()


def read_yaml(fp: TextIOBase, keep_open: bool = False) -> dict:
    """
    Read a yaml file into a dict
    :param fp: the file pointer
    :param keep_open: keep file open (default False)
    :return: the dict
    """
    if fp:
        data = safe_load(fp)
        if not keep_open:
            fp.close()
        return data
    return {}


def write_yaml(fp: TextIOBase, data: dict, keep_open: bool = False):
    """
    Write a dict into a yaml file
    :param fp: the file pointer
    :param data: the dict
    :param keep_open: keep file open (default False)
    """
    if fp:
        safe_dump(data, fp)
        if not keep_open:
            fp.close()


def read_all_files(path: Path):
    """
    Reads all files in a folder
    :param path: the path to the folder
    :return: All path of the files
    :rtype: list
    """
    return [Path.joinpath(f) for f in path.iterdir() if f.is_file()]
