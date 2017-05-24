import time

from discord.ext import commands

from config import *
from core.bot_info_core import build_info_embed
from core.checks import is_admin
from core.data_controller import set_prefix_, delete_prefix_
from core.discord_functions import get_prefix
from core.language_support import generate_language_entry, \
    generate_language_list, set_language
from shell import Hifumi


class BotInfo:
    """
    Cog for bot info
    """
    __slots__ = ['bot']

    def __init__(self, bot: Hifumi):
        """
        Initialized the BotInfo class
        :param bot: the bot object
        """
        self.bot = bot

    @commands.command(pass_context=True)
    async def info(self, ctx):
        """
        Displays the bot info
        :param ctx: the discord context object
        """
        await self.bot.say(embed=build_info_embed(ctx, self.bot))

    @commands.command(pass_context=True)
    async def support(self, ctx):
        """
        Says the support server for the bot
        :param ctx: the discord context object
        """
        base = self.bot.get_language_dict(ctx)['support']
        await self.bot.say(base.format(SUPPORT, TWITTER, WEBSITE))

    @commands.command(pass_context=True)
    async def donate(self, ctx):
        """
        Display the donate message
        :param ctx: the discord context object
        """
        await self.bot.say(self.bot.get_language_dict(ctx)['donate'])

    @commands.command(pass_context=True)
    async def git(self, ctx):
        """
        Display the git repo
        :param ctx: the discord context object
        """
        await self.bot.say(self.bot.get_language_dict(ctx)['git'])

    # TODO Finish help command
    # @commands.command(pass_context=True)
    # async def help(self, ctx):
    #     """
    #     help command
    #     :param ctx: the discord context object
    #     """
    #     await self.bot.say('Coming Soon' + str(ctx))

    @commands.command()
    async def ping(self):
        """
        ping command
        """
        start_time = time.time()
        msg = await self.bot.say('Pong! :hourglass:')
        end_time = time.time()
        await self.bot.edit_message(
            msg, 'Pong! | :timer: {}ms'.format(
                round((end_time - start_time) * 1000))
        )

    @commands.command(pass_context=True)
    async def invite(self, ctx):
        """
        Display the invite link
        :param ctx: the discord context object
        """
        await self.bot.say(
            self.bot.get_language_dict(ctx)['invite'].format(INVITE))

    @commands.group(pass_context=True, no_pm=True)
    async def language(self, ctx):
        """
        Get the language of the server
        :param ctx: the discord context object
        """
        if ctx.invoked_subcommand is None:
            localize = self.bot.get_language_dict(ctx)
            await self.bot.say(
                localize['language'].format(
                    generate_language_entry(localize['language_data']),
                    get_prefix(
                        self.bot.cur,
                        ctx.message.server, self.bot.default_prefix
                    ),
                    self.bot.default_language
                )
            )

    @language.command(pass_context=True)
    async def list(self, ctx):
        """
        Display a list of languages
        :param ctx: the discord context object
        """
        await self.bot.say(generate_language_list(
            self.bot.language, self.bot.get_language_key(ctx))
        )

    @language.command(pass_context=True, no_pm=True, name='set')
    @commands.check(is_admin)
    async def l_set(self, ctx, language: str = None):
        """
        Set the language for the server
        :param ctx: the discord context object
        :param language: the language to set to
        """
        localize = self.bot.get_language_dict(ctx)
        if language not in self.bot.language or language is None:
            await self.bot.say(
                localize['lan_no_exist'].format(
                    language,
                    get_prefix(
                        self.bot.cur, ctx.message.server,
                        self.bot.default_prefix
                    )
                )
            )
        else:
            await self.bot.say(set_language(self.bot, ctx, language))

    @language.command(pass_context=True, no_pm=True, name='reset')
    @commands.check(is_admin)
    async def l_reset(self, ctx):
        """
        Reset the language for the current server
        :param ctx: the discord context
        """
        await self.bot.say(
            set_language(self.bot, ctx, self.bot.default_language, True)
        )

    @commands.group(pass_context=True, no_pm=True)
    async def prefix(self, ctx):
        """
        Show the prefix for the current server
        :param ctx: the discord context
        """
        if ctx.invoked_subcommand is None:
            await self.bot.say(
                self.bot.get_language_dict(ctx)['prefix'].format(
                    get_prefix(
                        self.bot.cur, ctx.message.server,
                        self.bot.default_prefix
                    ),
                    self.bot.default_prefix
                )
            )

    @prefix.command(pass_context=True, no_pm=True, name='set')
    @commands.check(is_admin)
    async def p_set(self, ctx, prefix: str):
        """
        Set the prefix for the server
        :param ctx: the discord context object
        :param prefix: the prefix to set to
        """
        localize = self.bot.get_language_dict(ctx)
        if '/' in prefix or '\\' in prefix:
            await self.bot.say(localize['prefix_bad'])
            return
        if prefix.startswith('@') or prefix.startswith('#') \
                or prefix.startswith('<@'):
            await self.bot.say(localize['prefix_bad_start'])
            return
        set_prefix_(self.bot.conn, self.bot.cur, ctx.message.server.id, prefix)
        await self.bot.say(localize['set_prefix_'].format(prefix))

    @prefix.command(pass_context=True, no_pm=True, name='reset')
    @commands.check(is_admin)
    async def p_reset(self, ctx):
        """
        Reset the prefix of the server
        :param ctx: the discord context
        """
        delete_prefix_(self.bot.conn, self.bot.cur, ctx.message.server.id)
        await self.bot.say(
            self.bot.get_language_dict(ctx)['set_prefix_'].format(
                self.bot.default_prefix
            )
        )
