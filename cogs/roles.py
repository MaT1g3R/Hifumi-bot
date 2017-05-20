from discord.ext import commands

from core.checks import has_manage_role
from core.discord_functions import get_prefix
from core.roles_core import get_role_list, add_role, remove_role, role_unrole
from shell import Hifumi


class Roles:
    """
    Cog regarding roles
    """
    __slots__ = ['bot']

    def __init__(self, bot: Hifumi):
        """
        Initizliae the Roles class
        :param bot: the bot object
        """
        self.bot = bot

    @commands.command(no_pm=True, pass_context=True)
    async def roleme(self, ctx, *args):
        """
        Assign a role to the user
        """
        await role_unrole(
            bot=self.bot,
            ctx=ctx,
            target=ctx.message.author,
            role_name=' '.join(args),
            is_add=True,
            is_mute=False,
            check_db=True
        )

    @commands.command(no_pm=True, pass_context=True)
    async def unroleme(self, ctx, *args):
        """
        Removes a role from a user
        """
        await role_unrole(
            bot=self.bot,
            ctx=ctx,
            target=ctx.message.author,
            role_name=' '.join(args),
            is_add=False,
            is_mute=False,
            check_db=True
        )

    @commands.command(no_pm=True, pass_context=True)
    async def rolelist(self, ctx):
        """
        Display the rolelist for the server
        """
        await self.bot.say(
            get_role_list(
                server=ctx.message.server,
                conn=self.bot.conn,
                cur=self.bot.cur,
                localize=self.bot.get_language_dict(ctx)
            )
        )

    @commands.group(no_pm=True, pass_context=True)
    @commands.check(has_manage_role)
    async def selfrole(self, ctx):
        """
        Command group for selfrole
        :param ctx: the discord context
        """
        if ctx.invoked_subcommand is None:
            await self.bot.say(
                self.bot.get_language_dict(ctx)['selfrole_bad_command'].format(
                    get_prefix(
                        self.bot.cur, ctx.message.server,
                        self.bot.default_prefix
                    )
                )
            )

    @selfrole.command(pass_context=True)
    async def add(self, ctx, *args):
        """
        Add a self assignable role to the server
        """
        await self.bot.say(
            add_role(
                conn=self.bot.conn,
                cur=self.bot.cur,
                server=ctx.message.server,
                localize=self.bot.get_language_dict(ctx),
                role=' '.join(args)
            )
        )

    @selfrole.command(pass_context=True)
    async def remove(self, ctx, *args):
        """
        Removes a self assignable role from the server
        """
        await self.bot.say(
            remove_role(
                conn=self.bot.conn,
                cur=self.bot.cur,
                server=ctx.message.server,
                localize=self.bot.get_language_dict(ctx),
                role=' '.join(args)
            )
        )
