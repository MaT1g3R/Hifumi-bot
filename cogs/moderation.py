from discord import Member
from discord.ext import commands

from core.checks import is_admin, has_manage_message
from core.moderation_core import ban_kick, clean_msg


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
        good_number = False
        if delete_message_days is None:
            delete_message_days = 0
        try:
            delete_message_days = int(delete_message_days)
            if 0 <= delete_message_days <= 7:
                good_number = True
        except ValueError:
            good_number = False
        if good_number:
            await ban_kick(self.bot, ctx, member, delete_message_days)
        else:
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
                number = int(number)
                await clean_msg(ctx, self.bot, number)
            except ValueError:
                await self.bot.say(bad_num_msg)

    @commands.command(pass_context=True, no_pm=True)
    @commands.check(is_admin)
    async def mute(self, ctx, member: Member):
        pass

    @commands.command(pass_context=True, no_pm=True)
    @commands.check(is_admin)
    async def unmute(self, ctx, member: Member):
        pass

    @commands.command(pass_context=True, no_pm=True)
    @commands.check(is_admin)
    async def setlevel(self, ctx, member: Member, lvl):
        pass

    @commands.command(pass_context=True, no_pm=True)
    @commands.check(is_admin)
    async def warn(self, ctx, member: Member, message):
        pass

    @commands.command(pass_context=True, no_pm=True)
    @commands.check(is_admin)
    async def setlanguage(self, ctx, language):
        pass

    @commands.command(pass_context=True, no_pm=True)
    @commands.check(is_admin)
    async def setprefix(self, ctx, prefix):
        pass
