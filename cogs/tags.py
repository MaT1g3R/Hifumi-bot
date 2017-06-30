from discord.ext import commands


class Tags:
    """
    Tags cog
    """
    __slots__ = ['bot']

    def __init__(self, bot):
        """
        Initialize the Tags class
        :param bot: the discord bot object
        """
        self.bot = bot

    @commands.command()
    async def tag(self):
        raise NotImplementedError
