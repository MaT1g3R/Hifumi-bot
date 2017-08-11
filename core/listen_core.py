from json import dumps
from textwrap import wrap
from traceback import format_exc
from typing import Optional

from discord import ConnectionClosed, Game, Status
from discord.abc import Messageable
from discord.ext.commands import Context

from bot import HTTPStatusError
from data_controller.data_utils import get_prefix


async def try_change_presence(
        bot, retry: bool, *,
        game: Optional[Game] = None,
        status: Optional[Status] = None,
        afk: bool = False,
        shard_id: Optional[int] = None):
    """
    Try changing presence of the bot.

    :param bot: The bot instance

    :param retry: True to enable retry. Will log out the bot.

    :param game: The game being played. None if no game is being played.

    :param status: Indicates what status to change to. If None, then
    :attr:`Status.online` is used.

    :param afk: Indicates if you are going AFK. This allows the discord
    client to know how to handle push notifications better
    for you in case you are actually idle and not lying.

    :param shard_id: The shard_id to change the presence to. If not
    specified or ``None``, then it will change the presence of every
    shard the bot can see.

    :raises InvalidArgument:
    If the ``game`` parameter is not :class:`Game` or None.

    :raises ConnectionClosed:
    If retry parameter is set to False and ConnectionClosed was raised by
    super().change_presence
    """
    try:
        await bot.wait_until_ready()
        await bot.change_presence(
            game=game, status=status, afk=afk, shard_id=shard_id
        )
    except ConnectionClosed as e:
        if retry:
            bot.logger.warning(str(e))
            await bot.logout()
            await bot.login(bot.config['Bot']['token'])
            await try_change_presence(
                bot, retry, game=game, status=status,
                afk=afk, shard_id=shard_id
            )
        else:
            raise e


def format_command_error(context: Context, ex: Exception) -> tuple:
    """
    Format a command error to display and log.

    :param ex: the exception raised.

    :param context: the context.

    :return: a message to be displayed and logged, and triggered message
    """
    triggered = context.message.content
    four_space = ' ' * 4
    ex_type = type(ex).__name__
    return (f'{four_space}Triggered message: {triggered}\n'
            f'{four_space}Type: {ex_type}\n'
            f'{four_space}Exception: {str(ex)}'), triggered


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


async def send_traceback(channel, tb, header):
    """
    Send traceback to the error log channel if it exists.

    :param channel: The channel to send tb to.

    :param tb: the traceback.

    :param header: the header for the error.
    """
    if not channel:
        return
    await channel.send(header)
    for s in format_traceback(tb):
        await channel.send(s)


async def command_error(ctx, ex):
    """
    Handle command error.

    Send error message to the context and send traceback to the
    error log channel.

    :param ctx: The discord Context.

    :param ex: the exception raised.
    """
    id_ = ctx.bot.config['Bot']['error log']
    ch = ctx.bot.get_channel(id_)
    try:
        raise ex
    except Exception as e:
        tb = format_exc()
        msg, triggered = format_command_error(ctx, e)
        ctx.bot.logger.warning(f'\n{msg}\n\n{tb}')
        await ctx.send(
            ctx.bot.translate(ctx, 'sentence', 'ex_warn').format(msg)
        )
        await send_traceback(
            ch, tb, f'**WARNING** Triggered message:\n{triggered}'
        )


async def post_guild_count(bot):
    """
    Post guild count to
    https://discordbots.org/ and https://bots.discord.pw/

    :param bot: the bot instance.
    """
    botsorgapi = bot.config['Bot lists']['discord bots dot org']
    bots_discord_pw = bot.config['Bot lists']['bots_discord_pw']
    if not bots_discord_pw and not botsorgapi:
        return
    data = dumps({
        'shard_id': bot.shard_id,
        'shard_count': bot.shard_count,
        'server_count': len(bot.guilds)
    })
    if botsorgapi:
        await __try_post(bot, 'discordbots.org', data, botsorgapi)
    if bots_discord_pw:
        await __try_post(bot, 'bots.discord.pw', data, bots_discord_pw)


async def __try_post(bot, site, data, key):
    """
    Try to post guild count to the site.

    :param bot: the bot instance.

    :param site: the site name.

    :param data: the data to post.

    :param key: the api key.
    """
    url = f'https://{site}/api/bots/{bot.client_id}/stats'
    header = {
        'authorization': key,
        'content-type': 'application/json'
    }
    try:
        async with await bot.session_manager.post(url, data=data,
                                                  headers=header):
            bot.logger.info(f'Posted {data} to {site}')
    except HTTPStatusError as e:
        bot.logger.warn(str(e))


async def process_message(bot, message):
    """
    Process the message recieved from Client.on_message

    :param bot: The bot instance.

    :param message: The message recieved.
    """
    author = message.author
    content = message.content
    channel = message.channel
    prefix = get_prefix(bot, message)
    if (author.bot or
            content.startswith(prefix) or
            not isinstance(content, str) or
            not isinstance(channel, Messageable)):
        return
    prefix_msg = __for_prefix(
        bot, message, prefix, bot.default_prefix
    )
    if prefix_msg:
        await channel.send(prefix_msg)


def __strip_mention(mention, mention_msg, s: str):
    """
    Strip message starts with mention to the bot.

    :param mention: The regex to match for the bot mention.

    :param mention_msg:
        The regex to match for if the message starts with
        the mention to the bot and has at least one non-empty
        character beside the mention.

    :param s: The string to match against.

    :return: The message with sripped mentions if both regex matched.
    """
    match = mention_msg.fullmatch(s)
    mention = mention.findall(s)
    if match and mention:
        return match.string.replace(mention[0], '', 1).strip()


def __for_prefix(bot, message, prefix, default_prefix):
    """
    Get the string to display help bot prefix.

    :param bot: the bot instance.

    :param message: message recieved from Client.on_message

    :param prefix: Bot prefix for the message.

    :param default_prefix: default bot prefix.

    :return:
        The message to display if the message starts with a mention to
        the bot and contains only 'prefix'

        Otherwise return None.
    """

    stripped = __strip_mention(
        bot.mention_regex, bot.mention_msg_regex, message.content
    )
    if stripped and stripped.lower() == 'prefix':
        local_str = bot.translate(message, 'sentence', 'prefix')
        return local_str.format(prefix, default_prefix)
