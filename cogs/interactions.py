from discord.ext import commands

class Interactions:
    """
    Interactions cog
    """
    __slots__ = ['bot']

    def __init__(self, bot):
        """
        Initialize the Interactions class
        :param bot: the discord bot object
        """
        self.bot = bot
    
    @commands.command()
    async def cry():
        raise NotImplementedError

    async def cuddle():
        raise NotImplementedError
        
    async def hug():
        raise NotImplementedError

    async def kiss():
        raise NotImplementedError

    async def lick():
        raise NotImplementedError

    async def eat():
        raise NotImplementedError

    async def pat():
        raise NotImplementedError

    async def pout():
        raise NotImplementedError

    async def slap():
        raise NotImplementedError

    async def stare():
        raise NotImplementedError

    async def tickle():
        raise NotImplementedError
