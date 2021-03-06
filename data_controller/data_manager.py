from datetime import datetime
from typing import List, Optional, Type, Union

from data_controller.data_rows import *
from data_controller.postgres import Postgres
from scripts.helpers import assert_types

__all__ = ['DataManager']
_row_types = Union[_GuildRow, _MemberRow, _UserRow]


class DataManager:
    """
    A class that layer between the bot and the sqlite db. The bot should
    read/write to this class and the class will write to the db.
    """
    __slots__ = ['__postgres', '__guilds', '__members', '__users',
                 '__initializers']

    def __init__(self, postgres: Postgres):
        """
        Initialize an instance of this class.
        :param postgres: the postgres controller.
        """
        self.__postgres = postgres
        self.__guilds = {}
        self.__members = {}
        self.__users = {}
        self.__initializers = {
            _UserRow: get_user_row,
            _MemberRow: get_member_row,
            _GuildRow: get_guild_row
        }

    async def init(self):
        """
        Initialize self.__guilds with some values.
        """
        guilds = await self.__postgres.get_all_guild()
        members = await self.__postgres.get_all_member()
        users = await self.__postgres.get_all_user()
        for guild in guilds:
            row = _GuildRow(self.__postgres, guild)
            key = int(guild[0])
            self.__guilds[key] = row
        for member in members:
            row = _MemberRow(self.__postgres, member)
            key = int(member[0]), int(member[1])
            self.__members[key] = row
        for user in users:
            row = _UserRow(self.__postgres, user)
            key = int(user[0])
            self.__users[key] = row

    def __get_row(self, dict_: dict, class_: Type[_row_types], key):
        try:
            return dict_[key]
        except KeyError:
            if isinstance(key, tuple):
                new = self.__initializers[class_](self.__postgres, *key)
            else:
                new = self.__initializers[class_](self.__postgres, key)
            dict_[key] = new
            return new

    def __get_guild_row(self, guild_id: int) -> _GuildRow:
        """
        Get a row in the guild_info table.
        :param guild_id: the guild id.
        :return: the row with the id guild_id.
        """
        return self.__get_row(self.__guilds, _GuildRow, guild_id)

    def __get_member_row(
            self, member_id: int, guild_id: int) -> _MemberRow:
        """
        Get a row in the member_info table.
        :param member_id: the member id
        :param guild_id: the guild id
        :return: the row with id (member_id, guild_id)
        """
        key = (member_id, guild_id)
        return self.__get_row(self.__members, _MemberRow, key)

    def __get_user_row(
            self, user_id: int) -> _UserRow:
        """
        Get a row in the user_info table.
        :param user_id: the user id.
        :return: the row with id user_id.
        """
        return self.__get_row(self.__users, _UserRow, user_id)

    def get_prefix(self, guild_id: int) -> str:
        """
        Get the prefix of the guild
        :param guild_id: the guild id
        """
        return self.__get_guild_row(guild_id).prefix

    async def set_prefix(self, guild_id: int, prefix: str):
        """
        Set the prefix for a guild.
        :param guild_id: the guild id.
        :param prefix: the prefix to set to.
        """
        row = self.__get_guild_row(guild_id)
        await row.set_prefix(prefix)

    def get_language(self, guild_id: int) -> str:
        """
        Get the language of the guild
        :param guild_id: the guild id
        """
        return self.__get_guild_row(guild_id).language

    async def set_language(self, guild_id: int, language: str):
        """
        Set the language of a guild.
        :param guild_id: the guild id of the guild.
        :param language: the language to set to.
        """
        row = self.__get_guild_row(guild_id)
        await row.set_language(language)

    def get_mod_log(self, guild_id: int) -> int:
        """
        Get the mod_log of the guild
        :param guild_id: the guild id
        """
        return self.__get_guild_row(guild_id).mod_log

    async def set_mod_log(self, guild_id: int, channel_id: Optional[int]):
        """
        Set the mod log channel of a guild.
        :param guild_id: the guild id.
        :param channel_id: the channel id of the mod log.
        """
        row = self.__get_guild_row(guild_id)
        await row.set_mod_log(channel_id)

    def get_roles(self, guild_id: int) -> List[str]:
        """
        Get the list of roles in the guild.
        :param guild_id: the guild id.
        """
        res = self.__get_guild_row(guild_id).roles
        if res is not None:
            assert_types(res, str, False)
        return res

    async def set_roles(self, guild_id: int, roles: List[str]):
        """
        Set the role list for the guild.

        :param guild_id: the guild id.
        :param roles: the list of roles.
        """
        assert_types(roles, str, False)
        row = self.__get_guild_row(guild_id)
        await row.set_roles(roles)

    def get_member_warns(self, member_id: int, guild_id: int) -> int:
        """
        Get the number of warns on the member.
        :param member_id: the member id.
        :param guild_id: the guild id.
        :return: the number of warns on the member.
        """
        return self.__get_member_row(member_id, guild_id).warns

    async def set_member_warns(self, member_id: int, guild_id: int, warns: int):
        """
        Set the number of warns on the member.
        :param member_id: the member id.
        :param guild_id: the guild id.
        :param warns: the number of warns to set to.
        """
        assert warns >= 0
        row = self.__get_member_row(member_id, guild_id)
        await row.set_warns(warns)

    def get_user_balance(self, user_id: int) -> int:
        """
        Get the balance of a user.
        :param user_id: the user id.
        :return: the balance of that user.
        """
        return self.__get_user_row(user_id).balance

    async def set_user_balance(self, user_id: int, balance: int):
        """
        Set the balance of a user.
        :param user_id: the user id.
        :param balance: the balance to set to.
        """
        assert 0 <= balance < 9223372036854775807
        row = self.__get_user_row(user_id)
        await row.set_balance(balance)

    def get_user_daily(self, user_id: int) -> datetime:
        """
        Get the timestamp of the user's last daily..
        :param user_id: the user id.
        :return: the timestamp of the user's last daily.
        """
        return self.__get_user_row(user_id).daily

    async def set_user_daily(self, user_id: int, time_stamp: datetime):
        """
        Refresh the user's daily timestamp to the current time.
        :param user_id: the user id.
        :param time_stamp: the timestamp for the daily.
        """
        row = self.__get_user_row(user_id)
        await row.set_daily(time_stamp)
