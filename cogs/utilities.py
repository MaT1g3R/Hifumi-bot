from json import loads

from discord.ext import commands
from requests import get

from shell.hifumi import Hifumi


class Utilities:
    """
    Class for Utilities/Search commands
    """
    __slots__ = ['bot']

    def __init__(self, bot: Hifumi):
        """
        Initialize the Utilities class
        :param bot: the bot object
        """
        self.bot = bot

    @commands.command()
    async def advice(self):
        """
        Say a random advice lol
        """
        slip = loads(get('http://api.adviceslip.com/advice').content)['slip']
        await self.bot.say(
            ':information_source: **Advice #{}**: {}'.format(
                slip['slip_id'], slip['advice']
            )
        )

    @commands.group()
    async def fact(self):
        pass

    @fact.command()
    async def cat(self):
        pass

    @fact.command()
    async def dog(self):
        pass

    @fact.command()
    async def number(self):
        pass

    @commands.command()
    async def imdb(self):
        pass

    @commands.command()
    async def remindme(self):
        pass

    @commands.command()
    async def strawpoll(self):
        pass

    @commands.command()
    async def time(self):
        pass

    @commands.command()
    async def twitch(self):
        pass

    @commands.command()
    async def urban(self):
        pass

    @commands.command()
    async def weather(self):
        pass

    @commands.command()
    async def yesno(self):
        pass
