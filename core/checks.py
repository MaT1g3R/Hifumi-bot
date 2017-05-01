"""
Checks for commands
"""
from discord import ChannelType


def is_nsfw(ctx):
    """
    Detiremine if nsfw is enabled for this channel
    :param ctx: the context
    :return: if nsfw is enabled in this channel
    """
    return \
        ctx.message.channel.type == ChannelType.private \
        or ctx.message.channel.name.lower().startswith('nsfw')


def nsfw_exception(e):
    """
    Check if the exception is realted to nsfw
    :param e: the exception
    :return: True if it's related to nsfw
    """
    s = str(e)
    commands = ['danbooru', 'konachan', 'yandere', 'gelbooru']
    for c in commands:
        if 'command {} failed'.format(c) in s:
            return True
    return False
