from discord import Member
from discord.ext import commands

from core.checks import is_admin, has_manage_message
from core.moderation_core import ban_kick


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
    async def ban(self, ctx, member: Member, delete_message_days=0):
        await ban_kick(self.bot, ctx, member, delete_message_days)

    @commands.command(pass_context=True, no_pm=True)
    @commands.check(is_admin)
    async def kick(self, ctx, member: Member):
        await ban_kick(self.bot, ctx, member, None)

    @commands.command(pass_context=True, no_pm=True)
    @commands.check(has_manage_message)
    async def clean(self, ctx, number):
        pass

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
