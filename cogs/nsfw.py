"""
NSFW cog
"""
from discord.ext import commands
from pybooru import Danbooru

from core.checks import is_nsfw
from core.nsfw_core import danbooru, gelbooru, k_or_y, random_str
from config.settings import DANBOORU_API, DANBOORU_USERNAME


class Nsfw:
    def __init__(self, bot):
        """
        Initialize the Nsfw class
        :param bot: the discord bot object
        """
        self.bot = bot
        self.danbooru_api = Danbooru(
            'danbooru', username=DANBOORU_USERNAME, api_key=DANBOORU_API)

    @commands.command(pass_context=True)
    @commands.check(is_nsfw)
    @commands.cooldown(rate=1, per=3, type=commands.BucketType.server)
    async def danbooru(self, ctx, *query: str):
        if len(query) > 2:
            await self.bot.say(self.bot.get_language_dict(ctx)['two_term'])
            return
        if len(query) == 0:
            await self.bot.say(random_str(self.bot, ctx))
        await self.bot.say(danbooru(self.bot, ctx, query, self.danbooru_api))

    @commands.command(pass_context=True)
    @commands.check(is_nsfw)
    @commands.cooldown(rate=1, per=3, type=commands.BucketType.server)
    async def konachan(self, ctx, *query: str):
        if len(query) == 0:
            await self.bot.say(random_str(self.bot, ctx))
        await self.bot.say(k_or_y(self.bot, ctx, query, 'Konachan'))

    @commands.command(pass_context=True)
    @commands.check(is_nsfw)
    @commands.cooldown(rate=1, per=3, type=commands.BucketType.server)
    async def yandere(self, ctx, *query: str):
        if len(query) == 0:
            await self.bot.say(random_str(self.bot, ctx))
        await self.bot.say(k_or_y(self.bot, ctx, query, 'Yandere'))

    @commands.command(pass_context=True)
    @commands.check(is_nsfw)
    @commands.cooldown(rate=1, per=3, type=commands.BucketType.server)
    async def gelbooru(self, ctx, *query: str):
        if len(query) == 0:
            await self.bot.say(random_str(self.bot, ctx))
        await self.bot.say(gelbooru(self.bot, ctx, query))
