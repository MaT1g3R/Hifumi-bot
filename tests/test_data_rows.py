from datetime import datetime
from random import randint
from string import printable
from time import time as now

import pytest

from data_controller.data_rows import *
from data_controller.postgres import Postgres
from scripts.helpers import random_word
from tests import *

pytestmark = pytest.mark.asyncio

__default_guild = ('1', '?', 'en', '0', ['foo', 'bar'])
__default_member = ('1', '1', 3)
__default_user = ('1', 100, datetime.now())


@pytest.fixture(scope='function')
async def guild_row():
    pool = await _get_pool()
    pos = Postgres(pool, SCHEMA, mock_logger())
    await pos.set_guild(__default_guild)
    d = await pos.get_guild('1')
    r0 = get_guild_row(pos, 0)
    r1 = get_guild_row(pos, 1, d)
    yield r0, r1, pos
    async with pool.acquire() as conn:
        await _clear_db(conn)


@pytest.fixture(scope='function')
async def member_row():
    pool = await _get_pool()
    pos = Postgres(pool, SCHEMA, mock_logger())
    await pos.set_member(__default_member)
    d = await pos.get_member('1', '1')
    r0 = get_member_row(pos, 0, 0)
    r1 = get_member_row(pos, 1, 1, d)
    yield r0, r1, pos
    async with pool.acquire() as conn:
        await _clear_db(conn)


@pytest.fixture(scope='function')
async def user_row():
    pool = await _get_pool()
    pos = Postgres(pool, SCHEMA, mock_logger())
    await pos.set_user(__default_user)
    d = await pos.get_user('1')
    r0 = get_user_row(pos, 0)
    r1 = get_user_row(pos, 1, d)
    yield r0, r1, pos
    async with pool.acquire() as conn:
        await _clear_db(conn)


async def test_guild_properties(guild_row):
    """
    Test properties in GuildRow
    """
    guild_row_empty, guild_row_default = guild_row[:-1]

    assert guild_row_empty.guild_id == 0
    assert guild_row_empty.prefix is None
    assert guild_row_empty.language is None
    assert guild_row_empty.mod_log is None
    assert guild_row_empty.roles is None

    assert guild_row_default.guild_id == int(__default_guild[0])
    assert guild_row_default.prefix == __default_guild[1]
    assert guild_row_default.language == __default_guild[2]
    assert guild_row_default.mod_log == int(__default_guild[3])
    assert guild_row_default.roles == __default_guild[4]


async def test_guild_setters(guild_row):
    """
    Test setters in GuildRow
    """
    guild_row_empty, guild_row_default, pos = guild_row

    async def ass(row, index, actual, expected):
        r = await pos.get_guild(str(row.guild_id))
        return r[index] == expected == actual

    prefix0 = random_word(randint(1, 5), printable)
    prefix1 = random_word(randint(1, 5), printable)
    await guild_row_empty.set_prefix(prefix0)
    assert await ass(guild_row_empty, 1, guild_row_empty.prefix, prefix0)
    await guild_row_default.set_prefix(prefix1)
    assert await ass(guild_row_default, 1, guild_row_default.prefix, prefix1)

    lan0 = random_word(randint(1, 10), printable)
    lan1 = random_word(randint(1, 10), printable)
    await guild_row_empty.set_language(lan0)
    assert await ass(guild_row_empty, 2, guild_row_empty.language, lan0)
    await guild_row_default.set_language(lan1)
    assert await ass(guild_row_default, 2, guild_row_default.language, lan1)

    mod0, mod1 = randint(0, 999999), randint(0, 999999)
    await guild_row_empty.set_mod_log(mod0)
    assert await ass(guild_row_empty, 3, str(guild_row_empty.mod_log),
                     str(mod0))
    await guild_row_default.set_mod_log(mod1)
    assert await ass(guild_row_default, 3, str(guild_row_default.mod_log),
                     str(mod1))

    roles0 = [random_word(randint(1, 10), printable) for _ in
              range(randint(0, 100))]
    roles1 = [random_word(randint(1, 10), printable) for _ in
              range(randint(0, 100))]
    await guild_row_empty.set_roles(roles0)
    assert await ass(guild_row_empty, 4, guild_row_empty.roles, roles0)
    await guild_row_default.set_roles(roles1)
    assert await ass(guild_row_default, 4, guild_row_default.roles, roles1)


async def test_member_properties(member_row):
    """
    Test properties in MemberRow
    """
    member_empty, member_default = member_row[:-1]

    assert member_empty.member_id == 0
    assert member_empty.guild_id == 0
    assert member_empty.warns is None

    assert member_default.member_id == int(__default_member[0])
    assert member_default.guild_id == int(__default_member[1])
    assert member_default.warns == __default_member[2]


async def test_member_setters(member_row):
    """
    Test setters in MemberRow
    """
    member_empty, member_default, pos = member_row
    warn0, warn1 = randint(0, 100), randint(0, 100)

    await member_empty.set_warns(warn0)

    r = await pos.get_member(
        str(member_empty.member_id), str(member_empty.guild_id))
    assert member_empty.warns == warn0 == r[2]

    await member_default.set_warns(warn1)
    r = await pos.get_member(
        str(member_default.member_id), str(member_default.guild_id))
    assert member_default.warns == warn1 == r[2]


async def test_user_properties(user_row):
    """
    Test properties in UserRow
    """
    user_empty, user_default = user_row[:-1]

    assert user_empty.user_id == 0
    assert user_empty.balance is None
    assert user_empty.daily is None

    assert user_default.user_id == int(__default_user[0])
    assert user_default.balance == __default_user[1]
    assert user_default.daily == __default_user[2]


async def test_user_setters(user_row):
    """
    Test setters in UserRow
    """
    user_empty, user_default, pos = user_row

    async def ass(row, index, expected, actual):
        r = await pos.get_user(str(row.user_id))
        return r[index] == expected == actual

    balance0, balance1 = randint(0, 10000), randint(0, 10000)

    await user_empty.set_balance(balance0)
    assert await ass(user_empty, 1, balance0, user_empty.balance)
    await user_default.set_balance(balance1)
    assert await ass(user_default, 1, balance1, user_default.balance)

    low, high = now() // 1.2, now() // 0.8
    day0, day1 = randint(low, high), randint(low, high)
    day0, day1 = datetime.fromtimestamp(day0), datetime.fromtimestamp(day1)

    await user_empty.set_daily(day0)
    assert await ass(user_empty, 2, day0, user_empty.daily)
    await user_default.set_daily(day1)
    assert await ass(user_default, 2, day1, user_default.daily)
