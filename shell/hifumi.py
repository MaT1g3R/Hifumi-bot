"""
The hifumi bot object
"""
import time
from asyncio import coroutine

from discord.ext.commands import Bot, CommandOnCooldown
from discord.game import Game

from core.discord_functions import message_sender
from core.bot_info_core import update_shard_info


class Hifumi(Bot):
    """
    The hifumi bot class
    """

    def __init__(self, prefix, default_prefix, data_handler,
                 devs: list, helpers: list,
                 shard_count=1, shard_id=0, colour=0x4286f4, name='Hifumi+'):
        """
        Initialize the bot object
        :param prefix: the function to get prefix for a server
        :param default_prefix: the default bot prefix
        :param data_handler: the database handler
        :param devs: list of developers 
        :param helpers: list of bot helpers
        :param shard_count: the shard count, default is 1
        :param shard_id: shard id, default is 0
        :param colour: the bot colour, default is 0x4286f4
        :param name: the bot name, default is Hifumi+
        """
        super().__init__(command_prefix=prefix, shard_count=shard_count,
                         shard_id=shard_id)
        self.default_prefix = default_prefix
        self.data_handler = data_handler
        self.shard_id = shard_id
        self.shard_count = shard_count
        self.start_time = time.time()
        self.colour = colour
        self.name = name
        self.devs = devs
        self.helpers = helpers

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
        if isinstance(exception, CommandOnCooldown):
            await message_sender(self, context.message.channel, str(exception))
        else:
            raise exception
