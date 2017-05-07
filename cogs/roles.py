from discord.ext import commands

from core.checks import has_manage_role
from core.discord_functions import get_prefix
from core.roles_core import get_role_list, add_role, remove_role, role_me, \
    unrole_me


class Roles:
    """
    Cog regarding roles
    """
    __slots__ = ['bot']

    def __init__(self, bot):
        """
        Initizliae the Roles class
        :param bot: the bot object
        """
        self.bot = bot

    async def role_unrole(self, ctx, args, is_add):
        """
        A helper method to handle roleme and unroleme
        :param ctx: the context
        :param args: the args passed into roleme and unroleme
        :param is_add: wether if the method is add or remove
        """
        res, roles = role_me(ctx, self.bot, ' '.join(args)) if is_add else \
            unrole_me(ctx, self.bot, ' '.join(args))
        try:
            if roles:
                for role in roles:
                    if is_add:
                        await self.bot.add_roles(ctx.message.author, role)
                    else:
                        await self.bot.remove_roles(ctx.message.author, role)
            await self.bot.say(res)
        except Exception as e:
            await self.bot.say('```Python\n' + str(e) + '```')

    @commands.command(no_pm=True, pass_context=True)
    async def roleme(self, ctx, *args):
        """
        Assign a role to the user
        """
        await self.role_unrole(ctx, args, True)

    @commands.command(no_pm=True, pass_context=True)
    async def unroleme(self, ctx, *args):
        """
        Removes a role from a user
        """
        await self.role_unrole(ctx, args, False)

    @commands.command(no_pm=True, pass_context=True)
    async def rolelist(self, ctx):
        """
        Display the rolelist for the server
        """
        await self.bot.say(get_role_list(ctx, self.bot))

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

    @selfrole.command(pass_context=True)
    async def add(self, ctx, *args):
        """
        Add a self assignable role to the server
        """
        await self.bot.say(add_role(ctx, self.bot, ' '.join(args)))

    @selfrole.command(pass_context=True)
    async def remove(self, ctx, *args):
        """
        Removes a self assignable role from the server
        """
        await self.bot.say(remove_role(ctx, self.bot, ' '.join(args)))
