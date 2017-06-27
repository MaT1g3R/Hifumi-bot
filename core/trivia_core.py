from logging import WARN
from random import shuffle
from string import ascii_uppercase

from aiohttp import ClientSession
from discord.embeds import Embed
from pytrivia import Category, Diffculty, Trivia, Type

from bot import Hifumi
from data_controller import LowBalanceError
from data_controller.data_utils import change_balance, get_prefix


class ArgumentError(ValueError):
    pass


class TriviaGame:
    """
    A class to handle the trivia command
    """
    __slots__ = ['api', 'bot', 'args', 'channel', 'author', 'conn', 'cur',
                 'localize', 'bet', 'prefix', 'data_manager', 'user_id',
                 'ctx']

    def __init__(self, ctx, bot: Hifumi, args, api: Trivia):
        """
        Initialize an instance of this class
        :param ctx: the discord context
        :param bot: the bot
        :param args: the args the user passed in from trivia command
        :param api: the trivia api
        """
        self.api = api
        self.bot = bot
        self.ctx = ctx
        self.data_manager = bot.data_manager
        self.prefix = get_prefix(self.bot, self.ctx.message)
        self.args = args
        self.channel = ctx.message.channel
        self.author = ctx.message.author
        self.user_id = int(self.author.id)
        self.localize = bot.get_language_dict(ctx)
        self.bet = 0

    async def play(self):
        """
        Play the trivia game
        """
        if not self.args and not await self.__handle_no_args():
            return
        kwargs = await self.__get_kwargs()
        if kwargs is None:
            return
        trivia_data = await self.__get_trivia_data(
            kwargs, self.bot.session_manager.session)
        if not trivia_data:
            return
        if not await self.__process_bet(kwargs):
            return
        try:
            embed, answer, correct_str, difficulty = _format_trivia(
                trivia_data, self.localize
            )
            await self.bot.send_message(self.channel, embed=embed)
            user_answer = await self.bot.wait_for_message(
                10, author=self.author, channel=self.channel
            )
            correct = await self.__handle_answer(
                user_answer, answer, correct_str
            )
            if self.bet > 0:
                await self.bot.say(
                    await _handle_bet(
                        data_manager=self.data_manager,
                        correct=correct,
                        difficulty=difficulty,
                        amount=self.bet,
                        user_id=self.user_id,
                        localize=self.localize
                    )
                )
        except Exception as e:
            if self.bet > 0:
                await change_balance(self.data_manager, self.user_id, self.bet)
            raise e

    async def __handle_no_args(self):
        """
        Handle the case where the user provided no arguments
        :return: True if the user wish to proceed, else False
        """
        await self.bot.send_message(
            self.channel, self.localize['trivia_no_args']
        )
        message = await self.bot.wait_for_message(
            10, author=self.author, channel=self.channel
        )
        key, proceed = _no_args(message)
        if key == 'trivia_abort':
            await self.bot.send_message(self.channel, self.localize[key])
        elif key == 'trivia_help':
            def f(x):
                return '\n'.join(list(x.__members__))

            await self.bot.send_message(
                self.channel, self.localize['help_sent']
            )
            await self.bot.send_message(
                self.author, self.localize[key].format(
                    f(Category), f(Diffculty), f(Type), self.prefix
                )
            )
        return proceed

    async def __get_kwargs(self):
        """
        Get the kwargs from the args user passed in
        """
        try:
            return _parse_args(self.args)
        except ArgumentError:
            await self.bot.send_message(
                self.channel,
                self.localize['trivia_bad_args'].format(self.prefix)
            )

    async def __get_trivia_data(self, kwargs, session: ClientSession):
        """
        Get the trivia data from kwargs
        :return: the trivia data
        """
        try:
            trivia_data = await _get_trivia_data(kwargs, self.api, session)
        except Exception as e:
            self.bot.logger.log(WARN, str(e))
            trivia_data = None
        if trivia_data is None:
            await self.bot.send_message(
                self.channel, self.localize['trivia_error']
            )
        return trivia_data

    async def __process_bet(self, kwargs):
        """
        Process the amount of bet the user placed
        :param kwargs: the kwargs parsed from args
        :return: True if the user has enough money else False
        """
        bet = kwargs['amount'] if 'amount' in kwargs else 0
        if bet > 0:
            try:
                await change_balance(self.data_manager, self.user_id, -bet)
                self.bet = bet
                return True
            except LowBalanceError as e:
                await self.bot.send_message(
                    self.channel, self.localize['low_balance'].format(str(e))
                )
                return False
        return True

    async def __handle_answer(self, user_answer, answer, correct_str):
        """
        Handle the user answer
        :param user_answer: the user answer
        :param answer: the correct answer
        :param correct_str: the correct answer string
        :return: True if the user answer is correct else False
        """
        if user_answer is None:
            await self.bot.send_message(
                self.channel, self.localize['trivia_timeount'].format(
                    correct_str
                )
            )
            return False
        elif user_answer.content.upper() != answer:
            await self.bot.send_message(
                self.channel, self.localize['trivia_wrong'].format(correct_str)
            )
            return False
        else:
            await self.bot.send_message(
                self.channel, self.localize['trivia_correct']
            )
            return True


