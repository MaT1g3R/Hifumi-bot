"""
The channel reader cog
"""
from core.discord_functions import get_prefix, check_message


class ChannelReader:
    """
    A class that reads messages from the channel
    """
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
                self.bot, message, self.bot.mention_normal + ' prefix'
        ) or check_message(
            self.bot, message, self.bot.mention_nick + ' prefix'
        ):
            prefix = get_prefix(
                self.bot.cur, message.server, self.bot.default_prefix
            )
            localize = self.bot.get_language_dict(message)
            await self.bot.send_message(
                message.channel,
                localize['prefix'].format(prefix, self.bot.default_prefix))
