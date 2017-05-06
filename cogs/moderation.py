from discord import Member
from discord.ext import commands

from core.checks import is_admin, has_manage_message
from core.moderation_core import ban_kick, clean_msg


class Moderation:
    """
    The cog for Moderation commands
    """

    def __init__(self, bot):
        """
        Initialize the Moderation class
        :param bot: the bot
        """
        self.bot = bot

    @commands.command(pass_context=True, no_pm=True)
    @commands.check(is_admin)
    async def ban(self, ctx, member: Member, delete_message_days: int=0):
        """
        Throw down the ban hammer on someone
        :param ctx: the discord context
        :param member: the discord member
        :param delete_message_days: option to delete messages from the user
        """
        if delete_message_days < 0 or delete_message_days > 7:
            await self.bot.say(
                self.bot.get_language_dict(ctx)['delete_message_days']
            )
            return
        await ban_kick(self.bot, ctx, member, delete_message_days)

    @commands.command(pass_context=True, no_pm=True)
    @commands.check(is_admin)
    async def kick(self, ctx, member: Member):
        await ban_kick(self.bot, ctx, member, None)

    @commands.command(pass_context=True, no_pm=True)
    @commands.check(has_manage_message)
    async def clean(self, ctx, number=None):
        bad_int_msg = self.bot.get_language_dict(ctx)['clean_message_bad_num']
        try:
            number = int(number)
        except (TypeError, ValueError):
            await self.bot.say(bad_int_msg)
        else:
            await clean_msg(ctx, self.bot, number)

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
