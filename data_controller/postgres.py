from asyncio import sleep
from collections import deque
from datetime import datetime
from typing import Dict, List, Optional, Sequence

from asyncpg import Connection, Record
from asyncpg.prepared_stmt import PreparedStatement

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


def execute_task(high):
    """
    A decorator to ensure only one task in class Postgres is being executed
    at once.
    :param high: the importance of the task. True for high, Fasle for low.
    """

    def dec(coro):
        async def wraps(*args):
            f = coro(*args)
            postgres = args[0]
            postgres.queue_task(f, high)
            if high:
                while not postgres.high_priority_q[0] is f:
                    await sleep(0.1)
                assert f is postgres.high_priority_q[0]
            else:
                while not (postgres.low_priority_q[0] is f
                           and len(postgres.high_priority_q) == 0):
                    await sleep(0.1)
                assert f is postgres.low_priority_q[0]
            res = await f
            if high:
                postgres.high_priority_q.popleft()
            else:
                postgres.low_priority_q.popleft()
            return res

        return wraps

    return dec


class Postgres:
    """
    A Postgres database controller, this is not meant to be accessed directly
    with the bot. For bot use, please use the DataManager class.
    """

    def __init__(self, conn: Connection, schema):
        """
        Initialize the instance of this class.
        :param conn: the asyncpg connection.
        :param schema: the schema name.
        """
        self.__conn: Connection = conn

        self.__get_guild: PreparedStatement = None
        self.__set_guild: PreparedStatement = None
        self.__get_member: PreparedStatement = None
        self.__set_member: PreparedStatement = None
        self.__get_user: PreparedStatement = None
        self.__set_user: PreparedStatement = None
        self.__get_tags: PreparedStatement = None
        self.__set_tags: PreparedStatement = None
        self.schema = schema
        self.high_priority_q = deque()
        self.low_priority_q = deque()

    def queue_task(self, coro, high):
        """
        Queue a task into one of the two task queues.
        :param coro: the coroutine to be queued.
        :param high: True to send to high importance queue.
        """
        if high:
            self.high_priority_q.append(coro)
        else:
            self.low_priority_q.append(coro)

    async def init(self):
        """
        Prepare the queries that will be used.
        """
        f = self.__conn.prepare
        schema = self.schema

        self.__get_guild = await f(
            'SELECT * FROM {}.guild_info WHERE guild_id = $1'.format(schema)
        )

        self.__set_guild = await f(
            'INSERT INTO {}.guild_info VALUES ($1, $2, $3, $4, $5) '
            'ON CONFLICT (guild_id) '
            'DO UPDATE SET prefix=$2, lan=$3, mod_log=$4, roles=$5'.format(
                schema)
        )

        self.__get_member = await f(
            'SELECT * FROM {}.member_info '
            'WHERE member_id=$1 AND guild_id=$2'.format(schema)
        )

        self.__set_member = await f(
            'INSERT INTO {}.member_info VALUES ($1, $2, $3) '
            'ON CONFLICT (member_id, guild_id)'
            'DO UPDATE SET warns=$3'.format(schema)
        )

        self.__get_user = await f(
            'SELECT * FROM {}.user_info WHERE user_id=$1'.format(schema)
        )

        self.__set_user = await f(
            'INSERT INTO {}.user_info VALUES ($1, $2, $3) '
            'ON CONFLICT (user_id) '
            'DO UPDATE SET balance=$2, daily=$3'.format(schema)
        )

        self.__get_tags = await f('SELECT * FROM {}.nsfw_tags'.format(schema))

    @execute_task(True)
    async def get_guild(self, guild_id: str) -> tuple:
        """
        Get guild row by id.
        :param guild_id: the guild id.
        :return: the guild row.
        """

        res = (_parse_record(await self.__get_guild.fetchrow(guild_id)) or
               (None,) * len(_guild_types))
        assert_types(res, _guild_types, True)
        return res

    @execute_task(True)
    async def get_all_guild(self) -> List[tuple]:
        """
        Get all guild rows in the db.
        :return: A list of guild rows
        """

        sql = 'SELECT * FROM {}.guild_info'.format(self.schema)
        res = await self.__conn.fetch(sql)
        return [_parse_record(r) for r in res]

    @execute_task(True)
    async def set_guild(self, values: Sequence):
        """
        Set a guild row.
        :param values: the values of that row.
        """

        assert_types(values, _guild_types, True)
        await self.__set_guild.fetch(*values)

    @execute_task(True)
    async def get_member(self, member_id: str, guild_id: str) -> tuple:
        """
        Get a member row.
        :param member_id: the member id.
        :param guild_id: the guild id.
        :return: the member row.
        """

        res = (
            _parse_record(await self.__get_member.fetchrow(member_id, guild_id))
            or (None,) * len(_member_types)
        )
        assert_types(res, _member_types, True)
        return res

    @execute_task(True)
    async def get_all_member(self) -> List[tuple]:
        """
        Get all member rows from the db.
        :return: A list of all member rows.
        """
        sql = 'SELECT * FROM {}.member_info'.format(self.schema)
        res = await self.__conn.fetch(sql)
        return [_parse_record(r) for r in res]

    @execute_task(True)
    async def set_member(self, values: Sequence):
        """
        Set a member row.
        :param values: the values of that row.
        """
        assert_types(values, _member_types, True)
        await self.__set_member.fetch(*values)

    @execute_task(True)
    async def get_user(self, user_id: str) -> tuple:
        """
        Get a user row.
        :param user_id: the user id. 
        :return: the values of that row.
        """
        res = (_parse_record(await self.__get_user.fetchrow(user_id)) or
               (None,) * len(_user_types))
        assert_types(res, _user_types, True)
        return res

    @execute_task(True)
    async def get_all_user(self) -> List[tuple]:
        """
        Get all user row.
        :return: a list of all user rows.
        """
        sql = 'SELECT * FROM {}.user_info'.format(self.schema)
        res = await self.__conn.fetch(sql)
        return [_parse_record(r) for r in res]

    @execute_task(True)
    async def set_user(self, values: Sequence):
        """
        Set a user row.
        :param values: the values of that row.
        """
        assert_types(values, _user_types, True)
        await self.__set_user.fetch(*values)

    @execute_task(False)
    async def get_tags(self) -> Dict[str, List[str]]:
        """
        Get all tags stored in the DB.
        :return: A dict of {site name: list of tags in that site}
        """
        rows = await self.__get_tags.fetch()
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

    @execute_task(False)
    async def set_tags(self, site: str, tags: List[str]):
        """
        Set(Append) tags for a site.
        :param site: the site name.
        :param tags: the list of tags.
        """
        sql = (
            'INSERT INTO {}.nsfw_tags VALUES ($1, $2) '
            'ON CONFLICT (site, tag_name) '
            'DO NOTHING'.format(self.schema)
        )
        args = [(site, tag) for tag in tags]
        await self.__conn.executemany(sql, args)


async def get_postgres(conn: Connection, schema: str) -> Postgres:
    res = Postgres(conn, schema)
    await res.init()
    return res
