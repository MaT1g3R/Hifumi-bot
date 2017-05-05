"""
Checks for commands
"""
from discord import ChannelType
from discord.ext.commands import CommandError
from config.settings import BAD_WORD


class NsfwError(CommandError):
    pass


class BadWordError(CommandError):
    pass


def is_nsfw(ctx):
    """
    Detiremine if nsfw is enabled for this channel
    :param ctx: the context
    :return: if nsfw is enabled in this channel
    """
    res = ctx.message.channel.type == ChannelType.private or \
        ctx.message.channel.name.lower().startswith('nsfw')
    if res:
        return res
    else:
        raise NsfwError


def no_badword(ctx):
    """
    Check if the message has a bad word
    :param ctx: the context
    :return: True if it doesnt have bad words
    """
    input_words = str.split(ctx.message.content, ' ')
    for badword in BAD_WORD:
        for s in input_words:
            if badword in s.lower():
                raise BadWordError(s)
    return True
