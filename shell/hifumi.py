"""
The Hifumi bot object
"""
import time
import traceback
from asyncio import coroutine
from logging import WARNING, ERROR, CRITICAL
from os.path import join
from threading import Timer

from discord import ChannelType, Message
from discord.ext.commands import Bot, CommandOnCooldown, Context
from discord.ext.commands.errors import MissingRequiredArgument, CommandNotFound
from discord.game import Game

from config.settings import DEFAULT_PREFIX, SHARDED, DATA_CONTROLLER, \
    ENABLE_CONSOLE_LOGGING
from config.settings import OWNER
from core.bot_info_core import generate_shard_info
from core.checks import NsfwError, BadWordError, ManageRoleError, AdminError, \
    ManageMessageError
from core.discord_functions import command_error_handler
from core.file_io import write_json
from core.language_support import read_language
from core.logger import setup_logging, get_console_handler, info


class Hifumi(Bot):
    """
    The Hifumi bot class
    """
    __slots__ = ['default_prefix', 'shard_id', 'shard_count', 'start_time',
                 'language', 'default_language', 'logger', 'mention_normal',
                 'mention_nick', 'working_dir']

    def __init__(self, prefix, shard_count=1, shard_id=0,
                 default_language='en', working_dir=''):
        """
        Initialize the bot object
        :param prefix: the function to get prefix for a server
        :param shard_count: the shard count, default is 1
        :param shard_id: shard id, default is 0
        :param default_language: the default language of the bot, default is en
        :param working_dir: the working directory for the bot, dont change this
        unless you know what you are doing
        """
        super().__init__(command_prefix=prefix, shard_count=shard_count,
                         shard_id=shard_id)
        self.default_prefix = DEFAULT_PREFIX
        self.shard_id = shard_id
        self.shard_count = shard_count
        self.start_time = int(time.time())
        self.language = read_language(join(working_dir, 'data', 'language'))
        self.default_language = default_language
        self.logger = setup_logging(
            self.start_time, join(working_dir, 'data', 'logs')
        )
        self.mention_normal = ''
        self.mention_nick = ''
        self.working_dir = working_dir

    @coroutine
    async def on_ready(self):
        """
        Event for the bot is ready
        """
        g = '{}help'.format(self.default_prefix)
        if SHARDED:
            g = '{}/{} | '.format(self.shard_id + 1, self.shard_count) + g
        info('Logged in as ' + self.user.name + '#' + self.user.discriminator)
        info('Bot ID: ' + self.user.id)
        self.mention_normal = '<@{}>'.format(self.user.id)
        self.mention_nick = '<@!{}>'.format(self.user.id)
        await self.change_presence(game=Game(name=g))
        if SHARDED:
            self.update_shard_info()
        if ENABLE_CONSOLE_LOGGING:
            self.logger.addHandler(get_console_handler())

    @coroutine
    async def on_command_error(self, exception, context):
        """
        Custom command error handling
        :param exception: the expection raised
        :param context: the context of the command
        """
        handled_exceptions = (
            CommandOnCooldown, NsfwError, BadWordError, ManageRoleError,
            AdminError, ManageMessageError, MissingRequiredArgument
        )
        if ('Member' in str(exception) and 'not found' in str(exception)) \
                or isinstance(exception, handled_exceptions):
            await self.send_message(
                context.message.channel,
                command_error_handler(self, exception, context)
            )
        elif isinstance(exception, CommandNotFound):
            # Ignore this case
            return
        else:
            triggered = context.message.content
            ex_type = type(exception).__name__
            four_space = ' ' * 4
            str_ex = str(exception)
            msg = '\n{0}Triggered message: {1}\n' \
                  '{0}Type: {2}\n' \
                  '{0}Exception: {3}' \
                .format(four_space, triggered, ex_type, str_ex)
            self.logger.log(WARNING, msg)
            await self.send_message(
                context.message.channel,
                self.get_language_dict(context)['ex_warn'].format(
                    triggered, ex_type, str_ex
                )
            )

    @coroutine
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
            await self.send_message(
                ctx.message.channel,
                self.get_language_dict(ctx)['ex_error'].format(ig + tb)
            )
        except Exception as e:
            msg = str(e) + '\n' + str(tb)
            self.logger.log(CRITICAL, msg)
            for dev in [await self.get_user_info(i) for i in OWNER]:
                await self.send_message(dev, msg)

    def start_bot(self, cogs: list, token):
        """
        Start the bot
        :param cogs: a list of cogs
        :param token: the bot token
        """
        # TODO remove default help when custom help is finished
        # self.remove_command('help')
        for cog in cogs:
            self.add_cog(cog)
        self.run(token)

    def get_language_dict(self, ctx_msg):
        """
        Get the language of the given context
        :param ctx_msg: the discord context object, or a message object
        :return: the language dict
        :rtype: dict
        """
        return self.language[self.get_language_key(ctx_msg)]

    def get_language_key(self, ctx_msg):
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
            lan = DATA_CONTROLLER.get_language(message.server.id)
            return lan if lan is not None else self.default_language
        else:
            return self.default_language

    def update_shard_info(self):
        """
        Updates the bot shard info every second
        """
        Timer(1, self.update_shard_info).start()
        file_name = join(self.working_dir, 'data', 'shard_info',
                         'shard_{}.json'.format(self.shard_id))
        content = generate_shard_info(self)
        write_json(open(file_name, 'w+'), content)
