"""
NSFW cog
"""
from discord.ext import commands


class Nsfw:
    def __init__(self, bot):
        """
        Initialize the Nsfw class
        :param bot: the discord bot object
        """
        self.bot = bot

    @commands.command(pass_context=True)
    def setnsfw(self, ctx, arg):
        """
        Set the nsfw status of the current channel
        :param ctx: 
        :param arg: 
        :return: 
        """
        pass