"""
A collection of classes that represent a row in the sqlite database
"""
from sqlite3 import Connection, Cursor
from typing import Sequence
from data_controller.data_controller import _get_guild_row, _write_guild_row, \
    _get_member_row, _write_member_row, _get_user_row, _write_user_row


class _Row:
    """
    A generic row object
    """

    def __init__(
            self, connection: Connection, cursor: Cursor, row_data: Sequence):
        """
        Initialize this class with sqlite3 connection and cursor objects
        :param connection: the sqlite3 connection
        :param cursor: sqlite3 cursor
        :param row_data: the data of this row
        """
        self.connection = connection
        self.cursor = cursor
        self.row_data = list(row_data)


class GuildRow:
    """
    Represents a row in the guild_info table
    """

    def __init__(self, connection: Connection, cursor: Cursor, guild_id: int):
        """
        Initialize an instance of _GuildRow
        :param connection: the sqlite3 connection object
        :param cursor: the sqlite3 cursor object
        :param guild_id: the guild id
        """
        self.__row = _Row(
            connection, cursor, _get_guild_row(cursor, guild_id)
        )

    def __write(self):
        """
        Write self's row values into the db
        """
        _write_guild_row(
            self.__row.connection, self.__row.cursor, self.__row.row_data
        )

    @property
    def guild_id(self) -> int:
        return self.__row.row_data[0]

    @property
    def prefix(self) -> str:
        return self.__row.row_data[1]

    @property
    def language(self) -> str:
        return self.__row.row_data[2]

    @property
    def mod_log(self) -> int:
        return self.__row.row_data[3]

    @property
    def roles(self) -> str:
        return self.__row.row_data[4]

    @prefix.setter
    def prefix(self, prefix: str):
        self.__row.row_data[1] = prefix
        self.__write()

    @language.setter
    def language(self, language: str):
        self.__row.row_data[2] = language
        self.__write()

    @mod_log.setter
    def mod_log(self, mod_log: int):
        self.__row.row_data[3] = mod_log
        self.__write()

    @roles.setter
    def roles(self, roles: str):
        self.__row.row_data[4] = roles
        self.__write()


class MemberRow:
    """
    Represents a row in member_info table
    """

    def __init__(
            self, connection: Connection, cursor: Cursor,
            member_id: int, guild_id: int):
        """
        Initialize an instance of _MemberRow
        :param connection: the sqlite3 connection.
        :param cursor: the sqlite3 cursor.
        :param member_id: the member id.
        :param guild_id: the guild id of that member.
        """
        self.__row = _Row(
            connection, cursor,
            _get_member_row(cursor, member_id, guild_id)
        )

    def __write(self):
        """
        Write self's row values into the db
        """
        _write_member_row(
            self.__row.connection, self.__row.cursor, self.__row.row_data
        )

    @property
    def member_id(self) -> int:
        return self.__row.row_data[0]

    @property
    def guild_id(self) -> int:
        return self.__row.row_data[1]

    @property
    def warns(self) -> int:
        return self.__row.row_data[2]

    @warns.setter
    def warns(self, warns: int):
        self.__row.row_data[2] = warns
        self.__write()


class UserRow:
    def __init__(self, connection: Connection, cursor: Cursor, user_id: int):
        """
        Initialize an instance of _UserRow
        :param connection: the sqlite3 connection
        :param cursor: the sqlite3 cursor
        :param user_id: the user id
        """
        self.__row = _Row(connection, cursor, _get_user_row(cursor, user_id))

    def __write(self):
        """
        Write self's row values into the db
        """
        _write_user_row(
            self.__row.connection, self.__row.cursor, self.__row.row_data
        )

    @property
    def user_id(self) -> int:
        return self.__row.row_data[0]

    @property
    def balance(self) -> int:
        return self.__row.row_data[1]

    @property
    def daily(self) -> int:
        return self.__row.row_data[2]

    @balance.setter
    def balance(self, balance: int):
        self.__row.row_data[1] = balance
        self.__write()

    @daily.setter
    def daily(self, daily: int):
        self.__row.row_data[2] = daily
        self.__write()
