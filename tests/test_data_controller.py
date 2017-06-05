from random import randint
from sqlite3 import connect
from string import printable

from pytest import fixture

from data_controller.data_controller import *
from scripts.helpers import random_word
from tests import *


@fixture(scope='module')
def get_sql_obj():
    conn = connect(_db_path)
    cur = conn.cursor()
    yield conn, cur
    _clear_db(conn, cur)


def test_guild_row(get_sql_obj):
    """
    Test _get_guild_row, _write_guild_row
    """
    conn, cur = get_sql_obj
    guild_id = 1
    vals = (guild_id, '?', 'en', 2, '[3,5,7]')
    wrong_vals = (guild_id, '?', 'en', '2', '[3,5,7]')
    none_vals = (guild_id, None, None, None, None)

    assert not any(_get_guild_row(cur, guild_id))

    try:
        _write_guild_row(conn, cur, none_vals)
        assert _get_guild_row(cur, guild_id) == none_vals
    except Exception as e:
        print(e)
        assert False

    _write_guild_row(conn, cur, vals)
    assert _get_guild_row(cur, guild_id) == vals

    try:
        _write_guild_row(conn, cur, wrong_vals)
    except AssertionError:
        pass
    else:
        assert False
    finally:
        assert _get_guild_row(cur, guild_id) == vals

    assert not any(_get_guild_row(cur, 100))


def test_member_row(get_sql_obj):
    """
    Test _get_member_row, _write_member_row
    """
    conn, cur = get_sql_obj
    member_id, guild_id = 1, 1
    wrong_member, wrong_guild = 2, 2
    warns = 3
    expected = (member_id, guild_id, warns)

    assert not any(_get_member_row(cur, member_id, guild_id))

    _write_member_row(conn, cur, (member_id, guild_id, None))
    assert _get_member_row(
        cur, member_id, guild_id) == (member_id, guild_id, None)

    _write_member_row(conn, cur, expected)
    assert _get_member_row(cur, member_id, guild_id) == expected

    try:
        _write_member_row(conn, cur, (member_id, guild_id, '3'))
    except AssertionError:
        pass
    else:
        assert False
    finally:
        assert _get_member_row(cur, member_id, guild_id) == expected

    assert not any(_get_member_row(cur, member_id, wrong_guild))
    assert not any(_get_member_row(cur, wrong_member, guild_id))


def test_user_row(get_sql_obj):
    """
    Test _get_user_row, _write_user_row
    """
    conn, cur = get_sql_obj
    user_id = 1
    balance = 100
    daily = 1496627784
    expected = (user_id, balance, daily)

    assert not any(_get_user_row(cur, user_id))

    _write_user_row(conn, cur, (user_id, None, None))
    assert _get_user_row(cur, user_id) == (user_id, None, None)

    _write_user_row(conn, cur, expected)
    assert _get_user_row(cur, user_id) == expected

    try:
        _write_user_row(conn, cur, (user_id, balance, daily + 0.1))
    except AssertionError:
        pass
    else:
        assert False
    finally:
        assert _get_user_row(cur, user_id) == expected

    assert not any(_get_user_row(cur, user_id + 1))


def test_tags(get_sql_obj):
    """
    Test _get_tags, _write_tags
    """
    conn, cur = get_sql_obj
    expected = {}
    for _ in range(randint(3, 7)):
        site = random_word(randint(4, 8), printable)
        tags = [
            random_word(randint(3, 15), printable)
            for _ in range(randint(100, 300))
        ]
        if site not in expected:
            expected[site] = list(set(tags))
        else:
            expected[site] = list(set(expected[site] + tags))

    assert not any(_get_tags(cur))

    for site, tags in expected.items():
        _write_tags(conn, cur, site, tags)
    assert _get_tags(cur) == expected
