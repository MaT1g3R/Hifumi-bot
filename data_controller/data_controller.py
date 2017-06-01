"""
A sqlite3 database controller, this is not meant to be accessed directly with
the bot. For bot use, please use the DataManager class.
"""
from sqlite3 import Cursor, Connection
from time import time

from data_controller.data_manager import TransferError


def _get_guild_row(cursor: Cursor, guild_id: int) -> tuple:
    """
    Get the row with the guild_id from guild_info table.
    :param cursor: the sqlite3 cursor object.
    :param guild_id: the guild id.
    :return: a tuple of the columns in that row.
    """
    cursor.execute('SELECT * FROM guild_info WHERE guild=?', (guild_id,))
    return cursor.fetchone() or (None,) * 5


def _write_guild_row(cursor: Cursor, connection: Connection, *args):
    """
    Write into the guild_info table
    :param cursor: the sqlite3 cursor object
    :param connection: the sqlite3 connection object
    :param args: the values of that row
    """
    assert len(args) == 5
    cursor.execute('REPLACE INTO guild_info VALUES (?, ?, ?, ?, ?)', args)
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
    return cursor.fetchone() or (None,) * 3


def _write_member_row(cursor: Cursor, connection: Connection, *args):
    """
    Write into the member_info table
    :param cursor: the sqlite3 cursor.
    :param connection: the sqlite3 connection.
    :param args: the values of that row
    """
    assert len(args) == 3
    cursor.execute('REPLACE INTO member_info VALUES (?, ?, ?)', args)
    connection.commit()


def write_tag_(connection, cursor, site, tag):
    """
    Write a tag entry into the database
    :param connection: the sqlite db connection
    :param cursor: the database cursor
    :param site: the site name
    :param tag: the tag entry
    """
    sql_replace = '''REPLACE INTO nsfw_tags VALUES (?, ?)'''
    cursor.execute(sql_replace, (site, tag))
    connection.commit()


def write_tag_list_(connection, cursor, site, tags):
    """
    Writes a list of tags into the db
    :param connection: the sqlite db connection
    :param cursor: the database cursor
    :param site: the site name
    :param tags: the list of tags
    """
    for tag in tags:
        write_tag_(connection, cursor, site, tag)


def tag_in_db_(cursor, site, tag):
    """
    Returns if the tag is in the db or not
    :param cursor: the database cursor
    :param site: the site name
    :param tag: the tag name
    :return: True if the tag is in the db else false
    """
    sql = '''
    SELECT EXISTS(SELECT 1 FROM nsfw_tags WHERE site=? AND tag=?LIMIT 1)
    '''
    cursor.execute(sql, (site, tag))
    return cursor.fetchone() == (1,)


def fuzzy_match_tag_(cursor, site, tag):
    """
    Try to fuzzy match a tag with one in the db
    :param cursor: the database cursor
    :param site: the stie name
    :param tag: the tag name
    :return: a tag in the db if match success else None
    """
    sql = """
    SELECT tag FROM nsfw_tags 
    WHERE (tag LIKE '{0}%' OR tag LIKE '%{0}%' OR tag LIKE '%{0}') 
    AND site=?
    """.format(tag)
    res = cursor.execute(sql, (site,)).fetchone()
    return res[0] if res is not None else None


def get_balance_(cursor, user_id: str):
    """
    Get the balance of a user
    :param cursor: the db cursor
    :param user_id: the user id
    :return: the balance of the user
    """
    sql = '''
    SELECT balance FROM currency WHERE user = ?
    '''
    cursor.execute(sql, (user_id,))
    res = cursor.fetchone()
    return res[0] if res is not None else 0


def change_balance_(connection, cursor, user_id: str, delta: int):
    """
    Set the balance of a user
    :param connection: the db connection
    :param cursor: the db cursor
    :param user_id: the user id
    :param delta: how much to change the balance by
    """
    sql_insert = '''
    INSERT OR IGNORE INTO currency VALUES (?, 0, NULL)
    '''
    sql_change = '''
    UPDATE currency SET balance = balance + ? WHERE user = ?
    '''
    cursor.execute(sql_insert, (user_id,))
    cursor.execute(sql_change, (delta, user_id))
    connection.commit()


def transfer_balance_(connection, cursor, root_id, target_id, amount: int,
                      check_balance=True):
    """
    Transfer x amout of money from root to target
    :param connection: the db connection
    :param cursor: the db cursor
    :param root_id: the root user id
    :param target_id: the target user id
    :param amount: the amout of transfer
    :param check_balance: True to check if the root has enough balance
    :raises: TransferError if the root doesnt have enough money
    """
    sql_insert = '''
    INSERT OR IGNORE INTO currency VALUES (?, 0, NULL)
    '''
    sql_change = '''
    UPDATE currency SET balance = balance + ? WHERE user = ?
    '''
    root_balance = get_balance_(cursor, root_id)
    if root_balance < amount and check_balance:
        raise TransferError(str(root_balance))
    cursor.execute(sql_insert, (target_id,))
    cursor.execute(sql_change, (-amount, root_id))
    cursor.execute(sql_change, (amount, target_id))
    connection.commit()


def get_daily_(cursor, user_id: str):
    """
    Get the daily time stamp of a user
    :param cursor: the db cursor
    :param user_id: the user id
    :return: the daily timestamp of a user
    """
    sql = '''
    SELECT daily FROM currency WHERE user = ?
    '''
    cursor.execute(sql, (user_id,))
    res = cursor.fetchone()
    return res[0] if res is not None else None


def set_daily_(connection, cursor, user_id: str):
    """
    Set the daily time stamp for a user
    :param connection: the db connection
    :param cursor: the db cursor
    :param user_id: the user id
    """
    sql_insert = '''
    INSERT OR IGNORE INTO currency VALUES (?, 0, NULL)
    '''
    sql_update = '''
    UPDATE currency SET daily = ? WHERE user = ?
    '''
    cursor.execute(sql_insert, (user_id,))
    cursor.execute(sql_update, (int(time()), user_id))
    connection.commit()
