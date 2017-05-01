"""
Functions for file io
"""
import json
from os import listdir
from os.path import join, isfile


def read_json(fp, keep_open=False):
    """
    Read a json file into a dictionary
    :param fp: the file pointer
    :type fp: file
    :param keep_open: keep file open (default False)
    :type keep_open: bool | int
    :return: the dictionary
    :rtype: dict
    """
    if fp is not None:
        data = json.load(fp)
        if not keep_open:
            fp.close()
        return data
    return {}


def write_json(fp, data, keep_open=False):
    """
    Write a dictionary into a json file
    :param fp: The json file
    :type fp: ffile
    :param data: The dictionary
    :type data: dict
    :param keep_open: keep file open (default False)
    :type keep_open: bool | int
    :return: nothing
    :rtype: None
    """
    if fp is not None:
        json.dump(data, fp)
        if not keep_open:
            fp.close()


def read_all_files(path):
    """
    Reads all files in a folder
    :param path: the path to the folder
    :return: All path of the files
    :rtype: list
    """
    return [join(path, f) for
            f in listdir(path) if isfile(join(path, f))]
