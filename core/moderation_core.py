"""
Functions for Moderation class
"""
from asyncio import sleep

from discord import Member
from discord.utils import get

from .data_controller import get_mod_log_, set_mod_log_, remove_mod_log_, \
    add_warn_, remove_warn_, get_warn_
from .discord_functions import get_name_with_discriminator, build_embed, \
    get_avatar_url, handle_forbidden_http, get_prefix
from .helpers import get_date


async def ban_kick(bot, ctx, member: Member, delete_message_days, reason):
    """
    A function to handle banning and kicking of members
    :param bot: the bot
    :param ctx: the discord context
    :param member: the member to be banned/kicked
    :param delete_message_days: arg for bot.kick
    :param reason: the reason the member is ban/kicked
    """
    localize = bot.get_language_dict(ctx)
    action = localize['ban'] if delete_message_days is not None \
        else localize['kick']
    action_past = localize['banned'] if delete_message_days is not None \
        else localize['kicked']
    if member == ctx.message.author:
        await bot.say(
            localize['ban_kick_mute_self'].format(action)
        )
        return
    try:
        if delete_message_days is not None:
            await bot.ban(member, delete_message_days)
        else:
            await bot.kick(member)
        await send_mod_log(ctx, bot, action, member, reason)
        await bot.say(localize['banned_kicked'].format(action_past) +
                      '`' + member.name + '`')
    except Exception as e:
        await handle_forbidden_http(
            e, bot, ctx.message.channel, localize, action
        )


async def clean_msg(ctx, bot, count):
    """
    A function to handle clean message command
    :param ctx: the discord context
    :param bot: the bot
    :param count: number of messages to be cleaned
    """
    count += 1
    localize = bot.get_language_dict(ctx)
    if count < 2 or count > 100:
        await bot.say(localize['clean_message_bad_num'])
    else:
        channel = ctx.message.channel
        try:
            await bot.purge_from(channel, limit=count)
            purge_msg = await bot.say(
                localize['clean_message_success'].format(count - 1))
            await sleep(3)
            await bot.delete_message(purge_msg)
        except Exception as e:
            await handle_forbidden_http(
                e, bot, channel, localize, localize['clean_messages']
            )


async def mute_unmute(ctx, bot, member, is_mute, reason):
    """
    Mute/unmute a member
    :param ctx: the message context
    :param bot: the bot
    :param member: the member to be muted/unmuted
    :param is_mute: if True mute, if False unmute
    :param reason: the reason for mute/unmute
    """
    from core.roles_core import get_server_role
    from core.roles_core import role_unrole
    server = ctx.message.server
    localize = bot.get_language_dict(ctx)
    action = localize['mute'] if is_mute else localize['unmute']
    if is_mute and member.id == bot.user.id:
        await bot.say(localize['go_away'])
    elif member == ctx.message.author and is_mute:
        await bot.say(localize['ban_kick_mute_self'].format(action))
    elif get_server_role('Muted', server) is not None:
        await role_unrole(
            bot=bot,
            target=member,
            role_name='Muted',
            is_add=is_mute,
            is_mute=True,
            check_db=False,
            ctx=ctx,
            reason=reason
        )
    else:
        await bot.say(localize['muted_role_not_found'])


def get_mod_log_channels(cur, server):
    """
    Get the mod log of a server based on the context
    :param cur: the database cursor
    :param server: the discord server
    :return: A list of discord.Channel objects for the mod logs
    """
    ids = get_mod_log_(cur, server.id)
    res = []
    for id_ in ids:
        channel = get(server.channels, id=id_)
        if channel is not None:
            res.append(channel)
    return res


def add_mod_log(*, conn, cur, server_id, channel_id, channel_name, localize):
    """
    Add a mod log channel into the db
    :param conn: the database connection,
    :param cur: the databse cursor
    :param server_id: the server id
    :param channel_id: the channel id
    :param channel_name: the channel name
    :param localize: the localizationn strings
    :return: a message to inform mod log has been added
    """
    set_mod_log_(
        conn, cur, server_id, channel_id
    )
    return localize['mod_log_add'].format(channel_name)


