"""
Functions for currency commands
"""
from collections import deque
from random import sample, randint
from time import time

from core.data_controller import get_daily, set_daily, change_balance, \
    transfer_balance, TransferError, get_balance
from core.helpers import get_time_elapsed


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
