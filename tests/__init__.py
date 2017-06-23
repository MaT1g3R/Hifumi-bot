from asyncpg import Connection, connect

__all__ = ['_clear_db', '_get_connection', 'schema']


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
        [r for r in await conn.fetch(tables, schema())]
    ]
    for table in table_names:
        await conn.execute(f'TRUNCATE {schema()}.{table}')


async def _get_connection() -> Connection:
    """
    Get a asyncpg Connection object
    :return: the Connection object
    """
    kwagrs = __get_kwargs()
    conn = await connect(**kwagrs)
    return conn


def __get_kwargs(*args, **kwargs) -> dict:
    """
    Get the kwargs to connect to the db.
    """
    # TODO Finish this
    raise NotImplementedError


def schema():
    # TODO Finish this
    raise NotImplementedError
