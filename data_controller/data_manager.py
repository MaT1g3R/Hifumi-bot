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

    def __init__(self, postgres: Postgres):
        """
        Initialize an instance of this class.
        :param postgres: the postgres controller.
        """
        self.__postgres = postgres
        self.__guilds = {}
        self.__members = {}
        self.__users = {}
        self.__classes = {
            _GuildRow: guild_row,
            _MemberRow: member_row,
            _UserRow: user_row
        }

    async def __get_row(self, dict_: dict, class_: Type[_row_types], *args):
        if args not in dict_:
            new = await self.__classes[class_](self.__postgres, *args)
            dict_[args] = new
        return dict_[args]

    async def __get_guild_row(self, guild_id: int) -> _GuildRow:
        """
        Get a row in the guild_info table.
        :param guild_id: the guild id.
        :return: the row with the id guild_id.
        """
        return await self.__get_row(self.__guilds, _GuildRow, guild_id)

    async def __get_member_row(
            self, member_id: int, guild_id: int) -> _MemberRow:
        """
        Get a row in the member_info table.
        :param member_id: the member id
        :param guild_id: the guild id
        :return: the row with id (member_id, guild_id)
        """
        return await self.__get_row(
            self.__members, _MemberRow, member_id, guild_id)

    async def __get_user_row(
            self, user_id: int) -> _UserRow:
        """
        Get a row in the user_info table.
        :param user_id: the user id.
        :return: the row with id user_id.
        """
        return await self.__get_row(self.__users, _UserRow, user_id)

    async def get_prefix(self, guild_id: int) -> str:
        """
        Get the prefix of the guild
        :param guild_id: the guild id
        """
        row = await self.__get_guild_row(guild_id)
        return row.prefix

    async def set_prefix(self, guild_id: int, prefix: str):
        """
        Set the prefix for a guild.
        :param guild_id: the guild id.
        :param prefix: the prefix to set to.
        """
        row = await self.__get_guild_row(guild_id)
        await row.set_prefix(prefix)

    async def get_language(self, guild_id: int) -> str:
        """
        Get the language of the guild
        :param guild_id: the guild id
        """
        row = await  self.__get_guild_row(guild_id)
        return row.language

    async def set_language(self, guild_id: int, language: str):
        """
        Set the language of a guild.
        :param guild_id: the guild id of the guild.
        :param language: the language to set to.
        """
        row = await self.__get_guild_row(guild_id)
        await row.set_language(language)

    async def get_mod_log(self, guild_id: int) -> int:
        """
        Get the mod_log of the guild
        :param guild_id: the guild id
        """
        row = await self.__get_guild_row(guild_id)
        return row.mod_log

    async def set_mod_log(self, guild_id: int, channel_id: Optional[int]):
        """
        Set the mod log channel of a guild.
        :param guild_id: the guild id.
        :param channel_id: the channel id of the mod log.
        """
        row = await self.__get_guild_row(guild_id)
        await row.set_mod_log(channel_id)

    async def get_roles(self, guild_id: int) -> List[str]:
        """
        Get the list of roles in the guild.
        :param guild_id: the guild id.
        """
        row = await self.__get_guild_row(guild_id)
        res = row.roles
        if res is not None:
            assert_types(res, str, False)
        return res

    async def set_roles(self, guild_id: int, roles: List[str]):
        """
        Set the role list for the guild.    @assert_outputs(str, False)

        :param guild_id: the guild id.
        :param roles: the list of roles.
        """
        assert_types(roles, str, False)
        row = await self.__get_guild_row(guild_id)
        await row.set_roles(roles)

    async def get_member_warns(self, member_id: int, guild_id: int) -> int:
        """
        Get the number of warns on the member.
        :param member_id: the member id.
        :param guild_id: the guild id.
        :return: the number of warns on the member.
        """
        row = await self.__get_member_row(member_id, guild_id)
        return row.warns

    async def set_member_warns(self, member_id: int, guild_id: int, warns: int):
        """
        Set the number of warns on the member.
        :param member_id: the member id.
        :param guild_id: the guild id.
        :param warns: the number of warns to set to.
        """
        assert warns >= 0
        row = await self.__get_member_row(member_id, guild_id)
        await row.set_warns(warns)

    async def get_user_balance(self, user_id: int) -> int:
        """
        Get the balance of a user.
        :param user_id: the user id.
        :return: the balance of that user.
        """
        row = await self.__get_user_row(user_id)
        return row.balance

    async def set_user_balance(self, user_id: int, balance: int):
        """
        Set the balance of a user.
        :param user_id: the user id.
        :param balance: the balance to set to.
        """
        assert balance >= 0
        row = await self.__get_user_row(user_id)
        await row.set_balance(balance)

    async def get_user_daily(self, user_id: int) -> datetime:
        """
        Get the timestamp of the user's last daily..
        :param user_id: the user id.
        :return: the timestamp of the user's last daily.
        """
        row = await self.__get_user_row(user_id)
        return row.daily

    async def set_user_daily(self, user_id: int, time_stamp: datetime):
        """
        Refresh the user's daily timestamp to the current time.
        :param user_id: the user id.
        :param time_stamp: the timestamp for the daily.
        """
        row = await self.__get_user_row(user_id)
        await row.set_daily(time_stamp)
