from json import dump, load
from pathlib import Path


class Config:
    """
    Class to hold the config information.
    """
    __slots__ = ['__path', '__content']

    def __init__(self):
        """
        Initialize the instance of this class.
        """
        self.__path = Path(Path(__file__).parent.joinpath('settings.json'))
        with self.__path.open() as f:
            self.__content = load(f)

    def __getitem__(self, item):
        """
        self.__getitem__(item) -> self[item]
        """
        return self.__content[item]

    def __setitem__(self, key, value):
        """ Set self[key] to value. """
        edit = False
        try:
            old = self.__content[key]
            if value != old:
                edit = True
        except KeyError:
            edit = True
        if edit:
            self.__content[key] = value
            with self.__path.open('w+') as f:
                dump(self.__content, f, indent=2)
