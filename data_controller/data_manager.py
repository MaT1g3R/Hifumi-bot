from sqlite3 import Connection, Cursor
from typing import List, Type, Union

from data_controller.data_rows import *
from scripts.helpers import assert_inputs, assert_outputs

__all__ = ['DataManager']
_row_types = Union[GuildRow, MemberRow, UserRow]


class DataManager:
    """
    A class that layer between the bot and the sqlite db. The bot should
    read/write to this class and the class will write to the db.
    """

    def __init__(self, connection: Connection, cursor: Cursor):
        """
        Initialize an instance of this class.
        :param connection: the sqlite3 connection.
        :param cursor: the sqlite3 cursor.
        """
        self.__connection = connection
        self.__cursor = cursor
        self.__guilds = {}
        self.__members = {}
        self.__users = {}

    def __get_row(self, dict_: dict, class_: Type[_row_types], *args):
        if args not in dict_:
            new = class_(self.__connection, self.__cursor, *args)
            dict_[args] = new
        return dict_[args]

    def __get_guild_row(self, guild_id: int) -> GuildRow:
        """
        Get a row in the guild_info table.
        :param guild_id: the guild id.
        :return: the row with the id guild_id.
        """
        return self.__get_row(self.__guilds, GuildRow, guild_id)

    def __get_member_row(self, member_id: int, guild_id: int) -> MemberRow:
        """
        Get a row in the member_info table.
        :param member_id: the member id
        :param guild_id: the guild id
        :return: the row with id (member_id, guild_id)
        """
        return self.__get_row(self.__members, MemberRow, member_id, guild_id)

    def __get_user_row(self, user_id: int) -> UserRow:
        """
        Get a row in the user_info table.
        :param user_id: the user id.
        :return: the row with id user_id.
        """
        return self.__get_row(self.__users, UserRow, user_id)

    def get_prefix(self, guild_id: int) -> str:
        """
        Get the prefix of the guild
        :param guild_id: the guild id
        """
        return self.__get_guild_row(guild_id).prefix

    def set_prefix(self, guild_id: int, prefix: str):
        """
        Set the prefix for a guild.
        :param guild_id: the guild id.
        :param prefix: the prefix to set to.
        """
        self.__get_guild_row(guild_id).prefix = prefix

    def get_language(self, guild_id: int) -> str:
        """
        Get the language of the guild
        :param guild_id: the guild id
        """
        return self.__get_guild_row(guild_id).language

    def set_language(self, guild_id: int, language: str):
        """
        Set the language of a guild.
        :param guild_id: the guild id of the guild.
        :param language: the language to set to.
        """
        self.__get_guild_row(guild_id).language = language

    def get_mod_log(self, guild_id: int) -> int:
        """
        Get the mod_log of the guild
        :param guild_id: the guild id
        """
        return self.__get_guild_row(guild_id).mod_log

    def set_mod_log(self, guild_id: int, channel_id: int):
        """
        Set the mod log channel of a guild.
        :param guild_id: the guild id.
        :param channel_id: the channel id of the mod log.
        """
        self.__get_guild_row(guild_id).mod_log = channel_id

    @assert_outputs(str, False)
    def get_roles(self, guild_id: int) -> List[str]:
        """
        Get the list of roles in the guild.
        :param guild_id: the guild id.
        """
        if self.__get_guild_row(guild_id).roles is not None:
            return eval(self.__get_guild_row(guild_id).roles)

    @assert_inputs(str, False)
    def set_roles(self, guild_id: int, roles: List[str]):
        """
        Set the role list for the guild.
        :param guild_id: the guild id.
        :param roles: the list of roles.
        """
        self.__get_guild_row(guild_id).roles = repr(roles)

    def get_member_warns(self, member_id: int, guild_id: int) -> int:
        """
        Get the number of warns on the member.
        :param member_id: the member id.
        :param guild_id: the guild id.
        :return: the number of warns on the member.
        """
        return self.__get_member_row(member_id, guild_id).warns

    def set_member_warns(self, member_id: int, guild_id: int, warns: int):
        """
        Set the number of warns on the member.
        :param member_id: the member id.
        :param guild_id: the guild id.
        :param warns: the number of warns to set to.
        """
        assert warns >= 0
        self.__get_member_row(member_id, guild_id).warns = warns

    def get_user_balance(self, user_id: int) -> int:
        """
        Get the balance of a user.
        :param user_id: the user id.
        :return: the balance of that user.
        """
        return self.__get_user_row(user_id).balance

    def set_user_balance(self, user_id: int, balance: int):
        """
        Set the balance of a user.
        :param user_id: the user id.
        :param balance: the balance to set to.
        """
        assert balance >= 0
        self.__get_user_row(user_id).balance = balance

    def get_user_daily(self, user_id: int) -> int:
        """
        Get the timestamp of the user's last daily..
        :param user_id: the user id.
        :return: the timestamp of the user's last daily.
        """
        return self.__get_user_row(user_id).daily

    def set_user_daily(self, user_id: int, time_stamp: int):
        """
        Refresh the user's daily timestamp to the current time.
        :param user_id: the user id.
        :param time_stamp: the timestamp for the daily.
        """
        self.__get_user_row(user_id).daily = time_stamp
