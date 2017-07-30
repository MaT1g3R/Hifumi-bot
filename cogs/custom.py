from discord.ext import commands

class Custom:
    """
    Custom cog
    """
    __slots__ = ['bot']

    def __init__(self, bot):
        """
        Initialize the Fun class
        :param bot: the discord bot object
        """
        self.bot = bot

    # Custom commands goes here, please check
    # documentation if you wish to do custom
    # commands for your bot