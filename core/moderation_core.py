"""
Functions for Moderation class
"""
from asyncio import sleep

from discord import Member

from core.discord_functions import handle_forbidden_http
from core.roles_core import role_exist, role_unrole


async def ban_kick(bot, ctx, member: Member, delete_message_days):
    """
    A function to handle banning and kicking of members
    :param bot: the bot
    :param ctx: the discord context
    :param member: the member to be banned/kicked
    :param delete_message_days: arg for bot.kick
    """
    localize = bot.get_language_dict(ctx)
    action = 'ban' if delete_message_days is not None else 'kick'
    action_past = 'banned' if delete_message_days is not None else 'kicked'
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
                e, bot, channel, localize, 'clean messages'
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
    action = 'mute' if is_mute else 'unmute'
    if is_mute and member.id == bot.user.id:
        await bot.say(localize['go_away'])
    elif member == ctx.message.author and is_mute:
        await bot.say(localize['ban_kick_mute_self'].format(action))
    elif role_exist('Muted', server):
        await role_unrole(bot, ctx, 'Muted', is_mute, False, member)
    else:
        await bot.say(localize['muted_role_not_found'])
