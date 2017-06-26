"""
A collection of functions that's related to discord
"""
from typing import Optional

from discord import Channel, Forbidden, HTTPException, Role, Server
from discord.utils import get


def check_message(bot, message, expected):
    """
    A helper method to check if a message's content matches with expected 
    result and the author isn't the bot.
    :param bot: the bot
    :param message: the message to be checked
    :param expected: the expected result
    :return: true if the message's content equals the expected result and 
    the author isn't the bot
    """
    return \
        message.content == expected and \
        message.author.id != bot.user.id and \
        not message.author.bot


def check_message_startwith(bot, message, expected):
    """
    A helper method to check if a message's content start with expected 
    result and the author isn't the bot.
    :param bot: the bot
    :param message: the message to be checked
    :param expected: the expected result
    :return: true if the message's content equals the expected result and 
    the author isn't the bot
    """
    return \
        message.content.startswith(expected) and \
        message.author.id != bot.user.id and \
        not message.author.bot


def clense_prefix(message, prefix: str):
    """
    Clean the message's prefix
    :param message: the message
    :param prefix: the prefix to be cleaned
    :return: A new message without the prefix
    """
    if not message.content.startswith(prefix):
        return message.content
    else:
        return message.content[len(prefix):].strip()


async def handle_forbidden_http(
        ex: Exception, bot, channel: Channel, localize: dict, action: str):
    """
    Exception handling for Forbidden and HTTPException
    :param ex: the exception raised
    :param bot: the bot
    :param channel: the channel to send a message to
    :param localize: the localize strings
    :param action: the action that caused the exception
    """
    if isinstance(ex, Forbidden):
        await bot.send_message(channel, localize['no_perms'])
    elif isinstance(ex, HTTPException):
        await bot.send_message(channel, localize['https_fail'].format(action))
    else:
        raise ex


def get_avatar_url(member):
    """
    Get the avatar url of a member
    :param member: the discord member
    :return: the avatar url of the member
    """
    return '{0.avatar_url}'.format(member) if member.avatar_url != '' \
        else member.default_avatar_url


def get_name_with_discriminator(member):
    """
    Get the name of a member with discriminator
    :param member: the member
    :return: the name of a member with discriminator
    """
    return member.display_name + '#' + member.discriminator


# FIXME Change Server to Guild after lib rewrite
def get_server_role(role_name: str, guild: Server) -> Optional[Role]:
    """
    Get a role by name from a guild.
    :param role_name: the role name.
    :param guild: the guild.
    :return: the role with the same name as role name if it exists, else None
    """
    return get(guild.roles, name=role_name)
