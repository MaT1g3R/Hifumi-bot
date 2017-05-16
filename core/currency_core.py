"""
Functions for currency commands
"""
from collections import deque
from random import sample, randint
from random import shuffle
from string import ascii_uppercase
from time import time

from pytrivia import Category, Diffculty, Type

from core.data_controller import get_daily, set_daily, change_balance, \
    transfer_balance, TransferError, get_balance
from core.discord_functions import build_embed
from core.helpers import get_time_elapsed


class ArgumentError(ValueError):
    pass


def daily(conn, cur, user_id, localize):
    """
    Function to handle daily command
    :param conn: the db connection
    :param cur: the db cursor
    :param user_id: the user id
    :param localize: the localization strings
    :return: the daily command message
    """
    current_daily = get_daily(cur, user_id)
    first_time = current_daily is None
    delta = 500 if first_time else 200
    if not first_time:
        time_delta = int(time() - current_daily)
        if time_delta < 86400:
            hours, minutes, seconds = get_time_elapsed(time_delta, 86400)[1:]
            return localize['daily_come_back'].format(hours, minutes, seconds)
    set_daily(conn, cur, user_id)
    change_balance(conn, cur, user_id, delta)
    res_str = localize['daily_first_time'] if first_time \
        else localize['daily_success']
    return res_str.format(delta)


def transfer(conn, cur, root, target, amount, localize):
    """
    Transfer x amout of money from root to target
    :param conn: the db connection
    :param cur: the db cursor
    :param root: the root user
    :param target: the target user
    :param amount: the amount of transfer
    :param localize: the localize strings
    :return: the result message
    """
    try:
        transfer_balance(conn, cur, root.id, target.id, amount)
        root_balance = get_balance(cur, root.id)
        target_balance = get_balance(cur, target.id)
        return localize['transfer_success'].format(
            amount, target.display_name, root_balance, target_balance
        )
    except TransferError as e:
        return localize['low_balance'].format(str(e))


