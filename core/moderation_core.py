"""
Functions for Moderation class
"""
from asyncio import sleep

from discord import Member, Role
from discord.embeds import Embed

from bot import Hifumi
from data_controller.data_utils import get_modlog
from scripts.discord_functions import get_avatar_url, \
    get_name_with_discriminator, get_server_role, handle_forbidden_http
from scripts.helpers import get_date


async def ban_kick(bot: Hifumi, ctx, member: Member, reason: str,
                   is_ban: bool, delete_message_days: int = 0):
    """
    A function to handle banning and kicking of members
    :param bot: the bot
    :param ctx: the discord context
    :param member: the member to be banned/kicked
    :param is_ban: True for a ban, False for a kick
    :param delete_message_days: number of days to delete messages of the banned
    user, not used for kick.
    :param reason: the reason the member is ban/kicked
    """
    localize = bot.get_language_dict(ctx)
    action = localize['ban'] if is_ban else localize['kick']
    action_past = localize['banned'] if is_ban else localize['kicked']
    if member == ctx.message.author:
        await bot.say(
            localize['ban_kick_mute_self'].format(action)
        )
        return
    try:
        if is_ban:
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


async def clean_msg(ctx, bot: Hifumi, count: int):
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
        return
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


async def __mute(ctx, bot: Hifumi, member: Member, muted_role: Role,
                 is_mute: bool, localize: dict, action: str, reason: str):
    """
    Helper function to mute/unmute a member
    :param ctx: the discsord context
    :param bot: the bot
    :param member: the member to be muted/unmuted
    :param muted_role: the 'Muted' role to assign/remove to the member.
    :param is_mute: True to mute, False to unmute
    :param localize: the localization strings.
    :param action: the action string. ('mute' or 'unmute' in case of english)
    :param reason: the reason for mute/unmute.
    """
    try:
        if is_mute:
            await bot.add_roles(member, muted_role)
        else:
            await bot.remove_roles(member, muted_role)
    except Exception as e:
        await handle_forbidden_http(
            e, bot, ctx.message.channel, localize, action)
    else:
        _res = localize['muted'] if is_mute else localize['unmuted']
        res = localize['mute_unmute_success'].format(
            _res, member.name, reason
        )
        await send_mod_log(ctx, bot, action, member, reason)
        await bot.send_message(ctx.message.channel, res)


async def mute_unmute(ctx, bot: Hifumi, member: Member,
                      is_mute: bool, reason: str):
    """
    Mute/unmute a member
    :param ctx: the discsord context
    :param bot: the bot
    :param member: the member to be muted/unmuted
    :param is_mute: if True mute, if False unmute
    :param reason: the reason for mute/unmute
    """
    # FIXME change server to guild when rewrite is finished
    guild = ctx.message.server
    localize = await bot.get_language_dict(ctx)
    action = localize['mute'] if is_mute else localize['unmute']
    if is_mute and member.id == bot.user.id:
        await bot.say(localize['go_away'])
        return
    elif member == ctx.message.author and is_mute:
        await bot.say(localize['ban_kick_mute_self'].format(action))
        return
    muted_role = get_server_role('Muted', guild)
    if muted_role:
        await __mute(
            ctx, bot, member, muted_role, is_mute, localize, action, reason)
    else:
        await bot.send_message(
            ctx.message.channel, localize['muted_role_not_found'])


def generate_mod_log_entry(action: str, mod: Member, target: Member,
                           reason: str, localize: dict,
                           warn_count: int = None):
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
    embed = Embed(colour=colour)

    embed.set_author(
        name=get_name_with_discriminator(target) + ' ({})'.format(target.id),
        icon_url=get_avatar_url(target)
    )
    embed.set_footer(
        text=get_name_with_discriminator(mod) + ' | ' + get_date(),
        icon_url=get_avatar_url(mod)
    )

    embed.add_field(name=localize['type'], value=action.title())
    embed.add_field(name=localize['reason'], value=reason)
    if action == localize['warn'] or action == localize['pardon']:
        embed.add_field(name=localize['warnings'], value=str(warn_count))

    return embed


async def send_mod_log(ctx, bot: Hifumi, action: str, member: Member,
                       reason: str, warn_count: int = None):
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
    # FIXME Remove type casting when library rewrite is finished
    mod_log = bot.data_manager.get_mod_log(int(ctx.message.server.id))
    if mod_log:
        entry = generate_mod_log_entry(
            action, ctx.message.author, member, reason, localize, warn_count
        )
        channel = get_modlog(bot.data_manager, ctx.message.server)
        if channel:
            await bot.send_message(channel, embed=entry)


async def warn_pardon(bot: Hifumi, ctx, reason: str, member: Member,
                      is_warn: bool):
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
    # FIXME Remove casting when library rewrite is finished
    guild_id = int(ctx.message.server.id)
    member_id = int(ctx.message.author.id)
    data_manager = bot.data_manager
    warn_count = data_manager.get_member_warns(member_id, guild_id) or 0
    if is_warn:
        new_warn_count = warn_count + 1
        actions = 'warn', 'warn_success'
    else:
        new_warn_count = max(0, warn_count - 1)
        actions = 'pardon', 'pardon_success'
    data_manager.set_member_warns(member_id, guild_id, new_warn_count)
    await bot.say(
        localize[actions[1]].format(member, reason, author) +
        str(new_warn_count)
    )
    await send_mod_log(
        ctx, bot, localize[actions[0]], member, reason, new_warn_count
    )
