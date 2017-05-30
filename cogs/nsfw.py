from discord.ext import commands
from pybooru import Danbooru

from config import *
from core.nsfw_core import danbooru, gelbooru, k_or_y, random_str, e621, \
    greenteaneko
from scripts.checks import is_nsfw, no_badword
from scripts.data_controller import write_tag_list_
from shell import Hifumi


class Nsfw:
    """
    NSFW cog
    """
    __slots__ = ['bot', 'danbooru_api']

    def __init__(self, bot: Hifumi):
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
        localize = self.bot.get_language_dict(ctx)
        if len(query) > 2:
            await self.bot.say(localize['two_term'])
            return
        if len(query) == 0:
            await self.bot.say(random_str(self.bot, ctx))
        result, tags = danbooru(
            self.bot.cur, query, self.danbooru_api, localize
        )
        await self.bot.say(result)
        if tags is not None:
            write_tag_list_(self.bot.conn, self.bot.cur, 'danbooru', tags)

    @commands.command(pass_context=True)
    @commands.check(is_nsfw)
    @commands.check(no_badword)
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.server)
    async def konachan(self, ctx, *query: str):
        if len(query) == 0:
            await self.bot.say(random_str(self.bot, ctx))
        res, tags = k_or_y(
            self.bot.cur, query, 'Konachan', self.bot.get_language_dict(ctx)
        )
        await self.bot.say(res)
        if tags is not None:
            write_tag_list_(self.bot.conn, self.bot.cur, 'konachan', tags)

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
        res, tags = k_or_y(
            self.bot.cur, query, 'Yandere', self.bot.get_language_dict(ctx)
        )
        await self.bot.say(res)
        if tags is not None:
            write_tag_list_(self.bot.conn, self.bot.cur, 'yandere', tags)

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
        await self.bot.say(
            gelbooru(
                self.bot.conn, self.bot.cur,
                query, self.bot.get_language_dict(ctx)
            )
        )

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
        res, tags = e621(self.bot.cur, query, self.bot.get_language_dict(ctx))
        await self.bot.say(res)
        if tags is not None:
            write_tag_list_(self.bot.conn, self.bot.cur, 'e621', tags)

    @commands.command(pass_context=True)
    @commands.check(is_nsfw)
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.server)
    async def greenteaneko(self, ctx):
        """
        Find a random greenteaneko comic
        :param ctx: the discord context
        """
        await self.bot.say(greenteaneko(self.bot.get_language_dict(ctx)))
