"""
A collection of functions that's related to discord
"""
import discord
from discord.embeds import Embed


async def message_sender(bot, channel, msg):
    """
    A helper function to send a message 
    :param bot: the bot
    :param channel: the channel to send the messsage to
    :param msg: the message to send
    """
    await bot.send_message(channel, msg)


def get_prefix(bot, message: discord.Message):
    """
    the the prefix of commands for a channel
    :param bot: the discord bot object
    :param message: the message
    :return: the prefix for the server
    """
    if message.server is None:
        return bot.default_prefix
    res = bot.data_handler.get_prefix(message.server.id)
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

