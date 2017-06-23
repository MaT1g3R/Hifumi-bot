from datetime import datetime
from random import randint
from string import printable

import pytest

from data_controller.postgres import get_postgres
from scripts.helpers import random_word
from tests import *

pytestmark = pytest.mark.asyncio


@pytest.fixture(scope='function')
async def postgres():
    conn = await _get_connection()
    pos = await get_postgres(conn, schema())
    yield pos
    await _clear_db(conn)


async def test_guild_row(postgres):
    """
    Test _get_guild_row, _write_guild_row
    """
    guild_id = 1
    vals = (guild_id, '?', 'en', 2, ['3', '5', '7'])
    wrong_vals = (guild_id, '?', 'en', '2', '[3,5,7]')
    none_vals = (guild_id, None, None, None, None)

    assert not any(await postgres.get_guild(guild_id))

    try:
        await postgres.set_guild(none_vals)
        assert await postgres.get_guild(guild_id) == none_vals
    except Exception as e:
        print(e)
        assert False

    await postgres.set_guild(vals)
    assert await postgres.get_guild(guild_id) == vals

    try:
        await postgres.set_guild(wrong_vals)
    except AssertionError:
        pass
    else:
        assert False
    finally:
        assert await postgres.get_guild(guild_id) == vals

    assert not any(await postgres.get_guild(100))


async def test_member_row(postgres):
    """
    Test _get_member_row, _write_member_row
    """
    member_id, guild_id = 1, 1
    wrong_member, wrong_guild = 2, 2
    warns = 3
    none_warn = (member_id, guild_id, None)
    expected = (member_id, guild_id, warns)

    assert not any(await postgres.get_member(member_id, guild_id))

    await postgres.set_member(none_warn)
    assert await postgres.get_member(member_id, guild_id) == none_warn

    await postgres.set_member(expected)

    assert await postgres.get_member(member_id, guild_id) == expected

    try:
        await postgres.set_member((member_id, guild_id, '3'))
    except AssertionError:
        pass
    else:
        assert False
    finally:
        assert await postgres.get_member(member_id, guild_id) == expected

    assert not any(await postgres.get_member(member_id, wrong_guild))
    assert not any(await postgres.get_member(wrong_member, guild_id))


async def test_user_row(postgres):
    """
    Test _get_user_row, _write_user_row
    """
    user_id = 1
    balance = 100
    daily = datetime.now()
    none_val = (user_id, 0, None)
    expected = (user_id, balance, daily)

    assert not any(await postgres.get_user(user_id))

    await postgres.set_user(none_val)
    assert await postgres.get_user(user_id) == none_val

    await postgres.set_user(expected)
    assert await postgres.get_user(user_id) == expected

    try:
        await postgres.set_user((user_id, balance, str(daily)))
    except AssertionError:
        pass
    else:
        assert False
    finally:

        assert await postgres.get_user(user_id) == expected
    assert not any(await postgres.get_user(user_id + 1))


async def test_tags(postgres):
    """
    Test _get_tags, _write_tags
    """
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

    assert not any(await postgres.get_tags())

    for site, tags in expected.items():
        await postgres.set_tags(site, tags)

    assert await postgres.get_tags() == expected
