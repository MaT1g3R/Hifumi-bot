from asyncio import sleep
from json import loads

from discord.embeds import Embed
from discord.ext import commands
from imdbpie import Imdb
from requests import get

from core.utilities_core import number_fact, imdb, recipe_search
from scripts.discord_functions import get_prefix
from shell import Hifumi


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

    @commands.group(pass_context=True)
    async def fact(self, ctx):
        """
        Command group for all the facts commands. If no subcommand is invoked
        the bot will say the list of subcommands.

        :param ctx: the discord context
        """
        if ctx.invoked_subcommand is None:
            await self.bot.say(
                self.bot.get_language_dict(ctx)['fact_list'].format(
                    get_prefix(
                        self.bot.cur, ctx.message.server,
                        self.bot.default_prefix
                    ),
                    '\n'.join(tuple(self.fact.commands.keys()))
                )
            )

    @fact.command()
    async def cat(self):
        """
        Say a random cat fact
        """
        await self.bot.say(
            get('http://catfacts-api.appspot.com/api/facts').json()['facts'][0]
        )

    @fact.command(pass_context=True)
    @commands.cooldown(rate=1, per=1)
    async def number(self, ctx, num=None):
        """
        Display a fact about a number, random if number is not provided
        :param ctx: the discord context
        :param num: the number
        """
        localize = self.bot.get_language_dict(ctx)
        header = localize['num_fact_random'] if num is None \
            else localize['num_fact_found']
        num = 'random' if num is None else num
        await self.bot.say(
            number_fact(
                num, localize['num_fact_not_found'],
                localize['num_fact_str'], header
            )
        )

    @commands.command(pass_context=True)
    async def imdb(self, ctx, *query):
        """
        Search imdb for a movie
        :param ctx: the discord context
        :param query: the search query
        """
        res = imdb(
            ' '.join(query), self.imdb_api, self.bot.get_language_dict(ctx)
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
        res = recipe_search(' '.join(query), self.bot.get_language_dict(ctx))
        if isinstance(res, Embed):
            await self.bot.say(embed=res)
        else:
            await self.bot.say(res)

    @commands.command(pass_context=True)
    async def remindme(self, ctx, t):
        """
        Set a reminder and notify the user when time is up
        """
        t = int(t)
        await sleep(t)
        await self.bot.say(ctx)
        await self.bot.say(t)

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
