from discord import Member
from discord.ext import commands

from config.settings import DATA_CONTROLLER
from core.checks import is_admin, has_manage_message, has_manage_role
from core.discord_functions import get_prefix
from core.language_support import set_language
from core.moderation_core import ban_kick, clean_msg, mute_unmute


class Moderation:
    """
    The cog for Moderation commands
    """
    __slots__ = ['bot']

    def __init__(self, bot):
        """
        Initialize the Moderation class
        :param bot: the bot
        """
        self.bot = bot

    @commands.command(pass_context=True, no_pm=True)
    @commands.check(is_admin)
    async def ban(self, ctx, member: Member, delete_message_days=None):
        """
        Throw down the ban hammer on someone
        :param ctx: the discord context
        :param member: the discord member
        :param delete_message_days: option to delete messages from the user
        """
        bad_num_msg = self.bot.get_language_dict(ctx)['delete_message_days']
        if delete_message_days is None:
            delete_message_days = 0
        try:
            delete_message_days = int(delete_message_days)
            if 0 <= delete_message_days <= 7:
                await ban_kick(self.bot, ctx, member, delete_message_days)
            else:
                await self.bot.say(bad_num_msg)
        except ValueError:
            await self.bot.say(bad_num_msg)

    @commands.command(pass_context=True, no_pm=True)
    @commands.check(is_admin)
    async def kick(self, ctx, member: Member):
        await ban_kick(self.bot, ctx, member, None)

    @commands.command(pass_context=True, no_pm=True)
    @commands.check(has_manage_message)
    @commands.cooldown(rate=1, per=3, type=commands.BucketType.server)
    async def clean(self, ctx, number=None):
        bad_num_msg = self.bot.get_language_dict(ctx)['clean_message_bad_num']
        if number is None:
            await self.bot.say(bad_num_msg)
        else:
            try:
                await clean_msg(ctx, self.bot, int(number))
            except ValueError:
                await self.bot.say(bad_num_msg)

    @commands.command(pass_context=True, no_pm=True)
    @commands.check(has_manage_role)
    async def mute(self, ctx, member: Member):
        await mute_unmute(ctx, self.bot, member, True)

    @commands.command(pass_context=True, no_pm=True)
    @commands.check(has_manage_role)
    async def unmute(self, ctx, member: Member):
        await mute_unmute(ctx, self.bot, member, False)

    @commands.command(pass_context=True, no_pm=True)
    @commands.check(is_admin)
    async def warn(self, ctx, member: Member, message):
        pass

    @commands.command(pass_context=True, no_pm=True)
    @commands.check(is_admin)
    async def setlanguage(self, ctx, language: str = None):
        if language not in self.bot.language or language is None:
            localize = self.bot.get_language_dict(ctx)
            await self.bot.say(
                localize['lan_no_exist'].format(
                    language, get_prefix(self.bot, ctx.message)
                )
            )
        else:
            res = set_language(ctx, self.bot, language)
            await self.bot.say(res)

    @commands.command(pass_context=True, no_pm=True)
    @commands.check(is_admin)
    async def setprefix(self, ctx, prefix: str):
        DATA_CONTROLLER.set_prefix(ctx.message.server.id, prefix)
        await self.bot.say(
            self.bot.get_language_dict(ctx)['set_prefix'].format(prefix)
        )
