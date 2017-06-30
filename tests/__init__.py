from asyncpg import Connection, InvalidCatalogNameError, create_pool
from asyncpg.pool import Pool

from scripts.helpers import shell_command

__all__ = ['_clear_db', '_get_pool', 'SCHEMA', 'mock_logger']
SCHEMA = 'testing'


async def _make_tables(pool: Pool):
    sql = ('''
        CREATE TABLE IF NOT EXISTS testing.guild_info
    (
        guild_id VARCHAR NOT NULL
            CONSTRAINT guild_info_pkey
                PRIMARY KEY,
        prefix VARCHAR,
        lan VARCHAR,
        mod_log VARCHAR,
        roles VARCHAR[]
    )
    ;
    
    CREATE TABLE IF NOT EXISTS testing.member_info
    (
        member_id VARCHAR NOT NULL,
        guild_id VARCHAR NOT NULL,
        warns INTEGER DEFAULT 0
            CONSTRAINT positive_warn
                CHECK (warns >= 0),
        CONSTRAINT member_info_member_id_guild_id_key
            UNIQUE (member_id, guild_id)
    )
    ;
    
    CREATE TABLE IF NOT EXISTS testing.nsfw_tags
    (
        site VARCHAR NOT NULL,
        tag_name VARCHAR NOT NULL,
        CONSTRAINT nsfw_tags_site_tag_name_key
            UNIQUE (site, tag_name)
    )
    ;
    
    CREATE TABLE IF NOT EXISTS testing.user_info
    (
        user_id VARCHAR NOT NULL
            CONSTRAINT user_info_pkey
                PRIMARY KEY,
        balance BIGINT,
        daily TIMESTAMP
    )
    ;
    ''')
    schema_exist = await pool.fetchval(
        """
        SELECT exists(
        SELECT schema_name FROM information_schema.schemata 
        WHERE schema_name = 'testing'
        );
        """
    )
    if not schema_exist:
        await pool.execute('CREATE SCHEMA testing;')
    await pool.execute(sql)


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
    try:
        pool = await create_pool(database='hifumi_testing', user='postgres')
    except InvalidCatalogNameError:
        cmd = "psql -c 'create database hifumi_testing;' -U postgres"
        shell_command(cmd, True)
        pool = await create_pool(database='hifumi_testing', user='postgres')
    async with pool.acquire() as conn:
        await _clear_db(conn)
    await _make_tables(pool)
    return pool


class mock_logger:
    def log(self, *args, **kwargs):
        print(args, kwargs)
