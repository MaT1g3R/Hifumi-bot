"""
Functions for currency commands
"""
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
        return localize['transfer_fail'].format(str(e))
