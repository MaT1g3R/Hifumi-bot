import os
import shutil


def __autoclean(path=(os.getcwd())):
    """
    Helper function to get all "__pycache__" folders
    :return: A list of paths with name __pycache__
    """
    if os.path.isdir(path) and '__pycache__' in path:
        return [path]
    elif os.path.isfile(path):
        return []
    else:
        res = []
        for file_name in os.listdir(path):
            subitem = os.path.join(path, file_name)
            res += __autoclean(subitem)
        return res


def autoclean():
    """
    Cleans all Python cache.
    """
    for path in __autoclean():
        shutil.rmtree(path, ignore_errors=True)
    dumps = os.path.join('data', 'dumps')
    shard_info = os.path.join('data', 'shard_info')
    dummy = 'dummy.txt'
    for file in os.listdir(dumps):
        if dummy not in file:
            try:
                os.remove(os.path.join(dumps, file))
            except OSError:
                continue
    for file in os.listdir(shard_info):
        if dummy not in file:
            try:
                os.remove(os.path.join(shard_info, file))
            except OSError:
                continue


if __name__ == '__main__':
    print("Hey! This script is not intended to be opened "
          "in the Python shell >_< This file offers a "
          "external function to clean Python cache and "
          "should be executed only by internal process "
          "of Hifumi.")
    exit(1)
