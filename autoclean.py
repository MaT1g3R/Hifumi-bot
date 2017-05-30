import os
import shutil


def __find_cache(path=(os.getcwd())):
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
            res += __find_cache(subitem)
        return res


def __autoclean(path, filter_):
    """
    A helper function to delete all files under a folder
    :param path: the path that points to the folder
    :param filter_: the filter keyword will prevent deleting any file with the
    word in its name
    """
    for file in os.listdir(path):
        if filter_ not in file:
            try:
                os.remove(os.path.join(path, file))
            except OSError:
                continue


def autoclean():
    """
    Cleans all Python cache.
    """
    for path in __find_cache():
        shutil.rmtree(path, ignore_errors=True)
    dumps = os.path.join('data', 'dumps')
    shard_info = os.path.join('data', 'shard_info')
    logs = os.path.join('data', 'logs')
    for path in [dumps, shard_info, logs]:
        __autoclean(path, '.gitkeep')


if __name__ == '__main__':
    print("Hey! This script is not intended to be opened "
          "in the Python shell >_< This file offers a "
          "external function to clean Python cache and "
          "should be executed only by internal process "
          "of Hifumi.")
    exit(1)
