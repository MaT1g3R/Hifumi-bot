"""
The Hifumi bot object
"""
from pathlib import Path
from time import time
from traceback import format_exc
from typing import Union

from aiohttp import ClientSession
from discord import Message
from discord.ext.commands import AutoShardedBot, Context

from bot.hifumi_functions import (get_data_manager, handle_error)
from bot.session_manager import SessionManager
from config import Config
from core.listen_core import send_traceback
from data_controller import DataManager, TagMatcher
from data_controller.data_utils import get_prefix
from scripts.logger import get_console_handler, setup_logging
from translations.translations import Translation


class Hifumi(AutoShardedBot):
    """
    The Hifumi bot class
    """

    def __init__(self, *,
                 version: str,
                 start_time: int,
                 config: Config,
                 session_manager: SessionManager,
                 tag_matcher: TagMatcher,
                 data_manager: DataManager,
                 logger,
                 emojis: list):
        """
        Initialize an instance of this bot.
        :param start_time: the start time.
        :param config: the Config instance.
        :param session_manager: the SessionManager instance.
        :param tag_matcher: the TagMatcher instance.
        :param data_manager: the DataManager instance.
        :param logger: the logger.
        :param emojis: the list of emojis.
        """
        self.version = version
        self.config = config
        self.session_manager = session_manager
        self.tag_matcher = tag_matcher
        self.data_manager = data_manager
        self.start_time = start_time
        self.language = Translation()
        self.logger = logger
        self.all_emojis = emojis
        self.mention_regex = None
        self.mention_msg_regex = None
        super().__init__(command_prefix=get_prefix)

    @classmethod
    async def get_bot(cls):
        """
        Get an instance of the bot.
        :return: an instance of the bot.
        """
        data_path = Path(Path(__file__).parent.parent.joinpath('data'))
        config = Config()
        log_path = data_path.joinpath('logs')
        start_time = int(time())
        with data_path.joinpath('emojis.txt').open() as f:
            all_emojis = f.read().splitlines()
        logger = setup_logging(start_time, log_path)
        if config['Bot']['console logging']:
            logger.addHandler(get_console_handler())
        session_manager = SessionManager(ClientSession(), logger)
        data_manager, tag_matcher = await get_data_manager(
            config.postgres(), logger
        )
        return cls(
            start_time=start_time, config=config,
            session_manager=session_manager, tag_matcher=tag_matcher,
            data_manager=data_manager, logger=logger,
            emojis=all_emojis
        )

    @property
    def default_prefix(self):
        return self.config['Bot']['prefix']

    @property
    def client_id(self):
        return self.user.id

    @property
    def mention_normal(self):
        return '<@{}>'.format(self.client_id)

    @property
    def mention_nick(self):
        return '<@!{}>'.format(self.client_id)

    async def on_error(self, event_method, *args, **kwargs):
        """
        General error handling for discord
        Check :func:`discord.Client.on_error` for more details.
        """
        tb = format_exc()
        lvl, log_msg, header, ctx = handle_error(
            tb, event_method, *args, **kwargs
        )
        if ctx:
            await ctx.send(self.translate(ctx, 'sentence', 'ex_error'))
        self.logger.log(lvl, log_msg)
        await send_traceback(
            self.get_channel(self.config['Bot']['error log']), header, tb
        )

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

    def start_bot(self, cogs):
        """
        Start the bot.
        """
        # TODO remove default help when custom help is finished
        # bot.remove_command('help')
        for cog in cogs:
            self.add_cog(cog)
        self.run(self.config['Bot']['token'])

    def lan(self, ctx_msg: Union[Context, Message]) -> str:
        """
        Get the language key of the context
        :param ctx_msg: the discord context object, or a message object
        :return: the language key
        """
        try:
            return self.data_manager.get_language(ctx_msg.guild.id)
        except (TypeError, AttributeError):
            return 'en'

    def translate(self, ctx_msg: Union[Context, Message], file, key) -> str:
        return self.language.get(self.lan(ctx_msg), file, key)
