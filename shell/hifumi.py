"""
The hifumi bot object
"""
import logging
import time
from asyncio import coroutine
from os.path import join
from threading import Timer

from discord import ChannelType
from discord.ext.commands import Bot, CommandOnCooldown
from discord.game import Game

from config.settings import DEFAULT_PREFIX
from config.settings import SHARDED
from core.bot_info_core import generate_shard_info
from core.checks import nsfw_exception
from core.discord_functions import command_error_handler
from core.file_io import read_all_files, read_json, write_json


class Hifumi(Bot):
    """
    The hifumi bot class
    """

    def __init__(self, prefix, data_handler, shard_count=1, shard_id=0,
                 default_language='en'):
        """
        Initialize the bot object
        :param prefix: the function to get prefix for a server
        :param data_handler: the database handler
        :param shard_count: the shard count, default is 1
        :param shard_id: shard id, default is 0
        :param default_language: the default language of the bot, default is en
        """
        super().__init__(command_prefix=prefix, shard_count=shard_count,
                         shard_id=shard_id)
        self.default_prefix = DEFAULT_PREFIX
        self.data_handler = data_handler
        self.shard_id = shard_id
        self.shard_count = shard_count
        self.start_time = time.time()
        self.language = {f[14:-5]: read_json(open(f))
                         for f in read_all_files(join('data', 'language'))
                         if f.endswith('.json')}
        self.default_language = default_language
        logger = logging.getLogger('discord')
        logger.setLevel(logging.DEBUG)
        handler = logging.FileHandler(
            filename=join('data', 'logs', '{}.log'.format(self.start_time)),
            encoding='utf-8',
            mode='w')
        handler.setFormatter(
            logging.Formatter(
                '%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
        logger.addHandler(handler)

    async def on_ready(self):
        """
        Event for the bot is ready
        """
        g = '{}help'.format(self.default_prefix)
        if SHARDED:
            g = '{}/{} | '.format(self.shard_id + 1, self.shard_count) + g
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')
        await self.change_presence(game=Game(name=g))
        if SHARDED:
            self.update_shard_info()

    @coroutine
    async def on_command_error(self, exception, context):
        """
        Custom command error handling
        :param exception: the expection raised
        :param context: the context of the command
        """
        if isinstance(exception, CommandOnCooldown) \
                or nsfw_exception(exception):
            await command_error_handler(self, exception, context)
        elif str(exception) == 'Command "eval" is not found':
            return
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

    def start_bot(self, cogs: list, token):
        """
        Start the bot
        :param cogs: a list of cogs
        :param token: the bot token
        """
        self.remove_command('help')
        for cog in cogs:
            self.add_cog(cog)
        self.run(token)

    def get_language_dict(self, ctx):
        """
        Get the language of the given context
        :param ctx: the discord context object
        :return: the language dict
        :rtype: dict
        """
        return self.language[self.get_language_key(ctx)]

    def get_language_key(self, ctx):
        """
        Get the language key of the context
        :param ctx: the discord context
        :return: the language key
        """
        channel = ctx.message.channel
        if channel.type == ChannelType.text:
            server_id = ctx.message.server.id
            lan = self.data_handler.get_language(str(server_id))
            return lan if lan is not None else self.default_language
        else:
            return self.default_language

    def update_shard_info(self):
        """
        Updates the bot shard info every second
        """
        Timer(1, self.update_shard_info).start()
        file_name = join('data', 'shard_info',
                         'shard_{}.json'.format(self.shard_id))
        content = generate_shard_info(self)
        write_json(open(file_name, 'w+'), content)
