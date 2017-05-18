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

    @commands.command()
    async def anime(self):
        pass

    @commands.command()
    async def avatar(self):
        pass

    @commands.command()
    async def birthday(self):
        pass

    @commands.command()
    async def fact(self):
        pass

    @commands.command()
    async def catfact(self):
        pass

    @commands.command()
    async def dogfact(self):
        pass

    @commands.command()
    async def numberfact(self):
        pass

    @commands.command()
    async def imdb(self):
        pass

    @commands.command()
    async def manga(self):
        pass

    @commands.command()
    async def nicknames(self):
        pass

    @commands.command()
    async def remindme(self):
        pass

    @commands.command()
    async def serverinfo(self):
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
    async def userinfo(self):
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
