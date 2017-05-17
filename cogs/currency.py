from discord import Member
from discord.ext import commands
from pytrivia import Trivia

from core.currency_core import daily, transfer, slots_setup, roll_slots, \
    determine_slot_result
from core.data_controller import get_balance, change_balance
from core.trivia_core import TriviaGame
from shell.hifumi import Hifumi


class Currency:
    """
    Commands related to currency
    """
    __slots__ = ['bot', 'trivia_api']

    def __init__(self, bot: Hifumi):
        self.bot = bot
        self.trivia_api = Trivia(True)

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
            amount = round(float(amount))
            if amount <= 0:
                raise ValueError
        except (ValueError, TypeError):
            await self.bot.say(localize['currency_bad_num'])
        else:
            await self.bot.say(
                transfer(
                    self.bot.conn, self.bot.cur,
                    ctx.message.author, member, amount, localize
                )
            )

    @commands.command(pass_context=True)
    @commands.cooldown(rate=1, per=6, type=commands.BucketType.user)
    async def slots(self, ctx, amount=None):
        """
        Play slots
        :param ctx: the discord context
        :param amount: the amount of bet
        """
        localize = self.bot.get_language_dict(ctx)
        try:
            amount = round(float(amount))
            if amount <= 0:
                raise ValueError
        except (ValueError, TypeError):
            await self.bot.say(localize['currency_bad_num'])
        else:
            localize = self.bot.get_language_dict(ctx)
            conn = self.bot.conn
            cur = self.bot.cur
            user_id = ctx.message.author.id
            balance = get_balance(cur, user_id)
            if balance < amount:
                await self.bot.say(localize['low_balance'].format(balance))
            else:
                change_balance(conn, cur, user_id, -amount)
                q1, q2, q3, n1, n2, n3 = slots_setup(self.bot.all_emojis, 2, 5)
                await self.bot.say(localize['slots_header'])
                msg = await self.bot.say(
                    '[ {} | {} | {} ]'.format(q1[0], q2[0], q3[0])
                )
                r1, r2, r3 = await roll_slots(
                    self.bot, msg, q1, q2, q3, n1, n2, n3
                )
                await self.bot.say(
                    determine_slot_result(
                        conn, cur, user_id, self.bot.user.id,
                        localize, r1, r2, r3, amount
                    )
                )

    @commands.command(pass_context=True)
    @commands.cooldown(rate=1, per=5, type=commands.BucketType.user)
    async def trivia(self, ctx, *args):
        """
        Play trivia
        :param ctx: the discord context
        :param args: the arguments the user passes in.
            There can be at most 4 arguments:
                Type, Diffculty, Category, Amount(of bet)
        """
        await TriviaGame(ctx, self.bot, args, self.trivia_api).play()
