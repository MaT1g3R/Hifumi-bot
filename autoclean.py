import shutil


def autoclean():
    """
    Cleans automatically Python cache.
    :return: Clean if successful.
    """
    try:
        shutil.rmtree('./__pycache__')
    except FileNotFoundError:
        pass
