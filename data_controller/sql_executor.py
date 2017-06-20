"""
A sqlite3 database controller, this is not meant to be accessed directly with
the bot. For bot use, please use the DataManager class.
"""
from sqlite3 import Connection, Cursor
from typing import Dict, List, Sequence

from scripts.helpers import assert_inputs, assert_outputs

# Types expected for the different tables
__guild_types = (int, str, str, int, str)
__member_types = (int, int, int)
__user_types = (int, int, int)
__tag_types = (str, str)

__all__ = ['_get_guild_row', '_get_member_row', '_get_tags', '_get_user_row',
           '_write_guild_row', '_write_member_row', '_write_tags',
           '_write_user_row']


@assert_outputs(__guild_types, True)
def _get_guild_row(cursor: Cursor, guild_id: int) -> tuple:
    """
    Get the row with the guild_id from guild_info table.
    :param cursor: the sqlite3 cursor object.
    :param guild_id: the guild id.
    :return: a tuple of the columns in that row.
    """
    cursor.execute('SELECT * FROM guild_info WHERE guild=?', (guild_id,))
    return cursor.fetchone() or (None,) * len(__guild_types)


@assert_inputs(__guild_types, True)
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


@assert_outputs(__member_types, True)
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
    return cursor.fetchone() or (None,) * len(__member_types)


@assert_inputs(__member_types, True)
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


@assert_outputs(__user_types, True)
def _get_user_row(cursor: Cursor, user_id: int) -> tuple:
    """
    Get a row in user_info by user_id.
    :param cursor: the sqlite3 cursor.
    :param user_id: the user id
    :return: the values of that row
    """
    cursor.execute('SELECT * FROM user_info WHERE user=?', (user_id,))
    return cursor.fetchone() or (None,) * len(__user_types)


@assert_inputs(__user_types, True)
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
