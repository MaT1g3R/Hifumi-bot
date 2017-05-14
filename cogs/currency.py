from discord.ext import commands


class Currency:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def daily(self, ctx):
        """
        Daily command
        :param ctx: the discord context
        """
        pass
