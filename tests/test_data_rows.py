from sqlite3 import connect

from pytest import fixture

from data_controller.data_controller import _write_guild_row, \
    _write_member_row, _write_user_row
from data_controller.data_rows import *
from tests import *

__default_guild = (1, '?', 'en', 0, repr([0, 1]))
__default_member = (1, 1, 3)
__default_user = (1, 100, 1496646243)


@fixture(scope='function')
def guild_row():
    conn = connect(_db_path)
    cur = conn.cursor()
    _write_guild_row(conn, cur, __default_guild)
    yield GuildRow(conn, cur, 0), GuildRow(conn, cur, 1)
    _clear_db(conn, cur)


@fixture(scope='function')
def member_row():
    conn = connect(_db_path)
    cur = conn.cursor()
    _write_member_row(conn, cur, __default_member)
    yield MemberRow(conn, cur, 0, 0), MemberRow(conn, cur, 1, 1)
    _clear_db(conn, cur)


@fixture(scope='function')
def user_row():
    conn = connect(_db_path)
    cur = conn.cursor()
    _write_user_row(conn, cur, __default_user)
    yield UserRow(conn, cur, 0), UserRow(conn, cur, 1)
    _clear_db(conn, cur)


def test_guild_getters(guild_row):
    guild_row_empty, guild_row_default = guild_row
    assert guild_row_empty.guild_id == 0
    assert guild_row_empty.prefix is None
    assert guild_row_empty.language is None
    assert guild_row_empty.mod_log is None
    assert guild_row_empty.roles is None
