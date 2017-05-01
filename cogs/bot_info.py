"""
Cog for bot info
"""
from discord.ext import commands
from core.bot_info_core import build_info_embed


class BotInfo:

    def __init__(self, bot):
        """
        Initialized the BotInfo class
        :param bot: the bot object
        """
        self.bot = bot

    @commands.command()
    async def info(self):
        """
        Displays the bot info
        :return: 
        """
        await self.bot.say(embed=build_info_embed(self.bot))

    @commands.command()
    async def support(self):
        pass

    @commands.command()
    async def donate(self):
        pass

    @commands.command()
    async def git(self):
        pass

    @commands.command()
    async def help(self):
        pass

    @commands.command()
    async def ping(self):
        pass

    @commands.command()
    async def invite(self):
        pass
