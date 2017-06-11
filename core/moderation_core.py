"""
Functions for Moderation class
"""
from asyncio import sleep

from discord import Member
from discord.embeds import Embed
from discord.utils import get

from bot import Hifumi
from data_controller.data_utils import get_modlog
from scripts.discord_functions import add_embed_fields, get_avatar_url, \
    get_name_with_discriminator, handle_forbidden_http
from scripts.helpers import get_date


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
    from core.roles_core import role_unrole
    guild = ctx.message.server
    localize = bot.get_language_dict(ctx)
    action = localize['mute'] if is_mute else localize['unmute']
    if is_mute and member.id == bot.user.id:
        await bot.say(localize['go_away'])
    elif member == ctx.message.author and is_mute:
        await bot.say(localize['ban_kick_mute_self'].format(action))
    elif get(guild.roles, name='Muted') is not None:
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
    body = [(localize['type'], action.title()), (localize['reason'], reason)]
    if action == localize['warn'] or action == localize['pardon']:
        body.append((localize['warnings'], str(warn_count)))
    embed = Embed(colour=colour)
    embed.set_author(
        name=get_name_with_discriminator(target) + ' ({})'.format(target.id),
        icon_url=get_avatar_url(target))
    embed.set_footer(text=get_name_with_discriminator(mod) + ' | ' + get_date(),
                     icon_url=get_avatar_url(mod))
    return add_embed_fields(embed, body)


async def send_mod_log(
        ctx, bot: Hifumi, action, member, reason, warn_count=None):
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
    mod_log = bot.data_manager.get_mod_log(int(ctx.message.server.id))
    if mod_log:
        entry = generate_mod_log_entry(
            action, ctx.message.author, member, reason, localize, warn_count
        )
        # FIXME Remove str when library rewrite is finished
        channel = get_modlog(bot.data_manager, ctx.message.server)
        if channel:
            await bot.send_message(channel, embed=entry)


async def warn_pardon(bot: Hifumi, ctx, reason, member, is_warn):
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
        data_manager.set_member_warns(member_id, guild_id, new_warn_count)
        actions = 'warn', 'warn_success'
    else:
        new_warn_count = max(0, warn_count - 1)
        data_manager.set_member_warns(member_id, guild_id, new_warn_count)
        actions = 'pardon', 'pardon_success'

    await bot.say(
        localize[actions[1]].format(member, reason, author) +
        str(new_warn_count)
    )
    await send_mod_log(
        ctx, bot, localize[actions[0]], member, reason, new_warn_count
    )
