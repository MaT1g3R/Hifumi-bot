from discord.ext import commands

from core.currency_core import daily


class Currency:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def daily(self, ctx):
        """
        Daily command
        :param ctx: the discord context
        """
        await self.bot.say(daily(
            self.bot.conn, self.bot.cur,
            ctx.message.author.id, self.bot.get_language_dict(ctx))
        )
