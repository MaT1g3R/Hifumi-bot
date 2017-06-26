"""
The Hifumi bot object
"""

from logging import CRITICAL, ERROR, WARN
from pathlib import Path
from time import time
from traceback import format_exc
from typing import Union

from aiohttp import ClientSession
from discord import Channel, ChannelType, ConnectionClosed, Game, Message, \
    Object
from discord.ext.commands import Bot, CommandNotFound, \
    Context

from bot.hifumi_functions import command_error_handler, format_command_error, \
    format_traceback, get_data_manager
from bot.session_manager import SessionManager
from config import Config
from data_controller.data_utils import get_prefix
from scripts.discord_functions import get_name_with_discriminator
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

    async def on_ready(self):
        """
        Event for the bot is ready
        """
        await self.try_change_presence(f'{self.default_prefix}help', True)
        info(f'Logged in as {get_name_with_discriminator(self.user)}')
        info('Bot ID: ' + self.user.id)
        self.mention_normal = '<@{}>'.format(self.user.id)
        self.mention_nick = '<@!{}>'.format(self.user.id)
        self.session_manager = SessionManager(ClientSession(), self.logger)
        if self.config['Bot']['console logging']:
            self.logger.addHandler(get_console_handler())

    async def on_command_error(self, exception, context):
        """
        Custom command error handling
        :param exception: the expection raised
        :param context: the context of the command
        """
        if isinstance(exception, CommandNotFound):
            # Ignore this case.
            return
        localize = self.get_language_dict(context)
        channel = context.message.channel
        # FIXME temporary hack
        if 'NotImplementedError' in str(exception):
            s = ("**This command is under construction**\n\n"
                 "As of June 17, 2017, due to technical problems with the "
                 "previous Hifumi version, all commands and databases has been "
                 "wiped and Hifumi was switched to a newer rewrite. "
                 "This command, as many others, will be back soon and we are "
                 "sorry about this. If you wish more information, "
                 "join to our server and check announcements.\n\n"
                 "Cheers from the Hifumi's developer team~")
            await self.send_message(channel, s)
            return
        try:
            res = command_error_handler(localize, exception)
        except Exception as e:
            tb = format_exc()
            msg, triggered = format_command_error(e, context)
            self.logger.log(WARN, f'\n{msg}\n\n{tb}')
            await self.send_message(channel, localize['ex_warn'].format(msg))
            await self.send_traceback(
                tb, f'**WARNING** Triggered message:\n{triggered}')
        else:
            await self.send_message(channel, res)

    async def on_error(self, event_method, *args, **kwargs):
        """
        General error handling for discord
        Check :func:`discord.on_error` for more details.
        """
        ig = 'Ignoring exception in {}\n'.format(event_method)
        tb = format_exc()
        log_msg = f'\n{ig}\n{tb}'
        header = f'**CRITICAL**\n{ig}'
        lvl = CRITICAL
        try:
            ctx = args[1]
            channel = ctx.message.channel
            assert isinstance(ctx, Context)
            assert isinstance(channel, Channel)
        except (IndexError, AssertionError, AttributeError):
            pass
        else:
            header = f'**ERROR**\n{ig}'
            lvl = ERROR
            localize = self.get_language_dict(ctx)
            await self.send_message(channel, localize['ex_error'])
        finally:
            self.logger.log(lvl, log_msg)
            await self.send_traceback(tb, header)

    async def process_commands(self, message):
        """
        Overwrites the process_commands method
        to provide command black list support.
        Check :func:`Bot.process_commands` for more details.
        """
        if message.author.bot:
            return
        prefix = get_prefix(self, message)
        name = message.content.split(' ')[0][len(prefix):]
        # TODO Implement command black list
        await super().process_commands(message)

    async def send_traceback(self, tb, header):
        """
        Send traceback to the error log channel.
        :param tb: the traceback.
        :param header: the header for the error.
        """
        # FIXME Remove cast to str after lib rewrite
        id_ = str(self.config['Bot']['error log'])
        c = Object(id_)
        await self.send_message(c, header)
        for s in format_traceback(tb):
            await self.send_message(c, s)

    async def try_change_presence(self, game: str, retry: bool):
        """
        Try changing presence of the bot.
        :param game: the game name.
        :param retry: True to enable retry. Will log out the bot.
        """
        try:
            await self.wait_until_ready()
            await self.change_presence(game=Game(name=game))
        except ConnectionClosed as e:
            if retry:
                self.logger.log(WARN, str(e))
                await self.logout()
                await self.login(self.config['Bot']['token'])
                await self.try_change_presence(game, retry)
            else:
                raise e

    async def start_bot(self, cogs: list):
        """
        Start the bot
        :param cogs: a list of cogs
        """
        # TODO remove default help when custom help is finished
        # self.remove_command('help')
        for cog in cogs:
            self.add_cog(cog)
        self.data_manager, self.tag_matcher = await get_data_manager(
            self.config.postgres())
        await self.start(self.config['Bot']['token'])

    def get_language_dict(self, ctx_msg) -> dict:
        """
        Get the language of the given context
        :param ctx_msg: the discord context object, or a message object
        :return: the language dict
        :rtype: dict
        """
        return self.language[self.get_language_key(ctx_msg)]

    def get_language_key(self, ctx_msg: Union[Context, Message]):
        """
        Get the language key of the context
        :param ctx_msg: the discord context object, or a message object
        :return: the language key
        """
        if isinstance(ctx_msg, Context):
            message = ctx_msg.message
        else:
            message = ctx_msg

        try:
            type_ = message.channel.type
        except AttributeError:
            return self.default_language
        else:
            if type_ == ChannelType.text:
                lan = self.data_manager.get_language(
                    int(message.server.id))
                return lan or self.default_language
            return self.default_language
