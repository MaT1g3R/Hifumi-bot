"""
Functions for currency commands
"""
from datetime import timedelta
from time import time

from core.data_controller import get_daily, set_daily, change_balance


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
    delta = 500 if current_daily is None else 200
    if current_daily is not None:
        time_delta = time() - current_daily
        if time_delta > timedelta(1).total_seconds():
            return localize
    set_daily(conn, cur, user_id)
    change_balance(conn, cur, user_id, delta)
    return localize
