"""
The hifumi bot object
"""
import time
from asyncio import coroutine

from discord.ext.commands import Bot, CommandOnCooldown
from discord.game import Game

from core.discord_functions import message_sender
from core.bot_info_core import update_shard_info
from config.settings import DEFAULT_PREFIX
from core.checks import nsfw_exception


class Hifumi(Bot):
    """
    The hifumi bot class
    """

    def __init__(self, prefix, data_handler, token, shard_count=1, shard_id=0):
        """
        Initialize the bot object
        :param prefix: the function to get prefix for a server
        :param data_handler: the database handler
        :param token: the bot token
        :param shard_count: the shard count, default is 1
        :param shard_id: shard id, default is 0
        """
        super().__init__(command_prefix=prefix, shard_count=shard_count,
                         shard_id=shard_id)
        self.default_prefix = DEFAULT_PREFIX
        self.data_handler = data_handler
        self.shard_id = shard_id
        self.shard_count = shard_count
        self.start_time = time.time()
        self.token = token

    async def on_ready(self):
        """
        Event for the bot is ready
        """
        g = '{}/{} | ~help'.format(self.shard_id + 1, self.shard_count)
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')
        update_shard_info(self)
        await self.change_presence(game=Game(name=g))

    @coroutine
    async def on_command_error(self, exception, context):
        """
        Custom command error handling
        :param exception: the expection raised
        :param context: the context of the command
        """
        nsfw_str = 'NSFW commands must be used in DM or channel ' \
                   'with name that equal to or start with ' \
                   '`nsfw` (case insensitive)'
        if isinstance(exception, CommandOnCooldown):
            await message_sender(self, context.message.channel, str(exception))
        elif str(exception) == 'Command "eval" is not found':
            return
        elif nsfw_exception(exception):
            await message_sender(self, context.message.channel, nsfw_str)
        else:
            raise exception

    def mention_normal(self):
        """
        Returns the bot id in <@> format
        :return: bot id in <@> format
        """
        return '<@%s>' % self.user.id

    def mention_nick(self):
        """
        Returns the bot id in <!@> format
        :return: the bot id in <!@> format
        """
        return '<@!%s>' % self.user.id

    def start_bot(self, cogs: list):
        """
        Start the bot
        :param cogs: a list of cogs
        """
        self.remove_command('help')
        for cog in cogs:
            self.add_cog(cog)
        self.run(self.token)
