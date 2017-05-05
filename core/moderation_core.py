"""
Functions for Moderation class
"""
from discord import Member
from discord.client import Forbidden, HTTPException


async def ban_kick(bot, ctx, member: Member, delete_message_days):
    """
    A function to handle banning and kicking of members
    :param bot: the bot
    :param ctx: the discord context
    :param member: the member to be banned/kicked
    :param delete_message_days: arg for bot.kick
    """
    localize = bot.get_language_dict(ctx)
    s = 'ban' if delete_message_days is not None else 'kick'
    s_past_tense = 'banned' if delete_message_days is not None else 'kicked'
    if member == ctx.message.author:
        await bot.say(
            localize['ban_kick_self'].format(s)
        )
        return
    try:
        if delete_message_days is not None:
            await bot.ban(member, delete_message_days)
        else:
            await bot.kick(member)
        await bot.say(localize['banned_kicked'].format(s_past_tense) +
                      '`' + member.name + '`')
    except Forbidden:
        await bot.say(localize['ban_kick_no_perms'])
    except HTTPException:
        await bot.say(localize['ban_kick_fail'].format(s) +
                      '`{}`'.format(member.name))
