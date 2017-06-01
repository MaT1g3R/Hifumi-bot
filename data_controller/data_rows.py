"""
A collection of classes that represent a row in the sqlite database
"""
from sqlite3 import Connection, Cursor

from data_controller.data_controller import _get_guild_row, _write_guild_row


def _write_guild(func):
    """
    Decorator for class _GuildRow's setters to write into the db
    when it's called
    """

    def wrapper(self, arg):
        func(self, arg)
        _write_guild_row(
            self._row.cursor, self._row.connection, self._row.row_data
        )

    return wrapper


class _Row:
    """
    A generic row object
    """

    def __init__(self, connection: Connection, cursor: Cursor, row_data: list):
        """
        Initialize this class with sqlite3 connection and cursor objects
        :param connection: the sqlite3 connection
        :param cursor: sqlite3 cursor
        :param row_data: the data of this row
        """
        self.connection = connection
        self.cursor = cursor
        self.row_data = row_data


class _GuildRow:
    """
    Represents a row in the guild_info table
    """

    def __init__(self, guild_id: int, connection: Connection, cursor: Cursor):
        """
        Initialize an instance of this class
        :param guild_id: the guild id
        :param connection: the sqlite3 connection object
        :param cursor: the sqlite3 cursor object
        """
        self._row = _Row(
            connection, cursor, list(_get_guild_row(cursor, guild_id))
        )
        # self.guild_id, \
        #     self.prefix, \
        #     self.language, \
        #     self.mod_log, \
        #     self.roles = self._row.row_data
        assert isinstance(self._row.row_data[4], list) or \
               self._row.row_data[4] is None

    @property
    def guild_id(self) -> int:
        return self._row.row_data[0]

    @property
    def prefix(self) -> str:
        return self._row.row_data[1]

    @property
    def language(self) -> str:
        return self._row.row_data[2]

    @property
    def mod_log(self) -> int:
        return self._row.row_data[3]

    @property
    def roles(self) -> list:
        return self._row.row_data[4]

    @prefix.setter
    @_write_guild
    def prefix(self, prefix):
        self._row.row_data[1] = prefix

    @language.setter
    @_write_guild
    def language(self, language):
        self._row.row_data[2] = language
