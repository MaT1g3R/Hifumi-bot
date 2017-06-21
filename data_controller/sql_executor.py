from datetime import time
from typing import Dict, List, Sequence

from asyncpg import Connection, connect
from asyncpg.cursor import Cursor
from asyncpg.prepared_stmt import PreparedStatement

from scripts.helpers import assert_types

# Types expected for the different tables
_guild_types = (int, str, str, int, list)
_member_types = (int, int, int)
_user_types = (int, int, time)
_tag_types = (str, str)


class Postgres:
    """
    A Postgres database controller, this is not meant to be accessed directly with
    the bot. For bot use, please use the DataManager class.
    """

    def __init__(self, conn: Connection):
        """
        Initialize the instance of this class.
        :param conn: the asyncpg connection.
        """
        self.__ready = False
        self.__conn: Connection = conn

        self.__get_guild: PreparedStatement = None
        self.__set_guild: PreparedStatement = None
        self.__get_member: PreparedStatement = None
        self.__set_member: PreparedStatement = None
        self.__get_user: PreparedStatement = None
        self.__set_user: PreparedStatement = None
        self.__get_tags: PreparedStatement = None
        self.__set_tags: PreparedStatement = None

    async def prepare(self, schema: str):
        """
        Prepare the queries that will be used.
        :param schema: the Postgres schema name.
        """
        f = self.__conn.prepare

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

        self.__set_tags = await f(
            'INSERT INTO {}.nsfw_tags VALUES ($1, $2) '
            'ON CONFLICT (site, tag_name) '
            'DO NOTHING'.format(schema)
        )
        self.__ready = True

    async def get_guild(self, guild_id: int) -> tuple:
        """
        Get guild row by id.
        :param guild_id: the guild id.
        :return: the guild row.
        """
        assert self.__ready
        res = (await self.__get_guild.fetchrow(guild_id) or
               (None,) * len(_guild_types))
        assert_types(res, _guild_types, True)
        return res

    async def set_guild(self, values: Sequence):
        """
        Set a guild row.
        :param values: the values of that row.
        """
        assert self.__ready
        assert_types(values, _guild_types, True)
        await self.__set_guild.fetch(*values)

    async def get_member(self, member_id: int, guild_id: int) -> tuple:
        """
        Get a member row.
        :param member_id: the member id.
        :param guild_id: the guild id.
        :return: the member row.
        """
        assert self.__ready
        res = (await self.__get_member.fetchrow(member_id, guild_id) or
               (None,) * len(_member_types))
        assert_types(res, _member_types, True)
        return res

    async def set_member(self, values: Sequence):
        """
        Set a member row.
        :param values: the values of that row.
        """
        assert self.__ready
        assert_types(values, _member_types, True)
        await self.__set_member.fetch(*values)


async def _get_guild_row(connection: Connection, guild_id: int):
    """
    Get the row with the guild_id from guild_info table.
    :param connection: the postgres connection
    :param guild_id: the guild id.
    :return: a tuple of the columns in that row.
    """
    s = 'testing'
    p = 'production'
    stmt = await connection.prepare(
        'SELECT * FROM {}.guild_info WHERE guild_id = $1'.format(p))
    res = await stmt.fetchrow(guild_id) or (None,) * len(_guild_types)
    assert_types(res, _guild_types, True)
    print(res)
    # await connection.execute('SELECT * FROM guild_info WHERE guild_id=?')
    # cursor.execute('SELECT * FROM guild_info WHERE guild=?', (guild_id,))
    # return cursor.fetchone() or (None,) * len(_guild_types)


def _write_guild_row(
        connection: Connection, cursor: Cursor, values: Sequence):
    """
    Write into the guild_info table
    :param connection: the sqlite3 connection object
    :param cursor: the sqlite3 cursor object
    :param values: the values of that row
    """
    cursor.execute('REPLACE INTO guild_info VALUES (?, ?, ?, ?, ?)', values)
    connection.commit()


def _get_member_row(cursor: Cursor, member_id: int, guild_id: int) -> tuple:
    """
    Get the row with member_id and guild_id from member_info table.
    :param cursor: the sqlite3 cursor object.
    :param member_id: the member id.
    :param guild_id: the guild id.
    :return: a tuple of the columns in that row
    """
    cursor.execute(
        'SELECT * FROM member_info WHERE member=? AND guild=?',
        (member_id, guild_id)
    )
    return cursor.fetchone() or (None,) * len(_member_types)


def _write_member_row(
        connection: Connection, cursor: Cursor, values: Sequence):
    """
    Write into the member_info table
    :param connection: the sqlite3 connection.
    :param cursor: the sqlite3 cursor.
    :param values: the values of that row
    """
    cursor.execute('REPLACE INTO member_info VALUES (?, ?, ?)', values)
    connection.commit()


def _get_user_row(cursor: Cursor, user_id: int) -> tuple:
    """
    Get a row in user_info by user_id.
    :param cursor: the sqlite3 cursor.
    :param user_id: the user id
    :return: the values of that row
    """
    cursor.execute('SELECT * FROM user_info WHERE user=?', (user_id,))
    return cursor.fetchone() or (None,) * len(_user_types)


def _write_user_row(connection: Connection, cursor: Cursor, values):
    """
    Write into user_info table.
    :param connection: the sqlite3 connection.
    :param cursor: the sqlite3 cursor.
    :param values: the values to that row.
    """
    cursor.execute('REPLACE INTO user_info VALUES (?, ?, ?)', values)
    connection.commit()


def _get_tags(cursor: Cursor) -> Dict[str, List[str]]:
    """
    Read the tags stored in the db into a dict mapping of {site: tags}
    :param cursor: the sqlite3 cursor.
    :return: A dict of tags, mapped as {site: tags}
    """
    cursor.execute('SELECT * FROM nsfw_tags')
    res = {}
    for t in cursor.fetchall():
        if len(t) == 2 and all(t):
            k, v = t
            if k in res:
                res[k].append(v)
            else:
                res[k] = [v]
    return res


def _write_tags(
        connection: Connection, cursor: Cursor, site: str, tags: List[str]):
    """
    Write a list of tags into the db based on the site
    :param connection: the sqlite3 connection.
    :param cursor: the sqlite3 cursor.
    :param site: the site name.
    :param tags: the list of tags.
    """
    for tag in tags:
        cursor.execute(
            'INSERT OR IGNORE INTO nsfw_tags VALUES (?, ?)', (site, tag))
    connection.commit()




if __name__ == '__main__':
    pass
    # from asyncio import get_event_loop
    #
    # loop = get_event_loop()
    # loop.run_until_complete(foo())
