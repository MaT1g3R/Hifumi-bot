import shutil
from itertools import chain
from pathlib import Path


def __find_cache(path: Path = Path('.')):
    """
    Helper function to get all "__pycache__" folders
    :return: A list of paths with name __pycache__
    """
    if path.is_dir() and '__pycache__' in path.name:
        return [path]
    elif path.is_file():
        return []
    else:
        res = []
        for sub in path.iterdir():
            res += __find_cache(sub)
        return res


def autoclean():
    """
    Cleans all Python cache.
    """
    for path in __find_cache():
        shutil.rmtree(str(path), ignore_errors=True)
    dumps = Path('../data/dumps')
    shard_info = Path('../data/shard_info')
    logs = Path('../data/logs')
    for path in chain(dumps.iterdir(), shard_info.iterdir(), logs.iterdir()):
        if '.gitkeep' not in path.name:
            path.unlink()