def _parse_args(args):
    """
    Parse the user input arguments into kwargs
    :param args: the user input args
    :return: the parsed kwargs
    :raises: ArgumentError if there are bad args
    """
    if len(args) > 4:
        raise ArgumentError
    res = {}
    for arg in args:
        if arg.title() in Category.__members__:
            if 'category' in res:
                raise ArgumentError
            res['category'] = Category[arg.title()]
        elif arg.title() in Type.__members__:
            if 'type' in res:
                raise ArgumentError
            res['type'] = Type[arg.title()]
        elif arg.title() in Diffculty.__members__:
            if 'diffculty' in res:
                raise ArgumentError
            res['diffculty'] = Diffculty[arg.title()]
        else:
            try:
                amount = round((float(arg)))
            except:
                raise ArgumentError
            if amount < 0 or 'amount' in res:
                raise ArgumentError
            res['amount'] = amount
    return res


def _no_args(message):
    """
    Handle the case where the user input no arguments
    :param message: the user message after the prompt
    :return: (key, proceed)
    """
    if message is None:
        return 'trivia_abort', False
    else:
        s = message.content.strip('"').lower()
        if s == 'yes':
            return None, True
        elif s == 'help':
            return 'trivia_help', False
        else:
            return 'trivia_abort', False


async def _get_trivia_data(kwargs, api: Trivia, session: ClientSession):
    """
    Get the trivia data from the api
    :param kwargs: the kwargs parsed from user input args
    :param api: the trivia api
    :param session: the aiohttp ClientSession
    :return: the api response
    """
    category = kwargs['category'] if 'category' in kwargs else None
    type_ = kwargs['type'] if 'type' in kwargs else None
    diffculty = kwargs['diffculty'] if 'diffculty' in kwargs else None

    res = await api.request_async(
        session, False, 1, category, diffculty, type_)
    return res if res['response_code'] == 0 else None


def __generate_choices(correct, incorrect):
    """
    Generate choices from correct and incorrect answers
    :param correct: the correct answer
    :param incorrect: the incorrect answers
    :return: a list of shuffled answers
    """
    all_choices = [correct] + incorrect
    shuffle(all_choices)
    choices = []
    res_letter = ''
    for i in range(len(all_choices)):
        choice = all_choices[i]
        letter = ascii_uppercase[i]
        choices.append((letter, choice))
        if choice == correct:
            res_letter = letter
    return choices, res_letter


def _format_trivia(trivia_data, localize):
    """
    Format trivia data in an discord embed object
    :param trivia_data: the trivia data
    :param localize: the localization strings
    :return: (embed, answer, correct_str, difficulty)
    """
    result = trivia_data['results'][0]
    question = result['question']
    type_ = result['type']
    category = result['category']
    correct = result['correct_answer']
    incorrect = result['incorrect_answers']
    difficulty = result['difficulty']

    is_multiple = type_ == 'multiple'
    choice_str = localize['choices_str'] if is_multiple else localize['tf_str']
    colour = {
        "easy": 0x0baa00,
        "medium": 0xeab31c,
        "hard": 0xd10606
    }[difficulty]
    embed = Embed(colour=colour)
    embed.add_field(name=localize['category'], value=category)
    embed.add_field(name=localize['difficulty'], value=localize[difficulty])
    embed.add_field(name=localize['type'], value=localize[type_])
    embed.add_field(name=localize['question'], value=question, inline=False)
    embed.add_field(name=localize['choices'], value=choice_str, inline=False)
    if is_multiple:
        choices, answer = __generate_choices(correct, incorrect)
        correct_str = answer + '. ' + correct
        for choice in choices:
            embed.add_field(name=choice[0], value=choice[1])
    else:
        answer = correct[:1]
        correct_str = correct

    return embed, answer, correct_str, difficulty


async def _handle_bet(**kwargs):
    """
    Handle the trivia outcome if the user placed a bet
    :param kwargs: see below for details
    :key data_manager: the data_manager
    :key correct: if the answer was correct or not
    :key difficulty: the difficulty of the answer
    :key amount: the amount of bet
    :key user_id: the user id
    :key localize: the localization strings
    :return: the bot response string
    """
    data_manager = kwargs['data_manager']
    correct = kwargs['correct']
    difficulty = kwargs['difficulty']
    amount = kwargs['amount']
    user_id = kwargs['user_id']
    localize = kwargs['localize']
    if correct:
        multiplier = {
            "easy": 0.5,
            "medium": 1,
            "hard": 2
        }[difficulty]
        price = round(amount * multiplier)
        delta = price
        await change_balance(data_manager, user_id, amount + price)
    else:
        delta = amount
    key = 'trivia_correct_balance' if correct else 'trivia_wrong_balance'
    return localize[key].format(
        delta, data_manager.get_user_balance(user_id))
