from itertools import chain
from logging import CRITICAL, ERROR, INFO

from asyncpg import create_pool
from discord.ext.commands import Context

from data_controller import DataManager, TagMatcher
from data_controller.postgres import Postgres


async def get_data_manager(pg_config: dict, logger) -> tuple:
    """
    Get an instance of DataManager and TagMatcher.
    :param pg_config: the postgres config info.
    :param logger: the logger.
    :return: a tuple of (DataManager, TagMatcher)
    """
    pool = await create_pool(
        host=pg_config['host'], port=pg_config['port'], user=pg_config['user'],
        database=pg_config['database'], password=pg_config['password']
    )
    post = Postgres(pool, pg_config['schema'], logger)
    data_manager = DataManager(post)
    tag_matcher = TagMatcher(post, await post.get_tags())
    logger.log(INFO, 'Connected to database: {}.{}'.format(
        pg_config['database'], pg_config['schema']))
    await data_manager.init()
    return data_manager, tag_matcher


def handle_error(tb, event_method, *args, **kwargs) -> tuple:
    """
    Handle error passed to ``on_error``

    Check :func:`discord.Client.on_error` for more details.

    :return: a tuple of
        (Log level, log message, error header, error context if any)
    """
    ig = f'Ignoring exception in {event_method}\n'
    log_msg = f'\n{ig}\n{tb}'
    header = f'**CRITICAL**\n{ig}'
    lvl = CRITICAL
    ctx = None
    for arg in chain(args, kwargs.values()):
        if isinstance(arg, Context):
            ctx = arg
            header = f'**ERROR**\n{ig}'
            lvl = ERROR
            break
    return lvl, log_msg, header, ctx
