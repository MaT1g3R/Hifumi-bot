"""
NSFW cog
"""
from discord.ext import commands
from pybooru import Danbooru

from config.settings import DANBOORU_API, DANBOORU_USERNAME
from core.checks import is_nsfw, no_badword
from core.nsfw_core import danbooru, gelbooru, k_or_y, random_str, e621, \
    greenteaneko


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
    @commands.check(no_badword)
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.server)
    async def danbooru(self, ctx, *query: str):
        """
        Danbooru search command
        :param ctx: the discord context
        :param query: the sarch queries
        """
        if len(query) > 2:
            await self.bot.say(self.bot.get_language_dict(ctx)['two_term'])
            return
        if len(query) == 0:
            await self.bot.say(random_str(self.bot, ctx))
        result, tags = danbooru(self.bot, ctx, query, self.danbooru_api)
        await self.bot.say(result)
        if tags is not None:
            self.bot.data_handler.write_tag_list('danbooru', tags)

    @commands.command(pass_context=True)
    @commands.check(is_nsfw)
    @commands.check(no_badword)
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.server)
    async def konachan(self, ctx, *query: str):
        if len(query) == 0:
            await self.bot.say(random_str(self.bot, ctx))
        res, tags = k_or_y(self.bot, ctx, query, 'Konachan')
        await self.bot.say(res)
        if tags is not None:
            self.bot.data_handler.write_tag_list('konachan', tags)

    @commands.command(pass_context=True)
    @commands.check(is_nsfw)
    @commands.check(no_badword)
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.server)
    async def yandere(self, ctx, *query: str):
        """
        Yandere search command
        :param ctx: the discord context
        :param query: the sarch queries
        """
        if len(query) == 0:
            await self.bot.say(random_str(self.bot, ctx))
        res, tags = k_or_y(self.bot, ctx, query, 'Yandere')
        await self.bot.say(res)
        if tags is not None:
            self.bot.data_handler.write_tag_list('yandere', tags)

    @commands.command(pass_context=True)
    @commands.check(is_nsfw)
    @commands.check(no_badword)
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.server)
    async def gelbooru(self, ctx, *query: str):
        """
        Gelbooru search command
        :param ctx: the discord context
        :param query: the sarch queries
        """
        if len(query) == 0:
            await self.bot.say(random_str(self.bot, ctx))
        await self.bot.say(gelbooru(self.bot, ctx, query))

    @commands.command(pass_context=True)
    @commands.check(is_nsfw)
    @commands.check(no_badword)
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.server)
    async def e621(self, ctx, *query: str):
        """
       e621 search command
       :param ctx: the discord context
       :param query: the sarch queries
       """
        if len(query) == 0:
            await self.bot.say(random_str(self.bot, ctx))
        res, tags = e621(self.bot, ctx, query)
        await self.bot.say(res)
        if tags is not None:
            self.bot.data_handler.write_tag_list('e621', tags)

    @commands.command(pass_context=True)
    @commands.check(is_nsfw)
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.server)
    async def greenteaneko(self, ctx):
        """
        Find a random greenteaneko comic
        :param ctx: the discord context
        """
        await self.bot.say(greenteaneko(ctx, self.bot))
