"""
Functions for currency commands
"""
from collections import deque
from datetime import datetime
from random import randint, sample

from data_controller import DataManager, LowBalanceError
from data_controller.data_utils import change_balance, transfer_balance
from scripts.helpers import get_time_elapsed


async def daily(data_manager: DataManager, user_id: int, localize):
    """
    Function to handle daily command
    :param data_manager: the data manager.
    :param user_id: the user id
    :param localize: the localization strings
    :return: the daily command message
    """
    current_daily = data_manager.get_user_daily(user_id)
    first_time = current_daily is None
    delta = 500 if first_time else 200
    now = datetime.now()
    if not first_time:
        time_delta = now - current_daily
        if time_delta.days < 1:
            __, hours, minutes, seconds = get_time_elapsed(
                time_delta.total_seconds(), 86400)
            return localize['daily_come_back'].format(
                int(hours), int(minutes), int(seconds))

    await data_manager.set_user_daily(user_id, now)
    await change_balance(data_manager, user_id, delta)
    res_str = localize['daily_first_time'] if first_time \
        else localize['daily_success']
    return res_str.format(delta)


async def transfer(
        data_manager: DataManager, sender,
        receiver, amount: int, localize: dict) -> str:
    """
    Transfer x amout of money from root to receiver
    :param data_manager: the data manager.
    :param sender: the sender user
    :param receiver: the receiver user
    :param amount: the amount of transfer
    :param localize: the localize strings
    :return: the result message
    """
    new_sender, new_receiver = await transfer_balance(
        data_manager, int(sender.id), int(receiver.id), amount)
    return localize['transfer_success'].format(
        amount, receiver.display_name, new_sender, new_receiver
    )


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


async def determine_slot_result(
        data_manager: DataManager, user_id: int, localize, r1, r2, r3, amount):
    """
    determine the slot game result and give/take away money from the user
    :param data_manager: the data manager.
    :param user_id: the user id
    :param localize: the localization strings
    :param r1: result 1
    :param r2: result 2
    :param r3: result 3
    :param amount: the amount of bet
    :return: the resulting string
    """
    if r1 == r2 == r3:
        delta = amount * 3
        await change_balance(data_manager, user_id, delta)
        res = localize['slots_win'].format(delta - amount)
    elif r1 != r2 and r1 != r3 and r2 != r3:
        res = localize['slots_loose'].format(amount)
    else:
        res = localize['slots_draw']
        await change_balance(data_manager, user_id, amount)
    return res + '\n' + localize['new_balance'].format(
        data_manager.get_user_balance(user_id)
    )
