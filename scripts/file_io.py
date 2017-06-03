"""
Functions for file io
"""

from io import TextIOBase
from json import dump, load
from pathlib import Path

from yaml import safe_dump, safe_load


def __read(func: callable) -> callable:
    """
    Decorator for file-reading functions, checks that the file pointer is not
    None and closes the file if keep_open is False
    """

    def wrap(fp: TextIOBase, keep_open: bool, *args, **kwargs):
        if fp:
            res = func(fp, keep_open, *args, **kwargs)
            if not keep_open:
                fp.close()
            return res

    return wrap


def __write(func: callable) -> callable:
    """
    Decorator for file-writing functions, checks that the file pointer is not
    None and closes the file if keep_open is False
    """

    def wrap(fp: TextIOBase, data, keep_open: bool, *args, **kwargs):
        if fp:
            func(fp, data, keep_open, *args, **kwargs)
            if not keep_open:
                fp.close()

    return wrap


@__read
def read_json(fp: TextIOBase, keep_open: bool = False) -> dict:
    """
    Read a json file into a dictionary
    :param fp: the file pointer
    :param keep_open: keep file open (default False)
    :return: the dictionary
    """
    return load(fp)


@__write
def write_json(fp: TextIOBase, data: dict, keep_open: bool = False):
    """
    Write a dictionary into a json file
    :param fp: The json file
    :param data: The dictionary
    :param keep_open: keep file open (default False)
    """
    dump(data, fp)


@__read
def read_yaml(fp: TextIOBase, keep_open: bool = False) -> dict:
    """
    Read a yaml file into a dict
    :param fp: the file pointer
    :param keep_open: keep file open (default False)
    :return: the dict
    """
    return safe_load(fp)


@__write
def write_yaml(fp: TextIOBase, data: dict, keep_open: bool = False):
    """
    Write a dict into a yaml file
    :param fp: the file pointer
    :param data: the dict
    :param keep_open: keep file open (default False)
    """
    safe_dump(data, fp)


def read_all_files(path: Path):
    """
    Reads all files in a folder
    :param path: the path to the folder
    :return: All path of the files
    :rtype: list
    """
    return [Path.joinpath(f) for f in path.iterdir() if f.is_file()]
