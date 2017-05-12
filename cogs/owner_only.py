"""
Owner only commands
"""

from config.settings import OWNER
from core.discord_functions import check_message_startwith, clense_prefix, \
    get_prefix
from core.owner_only_core import handle_eval


class OwnerOnly:
    """
    OwnerOnly commands
    """
    __slots__ = ['bot']

    def __init__(self, bot):
        """
        Initialize the OwnerOnly class
        :param bot: the bot object
        """
        self.bot = bot

    async def on_message(self, message):
        """
        Events for reading messages
        :param message: the message
        """
        prefix = get_prefix(
            self.bot.cur, message.server, self.bot.default_prefix
        )
        if check_message_startwith(self.bot, message, '{}eval'.format(prefix)):
            if str(message.author.id) in OWNER:
                args = clense_prefix(message, '{}eval'.format(prefix))
                await self.bot.send_message(message.channel, handle_eval(args))
            else:
                await self.bot.send_message(
                    message.channel,
                    'Sorry! Only my owner can use this command.')
