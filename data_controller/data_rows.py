"""
A collection of classes that represent a row in the sqlite database
"""
from datetime import datetime
from typing import List

from data_controller.postgres import Postgres

__all__ = ['_GuildRow', '_MemberRow', '_UserRow', 'guild_row', 'member_row',
           'user_row']


class _Row:
    def __init__(self, postgres: Postgres):
        """
        Initialize an instance of _Row
        :param postgres: the postgres controller.
        """
        self._postgres = postgres
        self._row = []

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

    def __init__(self, postgres: Postgres):
        """
        Initialize an instance of _GuildRow
        :param postgres: the postgres controller.
        """
        super().__init__(postgres)

    async def init(self, guild_id: int):
        """
        Set up this instance's data.
        :param guild_id: the guild id.
        """
        row = await self._postgres.get_guild(guild_id)
        if row[0] is None:
            row = (guild_id,) + row[1:]
        self._row = list(row)
        assert self._row[0] is not None

    async def _write(self):
        """
        Write self's row values into the db
        """
        await self._postgres.set_guild(self._row)

    @property
    def guild_id(self) -> int:
        return self._row[0]

    @property
    def prefix(self) -> str:
        return self._row[1]

    @property
    def language(self) -> str:
        return self._row[2]

    @property
    def mod_log(self) -> int:
        return self._row[3]

    @property
    def roles(self) -> list:
        return self._row[4]

    async def set_prefix(self, prefix: str):
        await self._set(1, prefix)

    async def set_language(self, language: str):
        await self._set(2, language)

    async def set_mod_log(self, mod_log: int):
        await self._set(3, mod_log)

    async def set_roles(self, roles: List[str]):
        await self._set(4, roles)


class _MemberRow(_Row):
    """
    Represents a row in member_info table
    """

    def __init__(self, postgres: Postgres):
        """
        Initialize an instance of MemberRow
        :param postgres: the postgres controller.
        """
        super().__init__(postgres)

    async def init(self, member_id: int, guild_id: int):
        """
        Set up this instance's data.
        :param member_id: the member id.
        :param guild_id: the guild id of that member.
        """
        row = await self._postgres.get_member(member_id, guild_id)
        if row[0] is None and row[1] is None:
            row = (member_id, guild_id) + row[2:]
        elif row[0] is None or row[1] is None:
            raise RuntimeError(
                'One of (member_id, guild_id) read from the '
                'database is None and the other isn\'t None.'
            )
        self._row = list(row)
        assert self._row[0] is not None
        assert self._row[1] is not None

    async def _write(self):
        """
        Write self's row values into the db
        """
        await self._postgres.set_member(self._row)

    @property
    def member_id(self) -> int:
        return self._row[0]

    @property
    def guild_id(self) -> int:
        return self._row[1]

    @property
    def warns(self) -> int:
        return self._row[2]

    async def set_warns(self, warns: int):
        await self._set(2, warns)


class _UserRow(_Row):
    """
    Represents a row in user_info table
    """

    def __init__(self, postgres: Postgres):
        """
        Initialize an instance of UserRow
        :param postgres: the postgres controller.
        """
        super().__init__(postgres)

    async def init(self, user_id: int):
        """
        Set up this instance's data.
        :param user_id: the user id
        """
        row = await self._postgres.get_user(user_id)
        if row[0] is None:
            row = (user_id,) + row[1:]
        self._row = list(row)
        assert self._row[0] is not None

    async def _write(self):
        """
        Write self's row values into the db
        """
        await self._postgres.set_user(self._row)

    @property
    def user_id(self) -> int:
        return self._row[0]

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


async def guild_row(postgres: Postgres, guild_id: int) -> _GuildRow:
    res = _GuildRow(postgres)
    await res.init(guild_id)
    return res


async def member_row(
        postgres: Postgres, member_id: int, guild_id: int) -> _MemberRow:
    res = _MemberRow(postgres)
    await res.init(member_id, guild_id)
    return res


async def user_row(postgres: Postgres, user_id: int) -> _UserRow:
    res = _UserRow(postgres)
    await res.init(user_id)
    return res
