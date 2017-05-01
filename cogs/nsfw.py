"""
NSFW cog
"""
from discord.ext import commands
from core.checks import is_nsfw
from core.nsfw_core import danbooru, gelbooru, k_or_y
from pybooru import Danbooru


class Nsfw:
    def __init__(self, bot):
        """
        Initialize the Nsfw class
        :param bot: the discord bot object
        """
        self.bot = bot
        self.random = 'You didn\'t specify a search term, here\'s a ' \
                      'random result.'
        self.danbooru_api = Danbooru('danbooru')

    @commands.command()
    @commands.check(is_nsfw)
    @commands.cooldown(rate=1, per=3, type=commands.BucketType.server)
    async def danbooru(self, *query: str):
        if len(query) > 2:
            await self.bot.say(
                'You cannot search for more than 2 tags at a time')
            return
        if len(query) == 0:
            await self.bot.say(self.random)
        await self.bot.say(danbooru(query, self.danbooru_api,
                                    self.bot.data_handler))

    @commands.command()
    @commands.check(is_nsfw)
    @commands.cooldown(rate=1, per=3, type=commands.BucketType.server)
    async def konachan(self, *query: str):
        if len(query) == 0:
            await self.bot.say(self.random)
        await self.bot.say(k_or_y(query, 'Konachan'))

    @commands.command()
    @commands.check(is_nsfw)
    @commands.cooldown(rate=1, per=3, type=commands.BucketType.server)
    async def yandere(self, *query: str):
        if len(query) == 0:
            await self.bot.say(self.random)
        await self.bot.say(k_or_y(query, 'Yandere'))

    @commands.command()
    @commands.check(is_nsfw)
    @commands.cooldown(rate=1, per=3, type=commands.BucketType.server)
    async def gelbooru(self, *query: str):
        if len(query) == 0:
            await self.bot.say(self.random)
        await self.bot.say(gelbooru(query))
