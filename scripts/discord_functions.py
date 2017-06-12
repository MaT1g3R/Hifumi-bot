"""
A collection of functions that's related to discord
"""
import re

from discord import Forbidden, HTTPException
from discord.ext.commands import CommandOnCooldown
from discord.ext.commands.errors import MissingRequiredArgument

from scripts.checks import AdminError, BadWordError, ManageMessageError, \
    ManageRoleError, NsfwError, OwnerError
from scripts.helpers import strip_letters


def command_error_handler(localize, exception):
    """
    A function that handles command errors
    :param localize: the localization strings
    :param exception: the exception raised
    :return: the message to be sent based on the exception type
    """
    if isinstance(exception, CommandOnCooldown):
        return localize['time_out'].format(strip_letters(str(exception))[0])
    elif isinstance(exception, NsfwError):
        return localize['nsfw_str']
    elif isinstance(exception, BadWordError):
        return localize['bad_word'].format(
            str(exception)) + '\nhttps://imgur.com/8Noy9TH.png'
    elif isinstance(exception, ManageRoleError):
        return localize['not_manage_role']
    elif isinstance(exception, AdminError):
        return localize['not_admin']
    elif isinstance(exception, ManageMessageError):
        return localize['no_manage_messages']
    elif 'Member' in str(exception) and 'not found' in str(exception):
        regex = re.compile('\".*\"')
        name = regex.findall(str(exception))[0].strip('"')
        return localize['member_not_found'].format(name)
    elif isinstance(exception, MissingRequiredArgument) \
            and str(exception).startswith('member'):
        return localize['empty_member']
    elif isinstance(exception, OwnerError):
        return localize['owner_only']
    else:
        # This case should never happen, since it's should be checked in
        # bot.on_command_error
        raise exception


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


async def handle_forbidden_http(ex, bot, channel, localize, action):
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


def add_embed_fields(embed, body):
    """
    Add fileds into a embed.
    :param embed: the embed.
    :param body: a list of tuples with length 2 or 3.
    With the first element be the name of the field,
    the second element be the value of the field,
    the third element be a boolean for inline. defaults to True if the element
    is not present
    :return: the embed with fields added.
    """
    for t in body:
        name = t[0]
        val = t[1]
        if len(t) < 3:
            inline = True
        else:
            inline = t[2]
        embed.add_field(name=name, value=val, inline=inline)
    return embed