def remove_mod_log(*, conn, cur, server_id, channel_id, channel_name, localize):
    """
    Remove a mod log entry from the db
    :param conn: the database connection,
    :param cur: the databse cursor
    :param server_id: the server id
    :param channel_id: the channel id
    :param channel_name: the channel name
    :param localize: the localizationn strings
    :return: a message to inform the mod log has been removed
    """
    remove_mod_log_(
        conn, cur, server_id, channel_id
    )
    return localize['mod_log_rm'].format(channel_name)


def get_mod_log_name_list(conn, cur, server):
    """
    Get a list of mod log channel names
    :param conn: the database connection,
    :param cur: the databse cursor
    :param server: the discord server
    :return: a list of mod log channel names
    """
    id_lst = get_mod_log_(cur, server.id)
    res = []
    for id_ in id_lst:
        channel = get(server.channels, id=id_)
        if channel is not None:
            res.append(channel.name)
        else:
            remove_mod_log_(
                connection=conn,
                cursor=cur,
                server_id=server.id,
                channel_id=id_
            )
    return res


def generate_mod_log_list(*, localize, conn, cur, server, default_prefix):
    """
    Generate a mod log list, as a string

    :param localize: the localization strings

    :param conn: the database connection

    :param cur: the database cursor

    :param server: the discord server

    :param default_prefix: the bot default prefix

    :return: A formatting string to list all mod log channels
    """
    names = get_mod_log_name_list(conn, cur, server)
    res = localize['mod_log_info'].format(
        get_prefix(cur, server, default_prefix)
    )
    return res + localize['mod_log_list'].format('\n'.join(names)) if names \
        else res + localize['mod_log_empty']


def generate_mod_log_entry(action, mod, target, reason, localize,
                           warn_count=None):
    """
    Generate a mod log entry
    :param action: the action
    :param mod: the mod that performed the action
    :param target: the target
    :param reason: the reason
    :param localize: the localization strings
    :param warn_count: the total warning count on the user
    :return: A discord embed object for the mod log entry
    """
    colour = {
        localize['mute']: 0x591f60,
        localize['unmute']: 0x4286f4,
        localize['ban']: 0xe52424,
        localize['kick']: 0xdd6f1a,
        localize['warn']: 0xddc61a,
        localize['pardon']: 0x4286f4
    }[action]
    author = {
        'name': get_name_with_discriminator(target) + ' ({})'.format(target.id),
        'icon_url': get_avatar_url(target)
    }
    body = [(localize['type'], action.title()), (localize['reason'], reason)]
    if action == localize['warn'] or action == localize['pardon']:
        body.append((localize['warnings'], str(warn_count)))
    footer = {
        'text': get_name_with_discriminator(mod) + ' | ' + get_date(),
        'icon_url': get_avatar_url(mod)
    }
    return build_embed(body, colour=colour, author=author, footer=footer)


async def send_mod_log(ctx, bot, action, member, reason, warn_count=None):
    """
    Helper function to send a mod log
    :param ctx: the discord funtion
    :param bot: the bot
    :param action: the action preformed
    :param member: the target of the action
    :param reason: the reason of the action
    :param warn_count: the total warning count on the user
    """
    localize = bot.get_language_dict(ctx)
    log_lst = get_mod_log_channels(
        bot.cur, ctx.message.server
    )
    if log_lst:
        entry = generate_mod_log_entry(
            action, ctx.message.author, member, reason, localize, warn_count
        )
        for channel in log_lst:
            await bot.send_message(channel, embed=entry)


async def warn_pardon(bot, ctx, reason, member, is_warn):
    """
    Helper function for warn/pardon commands
    :param bot: the bot
    :param ctx: the discord context
    :param reason: the warn/pardon reason
    :param member: the warn/pardon target
    :param is_warn: True for warn, False for pardon
    """
    localize = bot.get_language_dict(ctx)
    author = ctx.message.author
    author = get_name_with_discriminator(author)
    server_id = ctx.message.server.id
    user_id = ctx.message.author.id
    if is_warn:
        add_warn_(
            bot.conn, bot.cur, server_id, user_id
        )
        actions = 'warn', 'warn_success'
    else:
        remove_warn_(
            bot.conn, bot.cur, server_id, user_id
        )
        actions = 'pardon', 'pardon_success'
    warn_count = get_warn_(bot.cur, server_id, user_id)
    await bot.say(
        localize[actions[1]].format(member, reason, author) +
        str(warn_count)
    )
    await send_mod_log(
        ctx, bot, localize[actions[0]], member, reason, warn_count
    )
