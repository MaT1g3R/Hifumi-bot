"""
Cog for bot info
"""
import time

from discord.ext import commands

from config.settings import INVITE
from core.bot_info_core import build_info_embed, handle_support


class BotInfo:
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

    @commands.command()
    async def support(self):
        """
        Says the support server for the bot
        """
        await self.bot.say(handle_support())

    @commands.command()
    async def donate(self):
        """
        Display the donate message
        """
        await self.bot.say("Thanks for your generosity! "
                           "Hifumi#8451 and Rem#5307 are alive thanks to "
                           "your help and our dearest contributor (Wolke) help."
                           " If you want to donate, please consider going to "
                           "the following link: "
                           "<http://www.hifumibot.xyz/donate>. "
                           "Once you donate, make sure to DM "
                           "Underforest#1284 with a proof of your donation, "
                           "so you can get a special bonus for you. "
                           "This includes a personal \"thank you\" from Wolke "
                           "and Underforest, Donators role for Hifumi and Rem "
                           "support servers, early beta testing for both bots, "
                           "special Hifumi features for "
                           "donators and so much more.")

    @commands.command()
    async def git(self):
        """
        Display the git repo
        """
        await self.bot.say(
            'Open source can be found here: '
            '<https://github.com/hifumibot/hifumibot>\n'
            'As well as the documentation: <http://hifumibot.xyz/docs>'
        )

    @commands.command()
    async def help(self):
        """
        help command
        """
        await self.bot.say('Coming Soon')

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
