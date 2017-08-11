from pathlib import Path

from yaml import safe_dump, safe_load


class Config(dict):
    """
    Class to hold the config information.
    """
    __slots__ = ['__path', '__content']

    def __init__(self):
        """
        Initialize the instance of this class.
        """
        self.__path = Path(Path(__file__).parent.joinpath('settings.yml'))
        with self.__path.open(encoding='utf-8') as f:
            self.__content = safe_load(f.read())
        super().__init__(self.__content)

    def dump(self):
        """
        Dump self's contents into the config file.
        """
        with self.__path.open('w', encoding='utf-8') as f:
            safe_dump(self.__content, f)

    def __setitem__(self, key, value):
        self.__content[key] = value
        super().__setitem__(key, value)

    def postgres(self):
        return self['Postgres']
