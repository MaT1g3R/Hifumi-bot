from json import loads

from aiohttp import ClientResponseError
from discord.embeds import Embed
from discord.ext import commands
from imdbpie import Imdb

from bot import Hifumi
from core.utilities_core import imdb, number_fact, recipe_search
from data_controller.data_utils import get_prefix


class Utilities:
    """
    Class for Utilities/Search commands
    """
    __slots__ = ['bot', 'imdb_api']

    def __init__(self, bot: Hifumi):
        """
        Initialize the Utilities class
        :param bot: the bot object
        """
        self.bot = bot
        self.imdb_api = Imdb()

    @commands.command(pass_context=True)
    async def advice(self, ctx):
        """
        Say a random advice lol
        """
        localize = self.bot.get_language_dict(ctx)
        url = 'http://api.adviceslip.com/advice'
        try:
            resp = await self.bot.session_manager.get(url)
            resp = await resp.read()
            slip = loads(resp)['slip']
            res = ':information_source: **Advice #{}**: {}'.format(
                slip['slip_id'], slip['advice']
            )
        except ClientResponseError:
            res = localize['api_error'].format('Adviceslip')
        await self.bot.say(res)

    @commands.group(pass_context=True)
    async def fact(self, ctx):
        """
        Command group for all the facts commands. If no subcommand is invoked
        the bot will say the list of subcommands.

        :param ctx: the discord context
        """
        if ctx.invoked_subcommand is None:
            localize = self.bot.get_language_dict(ctx)
            await self.bot.say(
                localize['fact_list'].format(
                    get_prefix(self.bot, ctx.message),
                    '\n'.join(tuple(self.fact.commands.keys()))
                )
            )

    @fact.command(pass_context=True)
    async def cat(self, ctx):
        """
        Say a random cat fact
        """
        localize = self.bot.get_language_dict(ctx)
        url = 'http://catfacts-api.appspot.com/api/facts'
        try:
            resp = await self.bot.session_manager.get(url)
            resp = await resp.read()
            res = loads(resp)['facts'][0]
        except ClientResponseError:
            res = localize['api_error'].format('Catfacts')
        await self.bot.say(res)

    @fact.command(pass_context=True)
    @commands.cooldown(rate=1, per=1)
    async def number(self, ctx, num=None):
        """
        Display a fact about a number, random if number is not provided
        :param ctx: the discord context
        :param num: the number
        """
        localize = self.bot.get_language_dict(ctx)
        num = 'random' if num is None else num
        res = await number_fact(num, localize, self.bot.session_manager)
        await self.bot.say(res)

    @commands.command(pass_context=True)
    async def imdb(self, ctx, *query):
        """
        Search imdb for a movie
        :param ctx: the discord context
        :param query: the search query
        """
        res = await imdb(
            ' '.join(query), self.imdb_api,
            self.bot.get_language_dict(ctx)
        )
        if isinstance(res, Embed):
            await self.bot.say(embed=res)
        else:
            await self.bot.say(res)

    @commands.command(pass_context=True)
    async def recipe(self, ctx, *query):
        """
        Search for a recipe
        :param ctx: the discord context
        :param query: the search query
        """
        e = self.bot.config['API keys']['edamam']
        res = await recipe_search(
            ' '.join(query),
            self.bot.get_language_dict(ctx),
            str(e['app id']),
            str(e['key']),
            self.bot.session_manager
        )
        if isinstance(res, Embed):
            await self.bot.say(embed=res)
        else:
            await self.bot.say(res)

    @commands.command(pass_context=True)
    async def remindme(self, ctx, t):
        """
        Set a reminder and notify the user when time is up
        """
        raise NotImplementedError

    @commands.command()
    async def strawpoll(self):
        raise NotImplementedError

    @commands.command()
    async def time(self):
        raise NotImplementedError

    @commands.command()
    async def twitch(self):
        raise NotImplementedError

    @commands.command()
    async def urban(self):
        raise NotImplementedError

    @commands.command()
    async def weather(self):
        raise NotImplementedError

    @commands.command()
    async def avatar(self):
        raise NotImplementedError
    
    @commands.command()
    async def serverinfo(self):
        raise NotImplementedError
    
    @commands.command()
    async def userinfo(self):
        raise NotImplementedError

    @commands.command()
    async def anime(self):
        raise NotImplementedError
        
    @commands.command()
    async def manga(self):
        raise NotImplementedError
        
    @commands.command()
    async def osu(self):
        raise NotImplementedError
        
    @commands.command()
    async def checkpp(self):
        raise NotImplementedError
