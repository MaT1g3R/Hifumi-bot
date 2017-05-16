from random import shuffle
from string import ascii_uppercase

from pytrivia import Diffculty, Category, Type

from core.currency_core import ArgumentError
from core.data_controller import get_balance, TransferError, transfer_balance
from core.discord_functions import build_embed, get_prefix


class TriviaGame:
    """
    A class to handle trivia commands
    """

    def __init__(self, api, bot, args, ctx):
        """
        Initialize an instance of TriviaGame
        :param api: the trivia api
        :param bot: the bot
        :param args: the args the user passed in
        :param ctx: the discord context
        """
        self.api = api
        self.bot = bot
        self.localize = bot.get_language_dict(ctx)
        self.args = args
        self.author = ctx.message.author
        self.channel = ctx.message.channel
        self.kwargs = {}
        self.trivia_data = None
        self.embed = None
        self.answer = None
        self.answer_str = None
        self.difficulty = None
        self.prefix = get_prefix(self.bot.cur, ctx.message.server, self.bot.default_prefix)
        self.amount = 0

    def __parse_trivia_arguments(self):
        if len(self.args) > 4:
            raise ArgumentError
        res = {}
        for arg in self.args:
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
        self.kwargs = res

    def __get_trivia_data(self):
        category = self.kwargs['category'] if 'category' in self.kwargs else None
        type_ = self.kwargs['type'] if 'type' in self.kwargs else None
        diffculty = self.kwargs['diffculty'] if 'diffculty' in self.kwargs else None
        res = self.api.request(1, category, diffculty, type_)
        self.trivia_data = res if res['response_code'] == 0 else None

    def __format_trivia_question(self):
        result = self.trivia_data['results'][0]
        question = result['question']
        type_ = result['type']
        category = result['category']
        correct = result['correct_answer']
        incorrect = result['incorrect_answers']
        difficulty = result['difficulty']
        is_multiple = type_ == 'multiple'
        choice_str = self.localize['choices_str'] if is_multiple else self.localize['tf_str']
        colour = {
            "easy": 0x0baa00,
            "medium": 0xeab31c,
            "hard": 0xd10606
        }[difficulty]
        body = [
            (self.localize['category'], category),
            (self.localize['difficulty'], self.localize[difficulty]),
            (self.localize['type'], self.localize[type_]),
            (self.localize['question'], question, False),
            (self.localize['choices'], choice_str, False)
        ]
        if is_multiple:
            choices, answer = self.__generate_choices(correct, incorrect)
            correct_str = answer + '. ' + correct
            for choice in choices:
                body += [
                    (choice[0], choice[1])
                ]
        else:
            answer = correct[:1]
            correct_str = correct
        self.embed = build_embed(body, colour)
        self.answer = answer
        self.answer_str = correct_str
        self.difficulty = difficulty

    @staticmethod
    def __generate_choices(correct, incorrect):
        """
        Generate choices based on the correct and incorrect answers
        :param correct: the correct answer
        :param incorrect: the incorrects answers
        :return: ([list of strings representing the choices], correct answer letter)
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

    @staticmethod
    def __trivia_no_arg_response(message):
        """
        Handles the case where trivia command didnt get any arguments
        :param message: the discord message the user responded with
        :return: (the response string for the bot, proceed)
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

    def __set__trivia_bet(self):
        """
        Handles the case where the user placed a bet on the trivia game
        :raises: TransferError if the user doesnt have enough money
        """
        amount = self.kwargs['amount'] if 'amount' in self.kwargs else 0
        if amount > 0:
            transfer_balance(self.bot.conn, self.bot.cur, self.author.id, self.bot.user.id, amount)
        self.amount = amount