def slots_setup(emojis, lower, upper):
    """
    Return 3 random emoji dequeues and 3 random numbers
    :param emojis: the entire emoji list
    :param lower: the lower bound of the length of the random list
    :param upper: the upper bound of the length of the random list
    :return: (rand_emoji_lst, rand_emoji_lst, rand_emoji_lst,
              rand_int, rand_int, rand_int)
    :rtype: tuple
    """
    emoji_lst = sample(emojis, randint(upper // 2, upper) * 3)
    return \
        deque(sample(emoji_lst, len(emoji_lst))), \
        deque(sample(emoji_lst, len(emoji_lst))), \
        deque(sample(emoji_lst, len(emoji_lst))), \
        randint(lower, upper), randint(lower, upper), randint(lower, upper)


async def roll_slots(bot, msg, q1, q2, q3, n1, n2, n3):
    """
    Simulates playing a slot machine
    :param bot: the bot
    :param msg: the initial message the bot sent for the slot
    :param q1: the first dequeue
    :param q2: the second dequeue
    :param q3: the third dequeue
    :param n1: the first random number
    :param n2: the second random number
    :param n3: the third random number
    :return: the final result
    """
    i = max(n1, n2, n3)
    while i > 0:
        if n1 > 0:
            q1.rotate()
        if n2 > 0:
            q2.rotate()
        if n3 > 0:
            q3.rotate()
        n1, n2, n3, i = n1 - 1, n2 - 1, n3 - 1, i - 1
        await bot.edit_message(
            msg, '[ {} | {} | {} ]'.format(q1[0], q2[0], q3[0])
        )
    return q1[0], q2[0], q3[0]


def determine_slot_result(conn, cur, user_id, bot_id, localize, r1, r2, r3,
                          amount):
    """
    determine the slot game result and give/take away money from the user
    :param conn: the db connection
    :param cur: the db cursor
    :param user_id: the user id
    :param bot_id: the bot id
    :param localize: the localization strings
    :param r1: result 1
    :param r2: result 2
    :param r3: result 3
    :param amount: the amount of bet
    :return: the resulting string
    """
    if r1 == r2 == r3:
        delta = amount * 3
        change_balance(conn, cur, user_id, delta)
        res = localize['slots_win'].format(delta - amount)
    elif r1 != r2 and r1 != r3 and r2 != r3:
        delta = 0
        res = localize['slots_loose'].format(amount)
    else:
        delta = amount
        res = localize['slots_draw']
        change_balance(conn, cur, user_id, delta)
    change_balance(conn, cur, bot_id, amount - delta)
    return res + '\n' + localize['new_balance'].format(
        get_balance(cur, user_id)
    )


def parse_trivia_arguments(args):
    """
    Parse the arguments from trivia command
    :param args: the arguments passed in by the user
    :return: a dict of arguments
    :raises: ArgumentError if a bad argument is present
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


def get_trivia_data(kwargs, api):
    """
    Get trivia question based on the user input
    :param kwargs: the parsed arguments passed in by the user
    :param api: an instance of Trivia
    :return: the trivia question
    """
    category = kwargs['category'] if 'category' in kwargs else None
    type_ = kwargs['type'] if 'type' in kwargs else None
    diffculty = kwargs['diffculty'] if 'diffculty' in kwargs else None
    res = api.request(1, category, diffculty, type_)
    return res if res['response_code'] == 0 else None


def format_trivia_question(trivia_data, localize):
    """
    Format the trivia question for display
    :param trivia_data: the trivia data from the api call
    :param localize: the localization strings
    :return: a formatted string of the trivia question, and the correct answer
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
    body = [
        (localize['category'], category),
        (localize['difficulty'], localize[difficulty]),
        (localize['type'], localize[type_]),
        (localize['question'], question, False),
        (localize['choices'], choice_str, False)
    ]
    if is_multiple:
        choices, answer = __generate_choices(correct, incorrect)
        correct_str = answer + '. ' + correct
        for choice in choices:
            body += [
                (choice[0], choice[1])
            ]
    else:
        answer = correct[:1]
        correct_str = correct
    return build_embed(body, colour), answer, correct_str, difficulty


def trivia_no_arg_response(message):
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


def trivia_bet(kwargs, conn, cur, user_id, bot_id):
    """
    Handles the case where the user placed a bet on the trivia game
    :param kwargs: the kwargs parsed from the user input
    :param conn: the db connection
    :param cur: the db cursor
    :param user_id: the user id
    :param bot_id: the bot id
    :return: the amount of bet
    :raises: TransferError if the user doesnt have enough money
    """
    amount = kwargs['amount'] if 'amount' in kwargs else 0
    if amount > 0:
        transfer_balance(conn, cur, user_id, bot_id, amount)
    return amount


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


async def trivia_args_proceed(args, localize, author, prefix, bot):
    """
    Check for empty user arguments for the irivia command
    :param args: the arguments the user passed in
    :param localize: the localization strings
    :param author: the message author
    :param prefix: the bot prefix
    :param bot: the bot
    :return: True if the command can proceed,
    False if the command should terminate
    """
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
    return proceed


async def trivia_kwargs_proceed(args, bot, localize, trivia_api, prefix):
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
        return None, None
    trivia_data = get_trivia_data(kwargs, trivia_api)
    if trivia_data is None:
        await bot.say(localize['trivia_error'])
    return trivia_data, kwargs


async def trivia_bet_proceed(bot, kwargs, localize, user_id):
    """
    Find the amount of bet the user placed
    :param bot: the bot
    :param kwargs: the kwargs parsed from args user passed in
    :param localize: the localization strings
    :param user_id: the user id
    :return: the amount of bet the user placed
    """
    try:
        bet = trivia_bet(kwargs, bot.conn, bot.cur, user_id, bot.user.id)
    except TransferError:
        await bot.say(localize['low_balance'].format(
            get_balance(bot.cur, user_id)))
        bet = None
    return bet


async def handle_user_answer(localize, bot, user_answer, answer, answer_str):
    """
    Handle the user answer
    :param localize: the localization strings
    :param bot: the bot
    :param user_answer: the user answer
    :param answer: the correct answer
    :param answer_str: the string representation of the correct answer
    :return: True if the user answer is correct else False
    """
    if user_answer is None:
        await bot.say(localize['trivia_timeount'].format(answer_str))
        return False
    elif user_answer.content.upper() != answer:
        await bot.say(localize['trivia_wrong'].format(answer_str))
        return False
    else:
        await bot.say(localize['trivia_correct'])
        return True
