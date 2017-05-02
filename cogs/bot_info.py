"""
Cog for bot info
"""
import time

from discord.ext import commands

from config.settings import INVITE, SUPPORT, WEBSITE, TWITTER
from core.bot_info_core import build_info_embed
from shell.hifumi import Hifumi

class BotInfo:
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

    @commands.command()
    async def invite(self):
        """
        Display invite link
        """
        await self.bot.say(
            "Use this link to invite me to your server:\n"
            "**NOTE: Select all permissions as needed but it's"
            " recommendable to keep enabled all, so I can work fine.**\n"
            "<{}>".format(INVITE)
        )