def trivia_handle_bet(conn, cur, correct, difficulty,
                      amount, user_id, bot_id, localize):
    """
    Handles the case where the user placed a bet on the trivia game and the
    result has been determined.
    :param conn: the db connection
    :param cur: the db cursor
    :param correct: if the user got the answer correct
    :param difficulty: the game difficulty
    :param amount: the amount of bet the user placed
    :param user_id: the user id
    :param bot_id: the bot id
    :param localize: the localization strings
    :return: the bot response string
    """
    if correct:
        multiplier = {
            "easy": 0.5,
            "medium": 1,
            "hard": 2
        }[difficulty]
        price = round(amount * multiplier)
        delta = price
        transfer_balance(conn, cur, bot_id, user_id, amount + price, False)
    else:
        delta = amount
    key = 'trivia_correct_balance' if correct else 'trivia_wrong_balance'
    return localize[key].format(delta, get_balance(cur, user_id))


async def trivia_args_proceed(ctx, args, bot, trivia_api):
    """
    Check for empty user arguments for the irivia command
    :param ctx: the discord context
    :param args: the arguments the user passed in
    :param bot: the bot
    :return: True if the command can proceed,
    False if the command should terminate
    """
    localize = bot.get_language_dict(ctx)
    author = ctx.message.author
    prefix = get_prefix(bot.cur, ctx.message.server, bot.default_prefix)
    proceed = True
    if not args:
        await bot.say(localize['trivia_no_args'])
        resp = await bot.wait_for_message(5, author=author)
        prompt, proceed = trivia_no_arg_response(resp)
        if prompt is not None:
            out = localize[prompt]
            if prompt == 'trivia_help':
                def f(x):
                    return '\n'.join(list(x.__members__))

                out = out.format(f(Category), f(Diffculty), f(Type), prefix)
                await bot.say(localize['help_sent'])
                await bot.whisper(out)
            else:
                await bot.say(out)
    if proceed:
        await trivia_kwargs_proceed(ctx, args, bot, localize, prefix,
                                    trivia_api)


async def trivia_kwargs_proceed(ctx, args, bot, localize, prefix, trivia_api):
    """
    Generates trivia data and kwargs from the args the user passed in
    :param args: the args the user passed in
    :param bot: the bot
    :param localize: the localization strings
    :param trivia_api: the trovoa api
    :param prefix: the bot prefix
    :return: (trivia_data, kwargs)
    """
    try:
        kwargs = parse_trivia_arguments(args)
    except ArgumentError:
        await bot.say(localize['trivia_bad_args'].format(prefix))
        return None
    trivia_data = get_trivia_data(kwargs, trivia_api)
    if trivia_data is None:
        await bot.say(localize['trivia_error'])
        return None
    await trivia_bet_proceed(ctx, bot, kwargs, localize, trivia_data)


async def trivia_bet_proceed(ctx, bot, kwargs, localize, trivia_data):
    """
    Find the amount of bet the user placed
    :param bot: the bot
    :param kwargs: the kwargs parsed from args user passed in
    :param localize: the localization strings
    :return: the amount of bet the user placed
    """
    author = ctx.message.author
    try:
        bet = trivia_bet(kwargs, bot.conn, bot.cur, author.id, bot.user.id)
        await handle_user_answer(bot, bet, localize, author, trivia_data)
    except TransferError:
        await bot.say(localize['low_balance'].format(
            get_balance(bot.cur, author.id)))
        return None


async def handle_user_answer(bot, bet, localize, author, trivia_data):
    """
    Handle the user answer
    :param localize: the localization strings
    :param bot: the bot
    :param bet: the amount of bet the user placed
    :param trivia_data: the trivia data
    :param author: the message author
    :return: True if the user answer is correct else False
    """
    embed, answer, answer_str, difficulty = format_trivia_question(
        trivia_data, localize
    )
    await bot.say(embed=embed)
    user_answer = await bot.wait_for_message(10, author=author)
    if user_answer is None:
        await bot.say(localize['trivia_timeount'].format(answer_str))
        correct = False
    elif user_answer.content.upper() != answer:
        await bot.say(localize['trivia_wrong'].format(answer_str))
        correct = False
    else:
        await bot.say(localize['trivia_correct'])
        correct = True
    if bet > 0:
        await bot.say(
            trivia_handle_bet(
                bot.conn, bot.cur, correct,
                difficulty, bet, author.id, bot.user.id, localize
            )
        )
