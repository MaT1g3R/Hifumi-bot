import time

from discord.ext import commands

from bot import Hifumi
from core.bot_info_core import build_info_embed
from data_controller.data_utils import get_prefix, set_language
from scripts.checks import is_admin
from scripts.language_support import generate_language_entry, \
    generate_language_list


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
        await self.bot.say(embed=await build_info_embed(ctx, self.bot))

    @commands.command(pass_context=True)
    async def support(self, ctx):
        """
        Says the support server for the bot
        :param ctx: the discord context object
        """
        base = self.bot.get_language_dict(ctx)['support']
        f = lambda s: str(self.bot.config['Bot extra'][s])
        await self.bot.say(
            base.format(f('support'), f('twitter'), f('website')))

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
            self.bot.get_language_dict(ctx)['invite'].format(
                self.bot.config['Bot extra']['invite']
            )
        )

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
                    get_prefix(self.bot, ctx.message),
                    self.bot.default_language
                )
            )

    @language.command(pass_context=True)
    async def list(self, ctx):
        """
        Display a list of languages
        :param ctx: the discord context object
        """
        await self.bot.say(
            generate_language_list(
                self.bot.language, await self.bot.get_language_key(ctx)
            )
        )

    async def __set_language(self, ctx, language):
        """
        Helper method to set the language of a guild.
        :param ctx: the discord context.
        :param language: the language to set to.
        """
        localize = self.bot.get_language_dict(ctx)
        if language not in self.bot.language:
            await self.bot.say(
                localize['lan_no_exist'].format(
                    language,
                    get_prefix(self.bot, ctx.message)
                )
            )
        else:
            await self.bot.say(
                await set_language(self.bot, ctx, language)
            )

    @language.command(pass_context=True, no_pm=True, name='set')
    @commands.check(is_admin)
    async def l_set(self, ctx, language: str = None):
        """
        Set the language for the server
        :param ctx: the discord context object
        :param language: the language to set to
        """
        await self.__set_language(ctx, language)

    @language.command(pass_context=True, no_pm=True, name='reset')
    @commands.check(is_admin)
    async def l_reset(self, ctx):
        """
        Reset the language for the current server
        :param ctx: the discord context
        """
        await self.__set_language(ctx, self.bot.default_language)

    @commands.group(pass_context=True, no_pm=True)
    async def prefix(self, ctx):
        """
        Show the prefix for the current server
        :param ctx: the discord context
        """
        if ctx.invoked_subcommand is None:
            localize = self.bot.get_language_dict(ctx)
            await self.bot.say(
                localize['prefix'].format(
                    get_prefix(self.bot, ctx.message),
                    self.bot.default_prefix
                )
            )

    async def __set_prefix(self, ctx, prefix: str):
        """
        Helper method to set the prefix of a guild.
        :param ctx: the discord context.
        :param prefix: the prefix to set to.
        """
        localize = self.bot.get_language_dict(ctx)
        if not prefix:
            await self.bot.say(localize['prefix_empty'])
            return
        if '/' in prefix or '\\' in prefix:
            await self.bot.say(localize['prefix_bad'])
            return
        if prefix.startswith('@') or prefix.startswith('#') \
                or prefix.startswith('<@'):
            await self.bot.say(localize['prefix_bad_start'])
            return
        await self.bot.data_manager.set_prefix(
            int(ctx.message.server.id), prefix
        )
        await self.bot.say(localize['set_prefix'].format(prefix))

    @prefix.command(pass_context=True, no_pm=True, name='set')
    @commands.check(is_admin)
    async def p_set(self, ctx, prefix: str = None):
        """
        Set the prefix for the server
        :param ctx: the discord context object
        :param prefix: the prefix to set to
        """
        await self.__set_prefix(ctx, prefix)

    @prefix.command(pass_context=True, no_pm=True, name='reset')
    @commands.check(is_admin)
    async def p_reset(self, ctx):
        """
        Reset the prefix of the server
        :param ctx: the discord context
        """
        localize = self.bot.get_language_dict(ctx)
        await self.bot.data_manager.set_prefix(
            int(ctx.message.server.id), None
        )
        prefix = get_prefix(self.bot, ctx.message)
        await self.bot.say(localize['set_prefix'].format(prefix))
