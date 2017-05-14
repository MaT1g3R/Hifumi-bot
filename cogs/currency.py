from discord import Member
from discord.ext import commands

from core.currency_core import daily, transfer
from core.data_controller import get_balance


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

    @commands.command(pass_context=True)
    async def balance(self, ctx, member: Member = None):
        """
        Show the balance of the member
        :param ctx: the discord context
        :param member: if the member parameter is not provided it will show
        the message author's balance
        """
        if member is None:
            member_id = ctx.message.author.id
            localize_key = 'balance_self'
            name = ctx.message.author.display_name
        else:
            member_id = member.id
            localize_key = 'balance_other'
            name = member.display_name
        await self.bot.say(
            self.bot.get_language_dict(ctx)[localize_key].format(
                name, get_balance(self.bot.cur, member_id)
            )
        )

    @commands.command(pass_context=True, no_pm=True)
    async def transfer(self, ctx, member: Member, amount=None):
        """
        Transfer x amout of credits to another member
        :param ctx: the discord context
        :param member: the target member for the transfer
        :param amount: the amout for the transfer
        """
        localize = self.bot.get_language_dict(ctx)
        try:
            amount = int(amount)
            if amount <= 0:
                raise ValueError
        except (ValueError, TypeError):
            await self.bot.say(localize['transfer_bad_num'])
        else:
            await self.bot.say(
                transfer(
                    self.bot.conn, self.bot.cur,
                    ctx.message.author, member, amount, localize
                )
            )
