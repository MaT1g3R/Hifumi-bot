"""
Checks for commands
"""

from discord import ChannelType
from discord.ext.commands import CommandError

# A list of bad words to comply with discord TOS, DON'T edit this
BAD_WORD = ['loli', 'l0l1', 'lol1', 'l0li', '7071', 'lolii', 'looli', 'lolli',
            'shota', 'sh07a', 'sh0ta', 'chota', 'ch0ta', 'shot4', 'sh0t4',
            '5hota', '5h0ta', '5h0t4', '7oli', '70li', '707i', 'l071', 'hifumi',
            'takimoto', 'child', 'children', 'cp', 'preteen', 'teen', 'gore',
            'g0r3', 'g0re', 'ch1ld', 'kid', 'k1d', 'kiddo', 'ロリ', 'ロリコン',
            'pico', 'ショタコン', 'ショタ']


class NsfwError(CommandError):
    pass


class BadWordError(CommandError):
    pass


class ManageRoleError(CommandError):
    pass


class AdminError(CommandError):
    pass


class ManageMessageError(CommandError):
    pass


class OwnerError(CommandError):
    pass


def is_nsfw(ctx):
    """
    Detiremine if nsfw is enabled for this channel
    :param ctx: the context
    :return: if nsfw is enabled in this channel
    """
    if ctx.message.channel.type == ChannelType.private \
            or ctx.message.channel.name.lower().startswith('nsfw'):
        return True
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


def has_manage_role(ctx):
    """
    Check if an user has the manage_roles permissions
    :param ctx: the context
    :return: True if the user has the manage_roles permissions
    :rtype: bool
    """
    id_ = ctx.message.author.id
    if ctx.message.server.get_member(id_).server_permissions.manage_roles:
        return True
    raise ManageRoleError


def is_admin(ctx):
    """
    Check if the user has admin permissions
    :param ctx: the discord context
    :return: True if the user has admin permissions
    """
    id_ = ctx.message.author.id
    if ctx.message.server.get_member(id_).server_permissions.administrator:
        return True
    raise AdminError


def has_manage_message(ctx):
    """
    Check if the user has manage message permissions
    :param ctx: the discord context
    :return: True if the user has manage message permissions
    """
    id_ = ctx.message.author.id
    if ctx.message.server.get_member(id_).server_permissions.manage_messages:
        return True
    raise ManageMessageError


def is_owner(ctx):
    """
    :param ctx: the discord context
    :return: True if the user is the bot owner
    """
    # FIXME Remove casting after lib rewrite
    id_ = int(ctx.message.author.id)
    if id_ in ctx.bot.config['owner']:
        return True
    raise OwnerError
