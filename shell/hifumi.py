"""
The hifumi bot object
"""
from asyncio import coroutine

from discord.ext.commands import Bot, CommandOnCooldown
from discord.game import Game

from core.discord_functions import message_sender


class Hifumi(Bot):
    """
    The hifumi bot class
    """

    def __init__(self, prefix, default_prefix,
                 data_handler, shard_count=1, shard_id=0):
        """
        Initialize the bot object
        :param prefix: the function to get prefix for a server
        :param default_prefix: the default bot prefix
        :param data_handler: the database handler
        :param shard_count: the shard count, default is 1
        :param shard_id: shard id, default is 0
        """
        super().__init__(command_prefix=prefix, shard_count=shard_count,
                         shard_id=shard_id)
        self.default_prefix = default_prefix
        self.data_handler = data_handler
        self.shard_id = shard_id
        self.shard_count = shard_count

    async def on_ready(self):
        """
        Event for the bot is ready
        """
        g = '{}/{} | ~help'.format(self.shard_id + 1, self.shard_count)
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')
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
