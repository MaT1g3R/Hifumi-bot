"""
Cog for bot info
"""
import time

from discord.ext import commands

from config.settings import INVITE, SUPPORT, WEBSITE, TWITTER
from core.bot_info_core import build_info_embed
from core.language_support import generate_language_entry, \
    generate_language_list


class BotInfo:
    __slots__ = ['bot']

    def __init__(self, bot):
        """
        Initialized the BotInfo class
        :param bot: the bot object
        """
        self.bot = bot

    @commands.command(pass_context=True)
    async def info(self, ctx):
        """
        Displays the bot info
        """
        await self.bot.say(embed=build_info_embed(ctx, self.bot))

    @commands.command(pass_context=True)
    async def support(self, ctx):
        """
        Says the support server for the bot
        """
        base = self.bot.get_language_dict(ctx)['support']
        await self.bot.say(base.format(SUPPORT, TWITTER, WEBSITE))

    @commands.command(pass_context=True)
    async def donate(self, ctx):
        """
        Display the donate message
        """
        await self.bot.say(self.bot.get_language_dict(ctx)['donate'])

    @commands.command(pass_context=True)
    async def git(self, ctx):
        """
        Display the git repo
        """
        await self.bot.say(self.bot.get_language_dict(ctx)['git'])

    @commands.command(pass_context=True)
    async def help(self, ctx):
        """
        help command
        """
        await self.bot.say('Coming Soon' + str(ctx))

    @commands.command()
    async def ping(self):
        """
        ping command
        """
        start_time = int(round(time.time() * 1000))
        msg = await self.bot.say('Pong! :hourglass:')
        end_time = int(round(time.time() * 1000))
        await self.bot.edit_message(
            msg, 'Pong! | :timer: {}ms'.format(end_time - start_time))

    @commands.command(pass_context=True)
    async def invite(self, ctx):
        """
        Display invite link
        """
        await self.bot.say(
            self.bot.get_language_dict(ctx)['invite'].format(INVITE))

    @commands.command(pass_context=True, no_pm=True)
    async def language(self, ctx):
        """
        Get the language of the server
        :param ctx: the context
        """
        localize = self.bot.get_language_dict(ctx)
        await self.bot.say(
            localize['language'].format(
                generate_language_entry(localize['language_data'])
            )
        )

    @commands.command(pass_context=True)
    async def languagelist(self, ctx):
        """
        Get a list of languages
        :param ctx: the discord context
        """
        await self.bot.say(generate_language_list(
            self.bot.language, self.bot.get_language_key(ctx))
        )
