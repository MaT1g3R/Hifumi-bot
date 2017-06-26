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

    @commands.command()
    async def cuddle():
        raise NotImplementedError
    
    @commands.command()
    async def hug():
        raise NotImplementedError

    @commands.command()
    async def kiss():
        raise NotImplementedError

    @commands.command()
    async def lick():
        raise NotImplementedError

    @commands.command()
    async def eat():
        raise NotImplementedError

    @commands.command()
    async def pat():
        raise NotImplementedError

    @commands.command()
    async def pout():
        raise NotImplementedError

    @commands.command()
    async def slap():
        raise NotImplementedError
    
    @commands.command()
    async def stare():
        raise NotImplementedError

    @commands.command()
    async def tickle():
        raise NotImplementedError

    @commands.command()
    async def smug():
        raise NotImplementedError
        
    @commands.command()
    async def lewd():
        raise NotImplementedError
