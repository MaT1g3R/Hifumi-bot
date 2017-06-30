from asyncio import coroutine
from datetime import datetime
from random import randint
from string import printable
from time import time as now

import pytest

from data_controller.data_manager import DataManager
from data_controller.postgres import Postgres
from scripts.helpers import random_word
from tests import *

pytestmark = pytest.mark.asyncio


@pytest.fixture(scope='function')
async def manager():
    pool = await _get_pool()
    pos = Postgres(pool, SCHEMA, mock_logger())
    yield DataManager(pos)
    async with pool.acquire() as conn:
        await _clear_db(conn)


async def __simple_test(
        getter: coroutine, setter: coroutine, ids: tuple, values: tuple):
    """
    Helper function the yield some simple test values for all the tests.
    :param getter: the DataManager getter function to be called.
    :param setter: the DataManager setter function to be called.
    :param ids: the ids of two rows.
    :param values: the values to set the property of the two rows to.
    """
    id0 = ids[0] if isinstance(ids[0], tuple) else (ids[0],)
    id1 = ids[1] if isinstance(ids[1], tuple) else (ids[1],)
    setter_args0 = [i for i in id0] + [values[0]]
    setter_args1 = [i for i in id1] + [values[1]]
    g0 = getter(*id0)
    g1 = getter(*id1)
    res0 = g0 is None
    res1 = g1 is None
    if not res0 or not res1:
        print('0')
        print(getter)
        print(g0)
        print(g1)
    yield res0
    yield res1

    await setter(*setter_args0)
    g0 = getter(*id0)
    g1 = getter(*id1)
    res0 = g0 == values[0]
    res1 = g1 != values[0]
    if not res0 or not res1:
        print('1')
        print(getter)
        print(g0)
        print(g1)
        print(values[0])
    yield res0
    yield res1

    await setter(*setter_args1)
    g0 = getter(*id0)
    g1 = getter(*id1)
    res0 = g1 == values[1]
    res1 = g0 != values[1]
    if not res0 or not res1:
        print('2')
        print(getter)
        print(g0)
        print(g1)
        print(values[1])
    yield res0
    yield res1


def __unique_ints(i0=None, i1=None) -> tuple:
    """
    Generate 2 unique random ints.
    :param i0: the first int.
    :param i1: the second int.
    :return: two unique random ints.
    """
    if i0 is None and i1 is None:
        i0, i1 = randint(0, 99999), randint(0, 99999)
    if i0 == i1:
        return __unique_ints()
    return i0, i1


def __unique_strs(s0=None, s1=None) -> tuple:
    """
    Generate 2 unique random strs.
    :param s0: the first str.
    :param s1: the second str.
    :return: two unique random strs.
    """
    if s0 is None and s1 is None:
        s0, s1 = random_word(randint(1, 7), printable), \
                 random_word(randint(1, 7), printable)
    if s0 == s1:
        return __unique_strs()
    return s0, s1


async def test_prefix(manager):
    """
    Test getting and setting prefix
    """
    async for test in __simple_test(
            manager.get_prefix,
            manager.set_prefix,
            __unique_ints(),
            __unique_strs()
    ):
        assert test


async def test_language(manager):
    """
    Test getting and setting language
    """
    async for test in __simple_test(
            manager.get_language,
            manager.set_language,
            __unique_ints(),
            __unique_strs()
    ):
        assert test


async def test_mod_log(manager):
    """
    Test getting and setting mod_log
    """
    async for test in __simple_test(
            manager.get_mod_log,
            manager.set_mod_log,
            __unique_ints(),
            __unique_ints()
    ):
        assert test


async def test_roles(manager):
    """
    Test getting and setting roles
    """
    roles0 = []
    roles1 = []
    id0, id1 = __unique_ints()
    for _ in range(randint(0, 100)):
        s0, s1 = __unique_strs()
        if s0 not in roles0:
            roles0.append(s0)
        if s1 not in roles1:
            roles1.append(s1)

    async for test in __simple_test(
            manager.get_roles,
            manager.set_roles,
            (id0, id1),
            (roles0, roles1)
    ):
        assert test
    bad_role = ['foo', 1]
    try:
        await manager.set_roles(id0, bad_role)
    except AssertionError:
        pass
    else:
        assert False
    finally:
        assert manager.get_roles(id0) == roles0


async def test_warns(manager):
    """
    Test getting and setting warns
    """
    member_ids = __unique_ints()
    guild_ids = __unique_ints()
    warns = __unique_ints()
    async for test in __simple_test(
            manager.get_member_warns,
            manager.set_member_warns,
            ((member_ids[0], guild_ids[0]), (member_ids[1], guild_ids[1])),
            warns
    ):
        assert test

    try:
        await manager.set_member_warns(member_ids[0], guild_ids[0], -1)
    except AssertionError:
        pass
    else:
        assert False
    finally:
        assert warns[0] == manager.get_member_warns(
            member_ids[0], guild_ids[0])


async def test_balance(manager):
    """
    Test getting and setting balance
    """
    user_ids = __unique_ints()
    balance = __unique_ints()
    async for test in __simple_test(
            manager.get_user_balance,
            manager.set_user_balance,
            (user_ids[0], user_ids[1]),
            (balance[0], balance[1])
    ):
        assert test
    try:
        await manager.set_user_balance(user_ids[0], -1)
    except AssertionError:
        pass
    else:
        assert False
    finally:
        assert balance[0] == manager.get_user_balance(user_ids[0])


async def test_daily(manager):
    """
    Test getting and setting daily
    """
    low, high = now() // 1.2, now() // 0.8
    day0, day1 = randint(low, high), randint(low, high)
    day0, day1 = datetime.fromtimestamp(day0), datetime.fromtimestamp(day1)
    async for test in __simple_test(
            manager.get_user_daily,
            manager.set_user_daily,
            __unique_ints(),
            (day0, day1)
    ):
        assert test
