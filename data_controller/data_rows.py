"""
A collection of classes that represent a row in the sqlite database
"""
from datetime import datetime
from typing import List

from data_controller.postgres import Postgres

__all__ = ['_GuildRow', '_MemberRow', '_UserRow', 'get_guild_row',
           'get_member_row', 'get_user_row']


class _Row:
    __slots__ = ['_postgres', '_row']

    def __init__(self, postgres: Postgres, row=None):
        """
        Initialize an instance of _Row
        :param postgres: the postgres controller.
        :param row: the row value for the row, optional parameter.
        """
        self._postgres = postgres
        self._row = list(row) or []

    async def _write(self):
        """
        Write self's row values into the db
        """
        raise NotImplementedError

    async def _set(self, pos: int, val):
        """
        Helper method to set a value of the row.
        :param pos: the position of the value.
        :param val: the value to set to.
        """
        if self._row[pos] != val:
            self._row[pos] = val
            await self._write()


class _GuildRow(_Row):
    """
    Represents a row in the guild_info table
    """

    def __init__(self, postgres: Postgres, row_val=None):
        """
        Initialize an instance of _GuildRow
        :param postgres: the postgres controller.
        :param row_val: the row values for this row, optional.
        """
        super().__init__(postgres, row_val)

    async def _write(self):
        """
        Write self's row values into the db
        """
        await self._postgres.set_guild(self._row)

    @property
    def guild_id(self) -> int:
        return int(self._row[0])

    @property
    def prefix(self) -> str:
        return self._row[1]

    @property
    def language(self) -> str:
        return self._row[2]

    @property
    def mod_log(self) -> int:
        if self._row[3]:
            return int(self._row[3])

    @property
    def roles(self) -> list:
        return self._row[4]

    async def set_prefix(self, prefix: str):
        await self._set(1, prefix)

    async def set_language(self, language: str):
        await self._set(2, language)

    async def set_mod_log(self, mod_log: int):
        if isinstance(mod_log, int):
            await self._set(3, str(mod_log))
        else:
            await self._set(3, None)

    async def set_roles(self, roles: List[str]):
        await self._set(4, roles)


class _MemberRow(_Row):
    """
    Represents a row in member_info table
    """

    def __init__(self, postgres: Postgres, row_val=None):
        """
        Initialize an instance of MemberRow
        :param postgres: the postgres controller.
        :param row_val: the row values for this row, optional.
        """
        super().__init__(postgres, row_val)

    async def _write(self):
        """
        Write self's row values into the db
        """
        await self._postgres.set_member(self._row)

    @property
    def member_id(self) -> int:
        return int(self._row[0])

    @property
    def guild_id(self) -> int:
        return int(self._row[1])

    @property
    def warns(self) -> int:
        return self._row[2]

    async def set_warns(self, warns: int):
        await self._set(2, warns)


class _UserRow(_Row):
    """
    Represents a row in user_info table
    """

    def __init__(self, postgres: Postgres, row_val=None):
        """
        Initialize an instance of UserRow
        :param postgres: the postgres controller.
        :param row_val: the row values for this row, optional
        """
        super().__init__(postgres, row_val)

    async def _write(self):
        """
        Write self's row values into the db
        """
        await self._postgres.set_user(self._row)

    @property
    def user_id(self) -> int:
        return int(self._row[0])

    @property
    def balance(self) -> int:
        return self._row[1]

    @property
    def daily(self) -> datetime:
        return self._row[2]

    async def set_balance(self, balance: int):
        await self._set(1, balance)

    async def set_daily(self, daily: datetime):
        await self._set(2, daily)


def get_guild_row(postgres: Postgres, guild_id: int, row_val=None):
    default = (str(guild_id), None, None, None, None)
    res = row_val or default
    return _GuildRow(postgres, res)


def get_member_row(postgres: Postgres, member_id: int, guild_id: int,
                   row_val=None):
    default = (str(member_id), str(guild_id), None)
    res = row_val or default
    return _MemberRow(postgres, res)


def get_user_row(postgres: Postgres, user_id: int, row_val=None):
    default = (str(user_id), None, None)
    res = row_val or default
    return _UserRow(postgres, res)
