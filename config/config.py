from pathlib import Path

from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap
from ruamel.yaml.scalarstring import DoubleQuotedScalarString


class Config:
    """
    Class to hold the config information.
    """
    __slots__ = ['__path', '__content', '__yaml']

    def __init__(self):
        """
        Initialize the instance of this class.
        """
        self.__yaml = YAML()
        self.__yaml.preserve_quotes = True
        self.__path = Path(Path(__file__).parent.joinpath('settings.yml'))
        with self.__path.open(encoding='utf-8') as f:
            self.__content = self.__yaml.load(f)

    def __getitem__(self, item):
        """
        self.__getitem__(item) -> self[item]
        """
        return self.__content[item]

    def __setitem__(self, key, value):
        """ Set self[key] to value. """
        self.__content.__setitem__(key, value)

    def dump(self):
        """
        Dump self's contents into the config file.
        """
        with self.__path.open('w+', encoding='utf-8') as f:
            self.__yaml.dump(self.__content, f)

    def postgres(self) -> dict:
        """
        Return the content in self.__content['Postgres'] as strings.
        :return: content in self.__content['Postgres']
        """

        def convert(map_):
            if isinstance(map_, list):
                return [convert(s) for s in map_]
            elif isinstance(map_, CommentedMap):
                return {k: convert(v) for k, v in map_.items()}
            elif isinstance(map_, DoubleQuotedScalarString):
                return str(map_)

        return convert(self.__content['Postgres'])
