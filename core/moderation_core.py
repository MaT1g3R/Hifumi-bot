"""
Functions for Moderation class
"""
from asyncio import sleep

from discord import Member
from discord.utils import get

from config.settings import DATA_CONTROLLER
from core.discord_functions import handle_forbidden_http, get_avatar_url, \
    build_embed, get_name_with_discriminator, get_prefix
from core.helpers import get_date
from core.roles_core import get_server_role, role_unrole


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
        await send_mod_log(ctx, bot, action, member, reason, localize)
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


async def mute_unmute(ctx, bot, member, is_mute):
    """
    Mute/unmute a member
    :param ctx: the message context
    :param bot: the bot
    :param member: the member to be muted/unmuted
    :param is_mute: if True mute, if False unmute
    """
    server = ctx.message.server
    localize = bot.get_language_dict(ctx)
    action = localize['mute'] if is_mute else localize['unmute']
    if is_mute and member.id == bot.user.id:
        await bot.say(localize['go_away'])
    elif member == ctx.message.author and is_mute:
        await bot.say(localize['ban_kick_mute_self'].format(action))
    elif get_server_role('Muted', server) is not None:
        await role_unrole(bot, ctx, 'Muted', is_mute, False, member)
    else:
        await bot.say(localize['muted_role_not_found'])


def get_mod_log_channels(ctx):
    """
    Get the mod log of a server based on the context
    :return: A list of discord.Channel objects for the mod logs
    """
    ids = DATA_CONTROLLER.get_mod_log(ctx.message.server.id)
    res = []
    for id_ in ids:
        channel = get(ctx.message.server.channels, id=id_)
        if channel is not None:
            res.append(channel)
    return res


def add_mod_log(ctx, localize):
    """
    Add a mod log channel into the db
    :param ctx: the discord context
    :param localize: the localizationn strings
    :return: a message to inform mod log has been added
    """
    DATA_CONTROLLER.set_mod_log(
        ctx.message.server.id, ctx.message.channel.id
    )
    return localize['mod_log_add'].format(ctx.message.channel.name)


def remove_mod_log(ctx, localize):
    """
    Remove a mod log entry from the db
    :param ctx: the discord context object
    :param localize: the localization strings
    :return: a message to inform the mod log has been removed
    """
    DATA_CONTROLLER.remove_mod_log(
        ctx.message.server.id, ctx.message.channel.id
    )
    return localize['mod_log_rm'].format(ctx.message.channel.name)


def get_mod_log_name_list(ctx):
    """
    Get a list of mod log channel names
    :param ctx: the message context
    :return: a list of mod log channel names
    """
    id_lst = DATA_CONTROLLER.get_mod_log(ctx.message.server.id)
    res = []
    for id_ in id_lst:
        channel = get(ctx.message.server.channels, id=id_)
        if channel is not None:
            res.append(channel.name)
        else:
            DATA_CONTROLLER.remove_mod_log(
                server_id=ctx.message.server.id,
                channel_id=id_
            )
    return res


def generate_mod_log_list(bot, ctx):
    """
    Generate a mod log list, as a string
    :param bot: the bot
    :param ctx: the discord context
    :return: A formatting string to list all mod log channels
    """
    localize = bot.get_language_dict(ctx)
    names = get_mod_log_name_list(ctx)
    res = localize['mod_log_info'].format(get_prefix(bot, ctx.message))
    return res + localize['mod_log_list'].format('\n'.join(names)) if names \
        else res + localize['mod_log_empty']


def generate_mod_log_entry(action, mod, target, reason, localize):
    """
    Generate a mod log entry
    :param action: the action
    :param mod: the mod that performed the action
    :param target: the target
    :param reason: the reason
    :param localize: the localization strings
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
    body = [(localize['type'], action), (localize['reason'], reason)]
    footer = {
        'text': get_name_with_discriminator(mod) + ' | ' + get_date(),
        'icon_url': get_avatar_url(mod)
    }
    return build_embed(body, colour=colour, author=author, footer=footer)


async def send_mod_log(ctx, bot, action, member, reason, localize):
    """
    Helper function to send a mod log
    :param ctx: the discord funtion
    :param bot: the bot
    :param action: the action preformed
    :param member: the target of the action
    :param reason: the reason of the action
    :param localize: the localization strings
    """
    log_lst = get_mod_log_channels(ctx)
    if log_lst:
        entry = generate_mod_log_entry(
            action, ctx.message.author, member, reason, localize
        )
        for channel in log_lst:
            await bot.send_message(channel, embed=entry)
