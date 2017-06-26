import re
from textwrap import wrap

from asyncpg import connect
from discord.ext.commands import BadArgument, CommandOnCooldown, Context, \
    MissingRequiredArgument

from data_controller import DataManager, TagMatcher
from data_controller.postgres import get_postgres
from scripts.checks import AdminError, BadWordError, ManageMessageError, \
    ManageRoleError, NsfwError, OwnerError
from scripts.helpers import strip_letters
from scripts.logger import info


async def get_data_manager(pg_config: dict) -> tuple:
    """
    Get an instance of DataManager and TagMatcher.
    :param pg_config: the postgres config info.
    :return: a tuple of (DataManager, TagMatcher)
    """
    conn = await connect(
        host=pg_config['host'], port=pg_config['port'], user=pg_config['user'],
        database=pg_config['database'], password=pg_config['password']
    )
    post = await get_postgres(conn, pg_config['schema']['production'])
    data_manager = DataManager(post)
    tag_matcher = TagMatcher(post, await post.get_tags())
    info('Connected to database: {}.{}'.format(
        pg_config['database'], pg_config['schema']['production']))
    return data_manager, tag_matcher


def command_error_handler(localize, exception):
    """
    A function that handles command errors
    :param localize: the localization strings
    :param exception: the exception raised
    :return: the message to be sent based on the exception type
    """
    ex_str = str(exception)
    res = None
    if isinstance(exception, CommandOnCooldown):
        res = localize['time_out'].format(strip_letters(ex_str)[0])
    elif isinstance(exception, NsfwError):
        res = localize['nsfw_str']
    elif isinstance(exception, BadWordError):
        res = localize['bad_word'].format(
            str(exception)) + '\nhttps://imgur.com/8Noy9TH.png'
    elif isinstance(exception, ManageRoleError):
        res = localize['not_manage_role']
    elif isinstance(exception, AdminError):
        res = localize['not_admin']
    elif isinstance(exception, ManageMessageError):
        res = localize['no_manage_messages']
    elif isinstance(exception, BadArgument):
        regex = re.compile('\".*\"')
        name = regex.findall(ex_str)[0].strip('"')
        if ex_str.lower().startswith('member'):
            res = localize['member_not_found'].format(name)
        elif ex_str.lower().startswith('channel'):
            res = localize['channel_not_found'].format(name)
    elif isinstance(exception, MissingRequiredArgument):
        if ex_str.startswith('member'):
            res = localize['empty_member']
        elif ex_str.startswith('channel'):
            res = localize['empty_channel']
        # FIXME for the temporary Music cog, change after Music is finished
        elif ex_str.startswith('song'):
            res = 'Please provide a song name/link for me to play.'
    elif isinstance(exception, OwnerError):
        res = localize['owner_only']
    if res:
        return res
    raise exception


def format_command_error(ex: Exception, context: Context):
    """
    Format a command error to display and log.
    :param ex: the exception raised.
    :param context: the context.
    :return: a message to be displayed and logged.
    """
    triggered = context.message.content
    four_space = ' ' * 4
    ex_type = type(ex).__name__
    return (f'{four_space}Triggered message: {triggered}\n'
            f'{four_space}Type: {ex_type}\n'
            f'{four_space}Exception: {str(ex)}')


def format_traceback(tb: str):
    """
    Format a traceback to be able to display in discord.
    :param tb: the traceback.
    :return: the traceback divided up into sections of max 1800 chars.
    """
    res = wrap(tb, 1800, replace_whitespace=False)
    str_out = ['```py\n' + s.replace('`', chr(0x1fef)) + '\n```'
               for s in res]
    return str_out
