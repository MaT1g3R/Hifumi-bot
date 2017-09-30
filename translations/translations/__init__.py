from json import load
from pathlib import Path

from language_data import LANGUAGE_PATH

__all__ = ['Translation']


def _good_folder(path):
    """
    Determine if a given path is a good folder for language data.

    :param path: the path.

    :return: True if the given path is a good folder for language data.
    """
    if not path.is_dir():
        return False
    if 'pycache' in path.name:
        return False
    for file in path.iterdir():
        if file.name.endswith('.json'):
            return True
        if file.name.endswith('.py') or file.name.endswith('.pyc'):
            return False
    return False


def get_all_data():
    """
    Get all language data.

    :return: All of the language data in a dict.
    """
    res = {}
    for folder in LANGUAGE_PATH.iterdir():
        path = Path(folder)
        lan_name = path.name
        if not _good_folder(path):
            continue
        for file in path.iterdir():
            if not file.name.endswith('.json'):
                continue
            fp = Path(file)
            fname = fp.name
            with fp.open() as f:
                dict_ = load(f, encoding='utf-8')
            if lan_name not in res:
                res[lan_name] = {}
            res[lan_name][fname] = dict_
    return res


class Translation:
    """
    Class to provide translation support for Hifumi.
    """
    __slots__ = ('_data',)

    def __init__(self):
        """
        Init the class.
        """
        self._data = {}
        self.reload()

    def reload(self):
        """
        Reload the class with new data read from disk.
        """
        self._data = get_all_data()

    @property
    def en(self):
        """
        A quick access to the base language(English)
        :return: The English language data.
        """
        return self._data['en']

    def get(self, lan: str, file: str, key: str) -> str:
        """
        Get data of a language.

        :param lan: The language name.

        :param file: the file name desired.

        :param key: the key to the string.

        :return:
            The string in the desired language if found,
            return in English if not found.

        :raises KeyError:
            If the language or file name is not in all of the data.
        """
        if not file.endswith('.json'):
            file = f'{file}.json'
        language_data = self._data[lan][file]
        english_data = self.en[file][key]
        return language_data.get(key, english_data)
