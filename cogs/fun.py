from discord.ext import commands

from bot import Hifumi
from core.fun_core import *

class Fun:
    """
    Fun cog
    """
    __slots__ = ['bot']

    def __init__(self, bot: Hifumi):
        """
        Initialize the Fun class
        :param bot: the discord bot object
        """
        self.bot = bot
        
    @commands.command(pass_context=True)
    async def foo(self, ctx):
        """
        Lorem ipsum
        :param ctx: the discord context object
        """
        pass
