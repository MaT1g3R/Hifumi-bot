from json import loads

from discord.ext import commands
from requests import get

from core.discord_functions import get_prefix
from shell import Hifumi


class Utilities:
    """
    Class for Utilities/Search commands
    """
    __slots__ = ['bot', 'cat_count']

    def __init__(self, bot: Hifumi):
        """
        Initialize the Utilities class
        :param bot: the bot object
        """
        self.bot = bot
        self.cat_count = None

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
        # http://www.catfact.info/api/v1/facts.json?page=583&per_page=1
        pass

    @fact.command()
    async def dog(self):
        # https://dog-api.kinduff.com/api/facts
        pass

    @fact.command()
    async def number(self):
        # http://numbersapi.com/foo?json=true
        # http://numbersapi.com/random?json=true
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
