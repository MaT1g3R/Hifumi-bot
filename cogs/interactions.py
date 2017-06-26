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
    async def cry(self):
        raise NotImplementedError

    @commands.command()
    async def cuddle(self):
        raise NotImplementedError
    
    @commands.command()
    async def hug(self):
        raise NotImplementedError

    @commands.command()
    async def kiss(self):
        raise NotImplementedError

    @commands.command()
    async def lick(self):
        raise NotImplementedError

    @commands.command()
    async def eat(self):
        raise NotImplementedError

    @commands.command()
    async def pat(self):
        raise NotImplementedError

    @commands.command()
    async def pout(self):
        raise NotImplementedError

    @commands.command()
    async def slap(self):
        raise NotImplementedError
    
    @commands.command()
    async def stare(self):
        raise NotImplementedError

    @commands.command()
    async def tickle(self):
        raise NotImplementedError

    @commands.command()
    async def smug(self):
        raise NotImplementedError
        
    @commands.command()
    async def lewd(self):
        raise NotImplementedError
