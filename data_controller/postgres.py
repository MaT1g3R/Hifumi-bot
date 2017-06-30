from collections import deque
from datetime import datetime
from typing import Dict, List, Optional, Sequence

from asyncpg import Record
from asyncpg.pool import Pool

from scripts.helpers import assert_types

# Types expected for the different tables
_guild_types = (str, str, str, str, list)
_member_types = (str, str, int)
_user_types = (str, int, datetime)
_tag_types = (str, str)


def _parse_record(record: Record) -> Optional[tuple]:
    """
    Parse a asyncpg Record object to a tuple of values
    :param record: the asyncpg Record object
    :return: the tuple of values if it's not None, else None
    """
    try:
        return tuple(record.values())
    except AttributeError:
        return None


class Postgres:
    """
    A Postgres database controller, this is not meant to be accessed directly
    with the bot. For bot use, please use the DataManager class.
    """

    def __init__(self, pool: Pool, schema, logger):
        """
        Initialize the instance of this class.
        :param pool: the asyncpg connection pool.
        :param logger: the logger.
        """
        self.queue = deque()
        self.logger = logger
        self.pool = pool
        self.__get_guild = (
            'SELECT * FROM {}.guild_info WHERE guild_id = $1'.format(schema)
        )
        self.__set_guild = (
            'INSERT INTO {}.guild_info VALUES ($1, $2, $3, $4, $5) '
            'ON CONFLICT (guild_id) '
            'DO UPDATE SET prefix=$2, lan=$3, mod_log=$4, roles=$5'.format(
                schema)
        )
        self.__get_member = (
            'SELECT * FROM {}.member_info '
            'WHERE member_id=$1 AND guild_id=$2'.format(schema)
        )
        self.__set_member = (
            'INSERT INTO {}.member_info VALUES ($1, $2, $3) '
            'ON CONFLICT (member_id, guild_id)'
            'DO UPDATE SET warns=$3'.format(schema)
        )
        self.__get_user = (
            'SELECT * FROM {}.user_info WHERE user_id=$1'.format(schema)
        )
        self.__set_user = (
            'INSERT INTO {}.user_info VALUES ($1, $2, $3) '
            'ON CONFLICT (user_id) '
            'DO UPDATE SET balance=$2, daily=$3'.format(schema)
        )
        self.__get_tags = 'SELECT * FROM {}.nsfw_tags'.format(schema)
        self.__set_tags = (
            'INSERT INTO {}.nsfw_tags VALUES ($1, $2) '
            'ON CONFLICT (site, tag_name) '
            'DO NOTHING'.format(schema)
        )
        self.__get_all_guild = 'SELECT * FROM {}.guild_info'.format(schema)
        self.__get_all_member = 'SELECT * FROM {}.member_info'.format(schema)
        self.__get_all_user = 'SELECT * FROM {}.user_info'.format(schema)

    async def get_guild(self, guild_id: str) -> tuple:
        """
        Get guild row by id.
        :param guild_id: the guild id.
        :return: the guild row.
        """
        _res = await self.pool.fetchrow(self.__get_guild, guild_id)
        res = _parse_record(_res) or (None,) * len(_guild_types)
        assert_types(res, _guild_types, True)
        return res

    async def get_all_guild(self) -> List[tuple]:
        """
        Get all guild rows in the db.
        :return: A list of guild rows
        """
        res = await self.pool.fetch(self.__get_all_guild)
        return [_parse_record(r) for r in res]

    async def set_guild(self, values: Sequence):
        """
        Set a guild row.
        :param values: the values of that row.
        """
        assert_types(values, _guild_types, True)
        await self.pool.execute(self.__set_guild, *values)

    async def get_member(self, member_id: str, guild_id: str) -> tuple:
        """
        Get a member row.
        :param member_id: the member id.
        :param guild_id: the guild id.
        :return: the member row.
        """
        _res = await self.pool.fetchrow(self.__get_member, member_id, guild_id)
        res = _parse_record(_res) or (None,) * len(_member_types)
        assert_types(res, _member_types, True)
        return res

    async def get_all_member(self) -> List[tuple]:
        """
        Get all member rows from the db.
        :return: A list of all member rows.
        """
        res = await self.pool.fetch(self.__get_all_member)
        return [_parse_record(r) for r in res]

    async def set_member(self, values: Sequence):
        """
        Set a member row.
        :param values: the values of that row.
        """
        assert_types(values, _member_types, True)
        await self.pool.execute(self.__set_member, *values)

    async def get_user(self, user_id: str) -> tuple:
        """
        Get a user row.
        :param user_id: the user id. 
        :return: the values of that row.
        """
        _res = await self.pool.fetchrow(self.__get_user, user_id)
        res = _parse_record(_res) or (None,) * len(_user_types)
        assert_types(res, _user_types, True)
        return res

    async def get_all_user(self) -> List[tuple]:
        """
        Get all user row.
        :return: a list of all user rows.
        """
        res = await self.pool.fetch(self.__get_all_user)
        return [_parse_record(r) for r in res]

    async def set_user(self, values: Sequence):
        """
        Set a user row.
        :param values: the values of that row.
        """
        assert_types(values, _user_types, True)
        await self.pool.execute(self.__set_user, *values)

    async def get_tags(self) -> Dict[str, List[str]]:
        """
        Get all tags stored in the DB.
        :return: A dict of {site name: list of tags in that site}
        """
        rows = await self.pool.fetch(self.__get_tags)
        res = {}
        for row in rows:
            parsed = _parse_record(row) or []
            if all(parsed) and len(parsed) == 2:
                k, v = parsed
                if k in res:
                    res[k].append(v)
                else:
                    res[k] = [v]
        return res

    async def set_tags(self, site: str, tags: List[str]):
        """
        Set(Append) tags for a site.
        :param site: the site name.
        :param tags: the list of tags.
        """
        args = [(site, tag) for tag in tags]
        await self.pool.executemany(self.__set_tags, args)
