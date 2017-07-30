from discord.ext import commands

from json import load
from random import choice
from pathlib import Path

class Fun:
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

    @commands.command(name='8ball', pass_context=True)
    async def _8ball(self, ctx, *question):
        localize = self.bot.localize(ctx)
        if not question:
            await self.bot.say(localize['8ball_no_question'])
        else:
            await self.bot.say(localize['8ball'].format(
                                      ' '.join(question), 
                       choice(localize['8ball_answers']))
                              )
            
    @commands.command()
    async def accordingtodevin(self):
        raise NotImplementedError

    @commands.command()
    async def choose(self):
        raise NotImplementedError

    @commands.command()
    async def coinflip(self):
        raise NotImplementedError

    @commands.command()
    async def animal(self):
        raise NotImplementedError

    @commands.command()
    async def joke(self):
        raise NotImplementedError

    @commands.command()
    async def garfield(self):
        raise NotImplementedError

    @commands.command()
    async def gif(self):
        raise NotImplementedError

    @commands.command()
    async def imgur(self):
        raise NotImplementedError

    @commands.command(pass_context=True)
    async def hifumi(self, ctx):
        """
        Display a random Hifumi GIF
        """
        try:
            __data_path = Path(__file__).parent.parent.joinpath('data')
            with open(__data_path.joinpath('hifumi.json')) as data_file:    
                data = load(data_file)
                await self.bot.say(choice(data))
        except Exception:
            localize = self.bot.localize(ctx)
            await self.bot.say(localize['hifumi_shy'])
            
    @commands.command()
    async def love(self):
        raise NotImplementedError

    @commands.command()
    async def meme(self):
        raise NotImplementedError

    @commands.command()
    async def rate(self):
        raise NotImplementedError

    @commands.command()
    async def reverse(self):
        raise NotImplementedError

    @commands.command()
    async def rip(self):
        raise NotImplementedError

    @commands.command()
    async def roll(self):
        raise NotImplementedError

    @commands.command()
    async def rps(self):
        raise NotImplementedError

    @commands.command()
    async def say(self):
        raise NotImplementedError

    @commands.command()
    async def sayd(self):
        raise NotImplementedError

    @commands.command()
    async def triggered(self):
        raise NotImplementedError

    @commands.command()
    async def xkcd(self):
        raise NotImplementedError

    @commands.command()
    async def yomomma(self):
        raise NotImplementedError
