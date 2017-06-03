"""
A sqlite3 database controller, this is not meant to be accessed directly with
the bot. For bot use, please use the DataManager class.
"""
from sqlite3 import Connection, Cursor
from typing import Sequence

from scripts.helpers import assert_inputs, assert_outputs

# Types expected for the different tables
__guild_types = (int, str, str, int, str)
__member_types = (int, int, int)
__user_types = (int, int, int)


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
