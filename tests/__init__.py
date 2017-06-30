from asyncpg import Connection, create_pool
from asyncpg.pool import Pool

from config import Config

__all__ = ['_clear_db', '_get_pool', 'SCHEMA', 'mock_logger']
__config = Config().postgres()
SCHEMA = __config['schema']['testing']


async def _clear_db(conn: Connection):
    """
    Helper function to delete all rows from all tables from the db
    :param conn: the Postgres connection.
    """
    tables = '''
    SELECT table_name
    FROM information_schema.tables
    WHERE table_schema=$1
    AND table_type='BASE TABLE'
    '''
    table_names = [
        list(v.values())[0] for v in
        [r for r in await conn.fetch(tables, SCHEMA)]
    ]
    for table in table_names:
        await conn.execute(f'TRUNCATE {SCHEMA}.{table}')


async def _get_pool() -> Pool:
    """
    Get a asyncpg Connection object
    :return: the Connection object
    """
    pool = await create_pool(
        host=__config['host'], port=__config['port'], user=__config['user'],
        database=__config['database'], password=__config['password']
    )
    async with pool.acquire() as conn:
        await _clear_db(conn)
    return pool


class mock_logger:
    def log(self, *args, **kwargs):
        print(args, kwargs)
