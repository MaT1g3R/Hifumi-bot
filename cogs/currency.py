from discord import Member
from discord.ext import commands
from pytrivia import Trivia

from bot import Hifumi
from core.currency_core import daily, determine_slot_result, roll_slots, \
    slots_setup, transfer
from core.trivia_core import TriviaGame
from data_controller import LowBalanceError
from data_controller.data_utils import change_balance


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
        await self.bot.say(
            await daily(
                self.bot.data_manager,
                int(ctx.message.author.id),
                self.bot.localize(ctx))
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
            member_id = int(ctx.message.author.id)
            localize_key = 'balance_self'
            name = ctx.message.author.display_name
        else:
            member_id = int(member.id)
            localize_key = 'balance_other'
            name = member.display_name
        balance = self.bot.data_manager.get_user_balance(member_id) or 0
        await self.bot.say(
            (self.bot.localize(ctx))[localize_key].format(
                name, balance
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
        localize = self.bot.localize(ctx)
        try:
            amount = round(float(amount))
            if amount <= 0:
                raise ValueError
        except (ValueError, TypeError):
            await self.bot.say(localize['currency_bad_num'])
        else:
            if self.bot.config['API keys']['discordtel'] and \
               member.id is "224662505157427200":
                self.bot.send_message(member, 
                                      ctx.message.author.id + 
                                      " sends " + amount + " credits")
            await self.bot.say(
                await transfer(
                    self.bot.data_manager, ctx.message.author,
                    member, amount, localize
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
        localize = self.bot.localize(ctx)
        try:
            amount = round(float(amount))
            if amount <= 0:
                raise ValueError
        except (ValueError, TypeError):
            await self.bot.say(localize['currency_bad_num'])
            return

        user_id = int(ctx.message.author.id)
        try:
            await change_balance(self.bot.data_manager, user_id, -amount)
        except LowBalanceError as e:
            await self.bot.say(localize['low_balance'].format(str(e)))
            return

        q1, q2, q3, n1, n2, n3 = slots_setup(self.bot.all_emojis, 2, 5)
        await self.bot.say(localize['slots_header'])
        msg = await self.bot.say(
            '[ {} | {} | {} ]'.format(q1[0], q2[0], q3[0])
        )
        r1, r2, r3 = await roll_slots(
            self.bot, msg, q1, q2, q3, n1, n2, n3
        )
        await self.bot.say(
            await determine_slot_result(
                self.bot.data_manager, user_id,
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

    @commands.command()
    async def shop(self):
        raise NotImplementedError
