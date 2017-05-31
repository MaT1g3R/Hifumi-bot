"""
A sqlite3 database handler
"""
from time import time


class TransferError(ValueError):
    pass


def get_prefix_(cursor, server_id: str):
    """
    Get the server prefix from databse
    :param cursor: the database cursor
    :param server_id: the server id
    :return: the server prefix if found else none
    """
    sql = '''SELECT prefix FROM prefix_old WHERE server=?'''
    res = cursor.execute(sql, (server_id,)).fetchone()
    return res[0] if res is not None else None


def set_prefix_(connection, cursor, server_id: str, prefix: str):
    """
    Set the prefix for a server
    :param connection: the sqlite db connection
    :param cursor: the database cursor
    :param server_id: the server id
    :param prefix: the command prefix
    """
    sql_replace = '''REPLACE INTO prefix VALUES (?, ?)'''
    cursor.execute(sql_replace, (server_id, prefix))
    connection.commit()


def delete_prefix_(connection, cursor, server_id: str):
    """
    Delete the prefix for a server
    :param connection: the db connection
    :param cursor: the db cursor
    :param server_id: the server id
    """
    sql_delete = '''
    DELETE FROM prefix_old WHERE server=?
    '''
    cursor.execute(sql_delete, (server_id,))
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


def get_language_(cursor, server_id: str):
    """
    Get the server language from databse
    :param cursor: the database cursor
    :param server_id: the server id
    :return: the server language if found else none
    """
    sql = '''SELECT lan FROM language_old WHERE server=?'''
    res = cursor.execute(sql, (server_id,)).fetchone()
    return res[0] if res is not None else None


def set_language_(connection, cursor, server_id: str, language: str):
    """
    Set the language for a server
    :param connection: the sqlite db connection
    :param cursor: the database cursor
    :param server_id: the server id
    :param language: the language
    """
    sql_replace = '''REPLACE INTO language VALUES (?, ?)'''
    cursor.execute(sql_replace, (server_id, language))
    connection.commit()


def delete_language_(connection, cursor, server_id: str):
    """
    Delete the language info for a server
    :param connection: the db connection
    :param cursor: the db cursor
    :param server_id: the server id
    """
    sql_delete = '''
    DELETE FROM language_old WHERE server=?
    '''
    cursor.execute(sql_delete, (server_id,))
    connection.commit()


def add_role_(connection, cursor, server_id: str, role: str):
    """
    Add a role to the db
    :param connection: the sqlite db connection
    :param cursor: the database cursor
    :param server_id: the server id
    :param role: the role name
    """
    sql_replace = '''REPLACE INTO roles VALUES (?, ?)'''
    cursor.execute(sql_replace, (server_id, role))
    connection.commit()


def remove_role_(connection, cursor, server_id: str, role: str):
    """
    Remove a role from the db
    :param connection: the sqlite db connection
    :param cursor: the database cursor
    :param server_id: the server id 
    :param role: the role name
    """
    sql = '''
    DELETE FROM roles WHERE server=? AND role=?
    '''
    cursor.execute(sql, (server_id, role))
    connection.commit()


def get_role_list_(cursor, server_id: str):
    """
    Get the list of roles under the server with id == server_id
    :param cursor: the database cursor
    :param server_id: the server 
    :return: a list of roles under the server with id == server_id
    """
    sql = '''
    SELECT role FROM roles WHERE server=?
    '''
    cursor.execute(sql, (server_id,))
    return [i[0] for i in cursor.fetchall()]


def set_mod_log_(connection, cursor, server_id: str, channel_id: str):
    """
    Set the mod log channel id for a given server
    :param connection: the sqlite db connection
    :param cursor: the database cursor
    :param server_id: the server id
    :param channel_id: the channel id
    """
    sql_replace = '''REPLACE INTO mod_log VALUES (?, ?)'''
    cursor.execute(sql_replace, (server_id, channel_id))
    connection.commit()


def get_mod_log_(cursor, server_id: str):
    """
    Get a list of all mod logs from a given server
    :param cursor: the database cursor
    :param server_id: the server id
    :return: a list of all mod log channel ids
    """

    sql = '''
    SELECT channel FROM mod_log WHERE server=?
    '''
    cursor.execute(sql, (server_id,))
    return [i[0] for i in cursor.fetchall()]


def remove_mod_log_(connection, cursor, server_id: str, channel_id: str):
    """
    Delete a modlog from the db
    :param connection: the sqlite db connection
    :param cursor: the database cursor
    :param server_id: the server id
    :param channel_id: the channel id
    """
    sql = '''
    DELETE FROM mod_log WHERE server=? AND channel=?
    '''
    cursor.execute(sql, (server_id, channel_id))
    connection.commit()


def add_warn_(connection, cursor, server_id: str, user_id: str):
    """
    Add 1 to the warning count of the user
    :param connection: the sqlite db connection
    :param cursor: the database cursor
    :param server_id: the server id
    :param user_id: the user id
    """
    sql_insert = '''INSERT OR IGNORE INTO warns VALUES(?,?,0)'''
    sql = '''
    UPDATE warns SET number = number + 1 WHERE server = ? AND user = ?
    '''
    cursor.execute(sql_insert, (server_id, user_id))
    cursor.execute(sql, [server_id, user_id])
    connection.commit()


def remove_warn_(connection, cursor, server_id: str, user_id: str):
    """
    Subtract 1 from the warning count of the user
    :param connection: the sqlite db connection
    :param cursor: the database cursor
    :param server_id: the server id
    :param user_id: the user id
    """
    sql = '''
    UPDATE warns SET number = number - 1 
    WHERE server = ? AND user = ? AND number > 0
    '''
    cursor.execute(sql, (server_id, user_id))
    connection.commit()


def get_warn_(cursor, server_id: str, user_id: str):
    """
    Get the warning count of a user
    :param cursor: the database cursor
    :param server_id: the server id
    :param user_id: the user id
    :return: the warning count of the user
    """
    sql = '''
    SELECT number FROM warns WHERE server = ? AND user = ?
    '''
    cursor.execute(sql, (server_id, user_id))
    result = cursor.fetchone()
    return result[0] if result is not None else 0


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
