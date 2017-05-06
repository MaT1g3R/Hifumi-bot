"""
The channel reader cog
"""
from core.discord_functions import get_prefix, check_message


class ChannelReader:
    __slots__ = ['bot']

    def __init__(self, bot):
        """
        Initialize the ChannelReader class
        :param bot: the bot object
        """
        self.bot = bot

    async def on_message(self, message):
        """
        Events for reading messages
        :param message: the message
        """
        if check_message(
                self.bot, message, self.bot.mention_normal() + ' prefix') \
                or check_message(
                    self.bot, message, self.bot.mention_nick() + ' prefix'):
            prefix = get_prefix(self.bot, message)
            await self.bot.send_message(
                message.channel,
                'The prefix for this server is: `{}`'.format(prefix))
