from discord import Member
from discord.ext import commands

from core.checks import is_admin, has_manage_message, has_manage_role
from core.data_controller import set_prefix
from core.discord_functions import get_prefix, get_name_with_discriminator
from core.language_support import set_language
from core.moderation_core import ban_kick, clean_msg, mute_unmute, \
    generate_mod_log_list, add_mod_log, remove_mod_log, send_mod_log


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
    async def ban(self, ctx, member: Member, *args):
        """
        Throw down the ban hammer on someone
        :param ctx: the discord context
        :param member: the discord member
        :param args: if args[0] is an interger it will be resolved as
        delete_message_days, else delete_message_days will be 0
        """
        localize = self.bot.get_language_dict(ctx)
        bad_num_msg = localize['delete_message_days']
        no_reason = localize['pls_provide_reason']
        try:
            delete_message_days = int(args[0])
            args = args[1:]
        except ValueError:
            delete_message_days = 0
        except IndexError:
            await self.bot.say(no_reason)
            return
        if not args:
            await self.bot.say(no_reason)
        else:
            reason = ' '.join(args)
            if 0 <= delete_message_days <= 7:
                await ban_kick(
                    self.bot, ctx, member, delete_message_days, reason
                )
            else:
                await self.bot.say(bad_num_msg)

    @commands.command(pass_context=True, no_pm=True)
    @commands.check(is_admin)
    async def kick(self, ctx, member: Member, *reason):
        """
        Kick a member from the server
        :param ctx: the discord context object
        :param member: the member to be kicked
        :param reason: the kick reason
        """
        if not reason:
            await self.bot.say(
                self.bot.get_language_dict(ctx)['pls_provide_reason']
            )
        else:
            await ban_kick(self.bot, ctx, member, None, ' '.join(reason))

    @commands.command(pass_context=True, no_pm=True)
    @commands.check(has_manage_message)
    @commands.cooldown(rate=1, per=3, type=commands.BucketType.server)
    async def clean(self, ctx, number=None):
        """
        Clean amount between 1-99 of messages from the current channel
        :param ctx: the discord context object
        :param number: the amount of messages to be deleted
        """
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
        """
        Give a member the "Muted" role
        :param ctx: the discord context object
        :param member: the member to be muted
        """
        await mute_unmute(ctx, self.bot, member, True)

    @commands.command(pass_context=True, no_pm=True)
    @commands.check(has_manage_role)
    async def unmute(self, ctx, member: Member):
        """
        Remove the "Muted" role from a member
        :param ctx: the discord context object
        :param member: the member to be unmuted
        """
        await mute_unmute(ctx, self.bot, member, False)

    @commands.command(pass_context=True, no_pm=True)
    @commands.check(is_admin)
    async def warn(self, ctx, member: Member, *reason):
        """
        Warn someone
        :param ctx: the discord context object
        :param member: the member to be warned
        :param reason: the warn reason
        """
        localize = self.bot.get_language_dict(ctx)
        if not reason:
            await self.bot.say(localize['pls_provide_reason'])
        else:
            reason = ' '.join(reason)
            author = ctx.message.author
            author = get_name_with_discriminator(author)
            await self.bot.say(
                localize['warn_success'].format(member, reason, author)
            )
            await send_mod_log(
                ctx, self.bot, localize['warn'], member, reason
            )

    @commands.command(pass_context=True, no_pm=True)
    @commands.check(is_admin)
    async def setlanguage(self, ctx, language: str = None):
        """
        Set the language for the server
        :param ctx: the discord context object
        :param language: the language to set to
        """
        localize = self.bot.get_language_dict(ctx)
        if language not in self.bot.language or language is None:
            await self.bot.say(
                localize['lan_no_exist'].format(
                    language,
                    get_prefix(
                        self.bot.cur, ctx.message.server,
                        self.bot.default_prefix
                    )
                )
            )
        else:
            res = set_language(
                self.bot.conn, self.bot.cur,
                localize, ctx.message.server.id, language
            )
            await self.bot.say(res)

    @commands.command(pass_context=True, no_pm=True)
    @commands.check(is_admin)
    async def setprefix(self, ctx, prefix: str):
        """
        Set the prefix for the server
        :param ctx: the discord context object
        :param prefix: the prefix to set to
        """
        set_prefix(self.bot.conn, self.bot.cur, ctx.message.server.id, prefix)
        await self.bot.say(
            self.bot.get_language_dict(ctx)['set_prefix'].format(prefix)
        )

    @commands.group(pass_context=True, no_pm=True)
    @commands.check(is_admin)
    async def modlog(self, ctx):
        """
        Command group for modlog, if no sub command is invoked,
        the bot will display a generic message stating the list of modlogs
        :param ctx: the discord context
        """
        if ctx.invoked_subcommand is None:
            await self.bot.say(
                generate_mod_log_list(
                    localize=self.bot.get_language_dict(ctx),
                    conn=self.bot.conn,
                    cur=self.bot.cur,
                    server=ctx.message.server,
                    default_prefix=self.bot.default_prefix
                )
            )

    @modlog.command(pass_context=True)
    async def add(self, ctx):
        """
        Add the current channel as a mod log channel
        :param ctx: the discord context
        """
        await self.bot.say(
            add_mod_log(
                conn=self.bot.conn,
                cur=self.bot.cur,
                server_id=ctx.message.server.id,
                channel_id=ctx.message.channel.id,
                channel_name=ctx.message.channel.name,
                localize=self.bot.get_language_dict(ctx)
            )
        )

    @modlog.command(pass_context=True)
    async def remove(self, ctx):

        """
        Remove the current channel from mod log channels
        :param ctx: the discord context
        """
        await self.bot.say(
            remove_mod_log(
                conn=self.bot.conn,
                cur=self.bot.cur,
                server_id=ctx.message.server.id,
                channel_id=ctx.message.channel.id,
                channel_name=ctx.message.channel.name,
                localize=self.bot.get_language_dict(ctx)
            )
        )
