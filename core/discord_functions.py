"""
A collection of functions that's related to discord
"""
import discord


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
