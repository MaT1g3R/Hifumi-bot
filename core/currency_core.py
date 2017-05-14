"""
Functions for currency commands
"""
from time import time

from core.data_controller import get_daily, set_daily, change_balance
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
            hours, minutes, seconds = get_time_elapsed(0, time_delta)[1:]
            return localize['daily_come_back'].format(hours, minutes, seconds)
    set_daily(conn, cur, user_id)
    change_balance(conn, cur, user_id, delta)
    res_str = localize['daily_first_time'] if first_time \
        else localize['daily_success']
    return res_str.format(delta)
