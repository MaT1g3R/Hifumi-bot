from typing import Optional

from discord.ext import commands

from bot import Hifumi
from data_controller.data_utils import add_self_role, get_prefix, \
    remove_self_role, self_role_names
from scripts.checks import has_manage_role
from scripts.discord_functions import get_server_role, handle_forbidden_http


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

    async def __role_me(self, ctx, role: Optional[str], is_add: bool):
        """
        Helper method to assign/remove a self role from a member
        :param ctx: the discord context
        :param role: the role name
        :param is_add: True to assign role, False to rm role
        """
        localize = self.bot.localize(ctx)
        if not role:
            await self.bot.say(localize['no_role'])
            return
        guild = ctx.message.server
        server_role = get_server_role(role, guild)
        role_lst = await self_role_names(guild, self.bot.data_manager)
        if not server_role:
            await self.bot.say(localize['role_unrole_no_exist'])
            return
        if role not in role_lst:
            await self.bot.say(localize['not_assignable'])
            return
        try:
            if is_add:
                await self.bot.add_roles(ctx.message.author, server_role)
                await self.bot.say(
                    localize['role_me_success'].format(role)
                )
            else:
                await self.bot.remove_roles(ctx.message.author, server_role)
                await self.bot.say(
                    localize['unrole_me_success'].format(role)
                )
        except Exception as e:
            action = localize['assign'] if is_add else localize['remove']
            await handle_forbidden_http(
                e, self.bot, ctx.message.channel, localize, action
            )

    @commands.command(no_pm=True, pass_context=True)
    async def roleme(self, ctx, *, role: str = None):
        """
        Assign a role to the member
        """
        await self.__role_me(ctx, role, True)

    @commands.command(no_pm=True, pass_context=True)
    async def unroleme(self, ctx, *, role: str = None):
        """
        Removes a role from a member
        """
        await self.__role_me(ctx, role, False)

    @commands.group(no_pm=True, pass_context=True)
    async def selfrole(self, ctx):
        """
        Command group for selfrole
        :param ctx: the discord context
        """
        if ctx.invoked_subcommand is None:
            localize = self.bot.localize(ctx)
            await self.bot.say(
                localize['selfrole_bad_command'].format(
                    get_prefix(self.bot, ctx.message)
                )
            )

    @selfrole.command(pass_context=True)
    async def list(self, ctx):
        """
        Display the selfrole list for the server
        """
        lst = await self_role_names(ctx.message.server, self.bot.data_manager)
        localize = self.bot.localize(ctx)
        if lst:
            res = localize['has_role_list'] + '```\n' + '\n'.join(lst) + '```'
        else:
            res = localize['no_role_list']
        await self.bot.say(res)

    async def __modify_self_role(self, ctx, role: Optional[str], is_add: bool):
        """
        Modify self role for a guild.
        :param ctx: the discord context.
        :param role: the self role name.
        :param is_add: True to add, False to remove
        """
        guild = ctx.message.server
        localize = self.bot.localize(ctx)
        if not role:
            await self.bot.say(localize['no_role'])
            return
        if not get_server_role(role, guild):
            await self.bot.say(localize['role_no_exist'])
        elif is_add:
            # FIXME Remove casting after lib rewrite
            await add_self_role(self.bot.data_manager, int(guild.id), role)
            await self.bot.say(localize['role_add_success'].format(role))
        else:
            # FIXME Remove casting after lib rewrite
            await remove_self_role(self.bot.data_manager, int(guild.id), role)
            await self.bot.say(localize['role_remove_success'].format(role))

    @selfrole.command(pass_context=True)
    @commands.check(has_manage_role)
    async def add(self, ctx, *, role: str = None):
        """
        Add a self assignable role to the server
        """
        await self.__modify_self_role(ctx, role, True)

    @selfrole.command(pass_context=True)
    @commands.check(has_manage_role)
    async def remove(self, ctx, *, role: str = None):
        """
        Removes a self assignable role from the server
        """
        await self.__modify_self_role(ctx, role, False)
