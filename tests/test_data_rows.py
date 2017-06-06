from random import randint
from sqlite3 import connect
from string import printable
from time import time

from pytest import fixture

from data_controller.data_controller import _get_guild_row, _get_member_row, \
    _get_user_row, _write_guild_row, _write_member_row, _write_user_row
from data_controller.data_rows import *
from scripts.helpers import random_word
from tests import *

__default_guild = (1, '?', 'en', 0, repr(['foo', 'bar']))
__default_member = (1, 1, 3)
__default_user = (1, 100, 1496646243)


@fixture(scope='function')
def guild_row():
    conn = connect(_db_path)
    cur = conn.cursor()
    _write_guild_row(conn, cur, __default_guild)
    yield GuildRow(conn, cur, 0), GuildRow(conn, cur, 1), cur
    _clear_db(conn, cur)


@fixture(scope='function')
def member_row():
    conn = connect(_db_path)
    cur = conn.cursor()
    _write_member_row(conn, cur, __default_member)
    yield MemberRow(conn, cur, 0, 0), MemberRow(conn, cur, 1, 1), cur
    _clear_db(conn, cur)


@fixture(scope='function')
def user_row():
    conn = connect(_db_path)
    cur = conn.cursor()
    _write_user_row(conn, cur, __default_user)
    yield UserRow(conn, cur, 0), UserRow(conn, cur, 1), cur
    _clear_db(conn, cur)


def test_guild_properties(guild_row):
    """
    Test properties in GuildRow
    """
    guild_row_empty, guild_row_default = guild_row[:-1]

    assert guild_row_empty.guild_id == 0
    assert guild_row_empty.prefix is None
    assert guild_row_empty.language is None
    assert guild_row_empty.mod_log is None
    assert guild_row_empty.roles is None

    assert guild_row_default.guild_id == __default_guild[0]
    assert guild_row_default.prefix == __default_guild[1]
    assert guild_row_default.language == __default_guild[2]
    assert guild_row_default.mod_log == __default_guild[3]
    assert guild_row_default.roles == __default_guild[4]


def test_guild_setters(guild_row):
    """
    Test setters in GuildRow
    """

    guild_row_empty, guild_row_default, cur = guild_row

    def ass(row, index, actual, expected):
        return _get_guild_row(cur, row.guild_id)[index] == expected == actual

    prefix0 = random_word(randint(1, 5), printable)
    prefix1 = random_word(randint(1, 5), printable)
    guild_row_empty.prefix = prefix0
    assert ass(guild_row_empty, 1, guild_row_empty.prefix, prefix0)
    guild_row_default.prefix = prefix1
    assert ass(guild_row_default, 1, guild_row_default.prefix, prefix1)

    lan0 = random_word(randint(1, 10), printable)
    lan1 = random_word(randint(1, 10), printable)
    guild_row_empty.language = lan0
    assert ass(guild_row_empty, 2, guild_row_empty.language, lan0)
    guild_row_default.language = lan1
    assert ass(guild_row_default, 2, guild_row_default.language, lan1)

    mod0, mod1 = randint(0, 999999), randint(0, 999999)
    guild_row_empty.mod_log = mod0
    assert ass(guild_row_empty, 3, guild_row_empty.mod_log, mod0)
    guild_row_default.mod_log = mod1
    assert ass(guild_row_default, 3, guild_row_default.mod_log, mod1)

    roles0 = [random_word(randint(1, 10), printable) for _ in
              range(randint(0, 100))]
    roles1 = [random_word(randint(1, 10), printable) for _ in
              range(randint(0, 100))]
    guild_row_empty.roles = repr(roles0)
    assert ass(guild_row_empty, 4, guild_row_empty.roles, repr(roles0))
    guild_row_default.roles = repr(roles1)
    assert ass(guild_row_default, 4, guild_row_default.roles, repr(roles1))


def test_member_properties(member_row):
    """
    Test properties in MemberRow
    """
    member_empty, member_default = member_row[:-1]

    assert member_empty.member_id == 0
    assert member_empty.guild_id == 0
    assert member_empty.warns is None

    assert member_default.member_id == __default_member[0]
    assert member_default.guild_id == __default_member[1]
    assert member_default.warns == __default_member[2]


def test_member_setters(member_row):
    """
    Test setters in MemberRow
    """
    member_empty, member_default, cur = member_row
    warn0, warn1 = randint(0, 100), randint(0, 100)

    member_empty.warns = warn0
    assert member_empty.warns == warn0 == _get_member_row(
        cur, member_empty.member_id, member_empty.guild_id)[2]

    member_default.warns = warn1
    assert member_default.warns == warn1 == _get_member_row(
        cur, member_default.member_id, member_default.guild_id)[2]


def test_user_properties(user_row):
    """
    Test properties in UserRow
    """
    user_empty, user_default = user_row[:-1]

    assert user_empty.user_id == 0
    assert user_empty.balance is None
    assert user_empty.daily is None

    assert user_default.user_id == __default_user[0]
    assert user_default.balance == __default_user[1]
    assert user_default.daily == __default_user[2]


def test_user_setters(user_row):
    """
    Test setters in UserRow
    """
    user_empty, user_default, cur = user_row

    def ass(row, index, expected, actual):
        return _get_user_row(cur, row.user_id)[index] == expected == actual

    balance0, balance1 = randint(0, 10000), randint(0, 10000)
    user_empty.balance = balance0
    assert ass(user_empty, 1, balance0, user_empty.balance)
    user_default.balance = balance1
    assert ass(user_default, 1, balance1, user_default.balance)

    low, high = time() // 1.2, time() // 0.8
    day0, day1 = randint(low, high), randint(low, high)
    user_empty.daily = day0
    assert ass(user_empty, 2, day0, user_empty.daily)
    user_default.daily = day1
    assert ass(user_default, 2, day1, user_default.daily)
