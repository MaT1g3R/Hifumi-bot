import datetime
from asyncio import sleep
from difflib import get_close_matches

from discord.embeds import Embed
from discord.ext import commands
from imdbpie import Imdb
from pytz import all_timezones, timezone

from bot import HTTPStatusError, Hifumi
from core.utilities_core import imdb, number_fact, parse_remind_arg, \
    recipe_search, urban
from data_controller.data_utils import get_prefix
from scripts.helpers import get_time_elapsed


class Utilities:
    """
    Class for Utilities/Search commands
    """
    __slots__ = ['bot', 'imdb_api', 'tzs']

    def __init__(self, bot: Hifumi):
        """
        Initialize the Utilities class
        :param bot: the bot object
        """
        self.bot = bot
        self.imdb_api = Imdb()
        self.tzs = all_timezones

    @commands.command(pass_context=True)
    async def advice(self, ctx):
        """
        Say a random advice lol
        """
        localize = self.bot.localize(ctx)
        url = 'http://api.adviceslip.com/advice'
        try:
            js = await self.bot.session_manager.get_json(url)
            slip = js['slip']
            res = ':information_source: **Advice #{}**: {}'.format(
                slip['slip_id'], slip['advice']
            )
        except HTTPStatusError as e:
            res = localize['api_error'].format('Adviceslip') + f'\n{e}'
        await self.bot.say(res)

    @commands.group(pass_context=True)
    async def fact(self, ctx):
        """
        Command group for all the facts commands. If no subcommand is invoked
        the bot will say the list of subcommands.

        :param ctx: the discord context
        """
        if ctx.invoked_subcommand is None:
            localize = self.bot.localize(ctx)
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
        localize = self.bot.localize(ctx)
        url = 'http://catfacts-api.appspot.com/api/facts'
        try:
            js = await self.bot.session_manager.get_json(url)
            res = js['facts'][0]
        except HTTPStatusError as e:
            res = localize['api_error'].format('Catfacts') + f'\n{e}'
        await self.bot.say(res)

    @fact.command(pass_context=True)
    @commands.cooldown(rate=1, per=1)
    async def number(self, ctx, num=None):
        """
        Display a fact about a number, random if number is not provided
        :param ctx: the discord context
        :param num: the number
        """
        localize = self.bot.localize(ctx)
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
            self.bot.localize(ctx)
        )
        if isinstance(res, Embed):
            await self.bot.say(embed=res)
        else:
            await self.bot.say(res)

    @commands.command(pass_context=True)
    async def recipe(self, ctx, *, query=None):
        """
        Search for a recipe
        :param ctx: the discord context
        :param query: the search query
        """
        e = self.bot.config['API keys']['edamam']
        localize = self.bot.localize(ctx)
        if not query:
            await self.bot.say(localize['no_recipe'])
            return
        res = await recipe_search(
            query,
            localize,
            str(e['app id']),
            str(e['key']),
            self.bot.session_manager
        )
        if isinstance(res, Embed):
            await self.bot.say(embed=res)
        else:
            await self.bot.say(res)

    @commands.command(pass_context=True)
    async def remind(self, ctx, *, time: str = None):
        """
        Set a reminder and notify the user when time is up.
        """
        localize = self.bot.localize(ctx)
        if not time:
            await self.bot.say(localize['no_remind'])
            return
        try:
            seconds = parse_remind_arg(time)
            d, h, m, s = get_time_elapsed(0, seconds)
            h += d * 24
            if d > 0:
                await self.bot.say(localize['remind_long'])
        except ValueError:
            await self.bot.say(localize['remind_bad'])
            return
        await self.bot.say(localize['remind_start'].format(h, m, s))
        await sleep(seconds)
        fin = localize['remind_fin']
        await self.bot.send_message(
            ctx.message.channel,
            f'{ctx.message.author.mention} {fin.format(h,m,s)}')

    @commands.command(pass_context=True)
    async def time(self, ctx, *, tz=None):
        """
        Time zone conversion.
        """
        localize = self.bot.localize(ctx)
        if not tz:
            await self.bot.say(localize['no_tz'])
            return
        matched = get_close_matches(tz, self.tzs, 1)
        if not matched:
            await self.bot.say(localize['bad_tz'].format(tz))
            return
        zone = timezone(matched[0])
        dt = datetime.datetime.now(tz=zone)
        await self.bot.say(localize['tz_res'].format(
            zone, dt.strftime('%Y-%m-%d %H:%M:%S')))

    @commands.command(pass_context=True)
    async def urban(self, ctx, *query):
        """
        Search urban dictionary for a word.
        """
        localize = self.bot.localize(ctx)
        if not query:
            await self.bot.say(localize['no_urban'])
            return
        res = await urban(localize, self.bot.session_manager, '%20'.join(query))
        for s in res:
            await self.bot.say(s)

    @commands.command()
    async def weather(self):
        raise NotImplementedError
