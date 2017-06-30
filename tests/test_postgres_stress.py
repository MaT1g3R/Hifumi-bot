from random import randint
from string import printable

import pytest

from data_controller.postgres import Postgres
from scripts.helpers import random_word
from tests import *

pytestmark = pytest.mark.asyncio


@pytest.fixture(scope='function')
async def postgres():
    pool = await _get_pool()
    pos = Postgres(pool, SCHEMA, mock_logger())
    yield pos
    async with pool.acquire() as conn:
        await _clear_db(conn)


def rand_str():
    source = printable
    num = randint(1, 10)
    return random_word(num, source)


def rand_lst():
    num = randint(0, 20)
    return [rand_str() for _ in range(num)]


async def test_guild(postgres):
    attempts = 1000
    guild_ids = [str(i) for i in range(attempts)]
    for i in guild_ids:
        assert await postgres.get_guild(i) == (None,) * 5
        expected = (i, rand_str(), rand_str(), rand_str(), rand_lst())
        await postgres.set_guild(expected)
        res = await postgres.get_guild(i)
        assert res == expected
