"""
A collection of functions that's related to discord
"""
import re

from discord import HTTPException, Forbidden
from discord.embeds import Embed
from discord.ext.commands import CommandOnCooldown
from discord.ext.commands.errors import MissingRequiredArgument

from config.settings import DATA_CONTROLLER
from core.checks import NsfwError, BadWordError, ManageRoleError, AdminError, \
    ManageMessageError
from core.helpers import strip_letters


def command_error_handler(bot, exception, context):
    """
    A function that handles command errors
    :param bot: the bot object
    :param exception: the exception raised
    :param context: the discord context object
    :return: the message to be sent based on the exception type
    """
    localize = bot.get_language_dict(context)
    if isinstance(exception, CommandOnCooldown):
        return localize['time_out'].format(strip_letters(str(exception))[0])
    elif isinstance(exception, NsfwError):
        return localize['nsfw_str']
    elif isinstance(exception, BadWordError):
        return localize['bad_word'].format(str(exception))
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
    elif isinstance(exception, MissingRequiredArgument):
        if str(exception).startswith('member'):
            return localize['empty_member']
    else:
        # This case should never happen, since it's should be checked in
        # bot.on_command_error
        raise exception


def get_prefix(bot, message):
    """
    the the prefix of commands for a channel
    :param bot: the discord bot object
    :param message: the message
    :return: the prefix for the server
    """
    if message.server is None:
        return bot.default_prefix
    res = DATA_CONTROLLER.get_prefix(message.server.id)
    return res if res is not None else bot.default_prefix


def build_embed(content: list, colour, **kwargs):
    """
    Build a discord embed object 
    :param content: list of tuples with as such:
        (name, value, *optional: Inline)
        If inline is not provided it defaults to true
    :param colour: the colour of the embed
    :param kwargs: extra options
        author: a dictionary to supply author info as such:
            {
                'name': author name,
                'icon_url': icon url, optional
            }
        footer: the footer for the embed, optional
    :return: a discord embed object
    """
    res = Embed(colour=colour)
    if 'author' in kwargs:
        author = kwargs['author']
        name = author['name'] if 'name' in author else None
        url = author['icon_url'] if 'icon_url' in author else None
        if url is not None:
            res.set_author(name=name, icon_url=url)
        else:
            res.set_author(name=name)
    for c in content:
        name = c[0]
        value = c[1]
        inline = len(c) != 3 or c[2]
        res.add_field(name=name, value=value, inline=inline)
    if 'footer' in kwargs:
        res.set_footer(text=kwargs['footer'])
    return res


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
        temp = message.content[len(prefix):]
        while temp.startswith(' '):
            temp = temp[1:]
        return temp


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
