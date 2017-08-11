import re

from discord import Game, Guild, Message
from discord.ext.commands import CommandNotFound

from core.listen_core import command_error, post_guild_count, process_message, \
    try_change_presence


class Listeners:
    def __init__(self, bot):
        self.bot = bot
        self.logger = self.bot.logger

    async def on_ready(self):
        """
        Event for the bot is ready
        """
        name = f'{self.bot.default_prefix}help | {self.bot.version}'
        await try_change_presence(self.bot, True, game=Game(name=name))
        self.logger.info(f'Logged in as {self.bot.user}\n'
                         f'Client ID: {self.bot.client_id}')
        await post_guild_count(self.bot)
        _mention = f'<@!?{self.bot.client_id}>'
        self.bot.mention_regex = re.compile(_mention)
        self.bot.mention_msg_regex = re.compile(f'^{_mention}\s*[^\s]+.*$')

    async def on_command_error(self, context, exception):
        """
        Custom command error handling
        :param context: the context of the command
        :param exception: the expection raised
        """
        if isinstance(exception, CommandNotFound):
            # Ignore this case.
            return
        # FIXME temporary hack
        if 'NotImplementedError' in str(exception):
            s = ("**This command is under construction**\n\n"
                 "As of June 17, 2017, due to technical problems with the "
                 "previous Hifumi version, all commands and databases has "
                 "been wiped and Hifumi was switched to a newer rewrite. "
                 "This command, as many others, will be back soon and we are "
                 "sorry about this. If you wish more information, "
                 "join to our server and check announcements.\n\n"
                 "Cheers from the Hifumi's developer team~")
            await context.send(s)
            return
        await command_error(context, exception)

    async def on_guild_join(self, guild: Guild):
        """
        Event for joining a guild.
        :param guild: the guild the Bot joined.
        """
        self.bot.logger.info(f'Joined guild {guild.name}')
        await post_guild_count(self.bot)

    async def on_guild_remove(self, guild: Guild):
        """
        Event for removing from a guild.
        :param guild: the guild the Bot was removed from.
        """
        self.bot.logger.info(f'Left guild {guild.name}')
        await post_guild_count(self.bot)

    async def on_message(self, message: Message):
        """
        Listener for Client.on_message.
        :param message: the message.
        """
        await process_message(self.bot, message)
