import os
import shutil


def __autoclean(path=(os.getcwd())):
    """
    Cleans automatically Python cache.
    :return: Clean if successful.
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
    Cleans automatically Python cache.
    :return: Clean if successful.
    """
    paths = __autoclean()
    for path in paths:
        try:
            shutil.rmtree(path)
        except FileNotFoundError:
            pass
