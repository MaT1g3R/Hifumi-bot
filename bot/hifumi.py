"""
The Hifumi bot object
"""

import traceback
from logging import CRITICAL, ERROR, WARNING
from pathlib import Path
from time import time

from aiohttp import ClientSession
from asyncpg import connect
from discord import ChannelType, Game, HTTPException, Message
from discord.ext.commands import BadArgument, Bot, CommandNotFound, \
    CommandOnCooldown, Context, MissingRequiredArgument
from websockets.exceptions import ConnectionClosed

from bot.session_manager import SessionManager
from config import Config
from data_controller import *
from data_controller.data_utils import get_prefix
from data_controller.postgres import get_postgres
from scripts.checks import AdminError, BadWordError, ManageMessageError, \
    ManageRoleError, NsfwError, OwnerError
from scripts.discord_functions import command_error_handler
from scripts.language_support import read_language
from scripts.logger import get_console_handler, info, setup_logging


class Hifumi(Bot):
    """
    The Hifumi bot class
    """
    __slots__ = ['shard_id', 'shard_count', 'start_time', 'language',
                 'default_language', 'logger', 'mention_normal', 'mention_nick',
                 'all_emojis', 'config', 'session_manager']

    def __init__(self, config: Config, shard_id: int, loop, default_lan='en'):
        """
        Initialize the bot object.
        :param config: the Config object.
        :param shard_id: the shard id.
        :param loop: the asyncio event loop.
        :param default_lan: the default language.
        """
        self.config = config
        self.session_manager = None
        self.shard_count = config['Bot']['shard count']
        self.shard_id = shard_id
        self.tag_matcher = None
        self.data_manager = None
        self.start_time = int(time())
        self.language = read_language(Path('./data/language'))
        self.default_language = default_lan
        self.logger = setup_logging(
            self.start_time, Path('./data/logs')
        )
        self.mention_normal = ''
        self.mention_nick = ''
        with Path('./data/emojis.txt').open() as f:
            self.all_emojis = f.read().splitlines()
            f.close()
        super().__init__(
            command_prefix=get_prefix,
            shard_count=self.shard_count,
            shard_id=self.shard_id,
            loop=loop
        )

    @property
    def default_prefix(self):
        return str(self.config['Bot']['prefix'])

    async def set_postgres(self):
        pg = self.config.postgres()
        conn = await connect(
            host=pg['host'], port=pg['port'], user=pg['user'],
            database=pg['database'], password=pg['password']
        )
        post = await get_postgres(conn, pg['schema']['production'])
        self.data_manager = DataManager(post)
        self.tag_matcher = TagMatcher(
            post, await post.get_tags())
        info('Connected to database: {}.{}'.format(
            pg['database'], pg['schema']['production']))

    async def on_ready(self):
        """
        Event for the bot is ready
        """
        g = '{}help'.format(self.default_prefix)
        info('Logged in as ' + self.user.name + '#' + self.user.discriminator)
        info('Bot ID: ' + self.user.id)
        self.mention_normal = '<@{}>'.format(self.user.id)
        self.mention_nick = '<@!{}>'.format(self.user.id)
        self.session_manager = SessionManager(ClientSession(), self.logger)

        async def __change_presence():
            try:
                await self.wait_until_ready()
                await self.change_presence(game=Game(name=g))
            except ConnectionClosed as e:
                self.logger.warning(str(e))
                await self.logout()
                await self.login()
                await __change_presence()

        await __change_presence()
        if self.config['Bot']['console logging']:
            self.logger.addHandler(get_console_handler())

    async def on_command_error(self, exception, context):
        """
        Custom command error handling
        :param exception: the expection raised
        :param context: the context of the command
        """
        localize = await self.get_language_dict(context)
        handled_exceptions = (
            CommandOnCooldown, NsfwError, BadWordError, ManageRoleError,
            AdminError, ManageMessageError, MissingRequiredArgument, OwnerError,
            BadArgument
        )
        if isinstance(exception, handled_exceptions):
            await self.send_message(
                context.message.channel,
                command_error_handler(localize, exception)
            )
        elif isinstance(exception, CommandNotFound):
            # Ignore this case
            return
        else:
            try:
                raise exception
            except Exception as e:
                tb = traceback.format_exc()
                triggered = context.message.content
                ex_type = type(e).__name__
                four_space = ' ' * 4
                str_ex = str(e)
                msg = '\n{0}Triggered message: {1}\n' \
                      '{0}Type: {2}\n' \
                      '{0}Exception: {3}\n\n{4}' \
                    .format(four_space, triggered, ex_type, str_ex, tb)
                self.logger.log(WARNING, msg)
                await self.send_message(
                    context.message.channel,
                    localize['ex_warn'].format(
                        triggered, ex_type, str_ex
                    )
                )

    async def on_error(self, event_method, *args, **kwargs):
        """
        General error handling for discord
        Check :func:`discord.on_error` for more details.
        """
        ig = 'Ignoring exception in {}\n'.format(event_method)
        tb = traceback.format_exc()
        self.logger.log(ERROR, '\n' + ig + '\n' + tb)

        try:
            ctx = args[1]
            localize = await self.get_language_dict(ctx)
            await self.send_message(
                ctx.message.channel,
                localize['ex_error'].format(ig + tb)
            )
        except HTTPException:
            pass
        except Exception as e:
            msg = str(e) + '\n' + str(tb)
            self.logger.log(CRITICAL, msg)
            # FIXME Remove cast to str after lib rewrite
            for dev in [await self.get_user_info(str(i))
                        for i in self.config['Bot']['owners']]:
                await self.send_message(
                    dev,
                    'An exception ocurred while the '
                    'bot was running. For help, check '
                    '"Troubleshooting" section in '
                    'documentation, come to our support '
                    'server or open an issue in Git repo.'
                    "\n```py\n" + msg + "```"
                )

    async def process_commands(self, message):
        """
        Overwrites the process_commands method
        to provide command black list support.
        Check :func:`Bot.process_commands` for more details.
        """
        if message.author.bot:
            return
        prefix = await get_prefix(self, message)
        name = message.content.split(' ')[0][len(prefix):]
        # TODO Implement command black list
        await super().process_commands(message)

    async def start_bot(self, cogs: list):
        """
        Start the bot
        :param cogs: a list of cogs
        """
        # TODO remove default help when custom help is finished
        # self.remove_command('help')
        for cog in cogs:
            self.add_cog(cog)
        await self.set_postgres()
        await self.start(self.config['Bot']['token'])

    async def get_language_dict(self, ctx_msg) -> dict:
        """
        Get the language of the given context
        :param ctx_msg: the discord context object, or a message object
        :return: the language dict
        :rtype: dict
        """
        return self.language[await self.get_language_key(ctx_msg)]

    async def get_language_key(self, ctx_msg):
        """
        Get the language key of the context
        :param ctx_msg: the discord context object, or a message object
        :return: the language key
        """
        if isinstance(ctx_msg, Context):
            message = ctx_msg.message
        elif isinstance(ctx_msg, Message):
            message = ctx_msg
        else:
            raise TypeError
        channel = message.channel
        if channel.type == ChannelType.text:
            lan = await self.data_manager.get_language(int(message.server.id))
            return lan or self.default_language
        else:
            return self.default_language
