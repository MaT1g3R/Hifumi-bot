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
    pos = await get_postgres(conn, SCHEMA, mock_logger())
    yield pos
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
