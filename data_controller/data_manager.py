from sqlite3 import connect
from data_controller.data_rows import GuildRow, MemberRow, UserRow
from typing import Union, List
from pathlib import Path
from scripts.helpers import assert_inputs, assert_outputs


class TransferError(ValueError):
    pass


class DataManager:
    """
    A class that layer between the bot and the sqlite db. The bot should
    read/write to this class and the class will write to the db.
    """
    __row_types = Union(GuildRow, MemberRow, UserRow)

    def __init__(self, path: Path):
        """
        Initialize an instance of this class.
        :param path: the path that points to the db
        """
        self.__connection = connect(str(path))
        self.__cursor = self.__connection.cursor()
        self.__tables = {}

    def __get_row(self, row_type: __row_types, *keys) -> __row_types:
        """
        Get a row by its type and keys, if the row does not exist already,
        create a new row with the keys.
        :param row_type: the row type.
        :param keys: the keys to the row.
        :return: the row with the keys.
        """
        if keys not in self.__tables[row_type]:
            new_row = row_type(self.__connection, self.__cursor, *keys)
            self.__tables[row_type][keys] = new_row
            return new_row

        return self.__tables[row_type][keys]

    def __get_guild_row(self, guild_id: int) -> GuildRow:
        """
        Get a row in the guild_info table.
        :param guild_id: the guild id.
        :return: the row with the id guild_id.
        """
        return self.__get_row(GuildRow, guild_id)

    def __get_member_row(self, member_id: int, guild_id: int) -> MemberRow:
        """
        Get a row in the member_info table.
        :param member_id: the member id
        :param guild_id: the guild id
        :return: the row with id (member_id, guild_id)
        """
        return self.__get_row(MemberRow, member_id, guild_id)

    def __get_user_row(self, user_id: int) -> UserRow:
        """
        Get a row in the user_info table.
        :param user_id: the user id.
        :return: the row with id user_id.
        """
        return self.__get_row(UserRow, user_id)

    def get_prefix(self, guild_id: int) -> str:
        """
        Get the prefix of the guild
        :param guild_id: the guild id
        """
        return self.__get_guild_row(guild_id).prefix

    def get_language(self, guild_id: int) -> str:
        """
        Get the language of the guild
        :param guild_id: the guild id
        """
        return self.__get_guild_row(guild_id).language

    def get_mod_log(self, guild_id: int) -> int:
        """
        Get the mod_log of the guild
        :param guild_id: the guild id
        """
        return self.__get_guild_row(guild_id).mod_log

    @assert_outputs(str, False)
    def get_roles(self, guild_id: int) -> List[str]:
        """
        Get the list of roles in the guild
        :param guild_id: the guild id
        """
        return eval(self.__get_guild_row(guild_id).roles)

    def set_prefix(self, guild_id: int, prefix: str):
        """
        Set the prefix for a guild.
        :param guild_id: the guild id.
        :param prefix: the prefix to set to.
        """
        self.__get_guild_row(guild_id).prefix = prefix
