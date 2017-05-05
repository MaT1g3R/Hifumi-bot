from discord.ext import commands

from core.checks import has_manage_role
from core.discord_functions import get_prefix


class Roles:
    """
    Cog regarding roles
    """

    def __init__(self, bot):
        """
        Initizliae the Roles class
        :param bot: the bot object
        """
        self.bot = bot

    @commands.command(no_pm=True)
    async def rolelist(self):
        pass

    @commands.command(no_pm=True)
    async def roleme(self):
        pass

    @commands.command(no_pm=True)
    async def unroleme(self):
        pass

    @commands.group(no_pm=True, pass_context=True)
    @commands.check(has_manage_role)
    async def selfrole(self, ctx):
        """
        Command group for selfrole
        :param ctx: the discord context
        """
        if ctx.invoked_subcommand is None:
            localize = self.bot.get_language_dict(ctx)['selfrole_bad_command']
            await self.bot.say(
                localize.format(get_prefix(self.bot, ctx.message)))

    @selfrole.command()
    async def add(self):
        pass

    @selfrole.command()
    async def remove(self):
        pass
