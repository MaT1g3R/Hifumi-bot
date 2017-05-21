"""
Functions for Utilities commands
"""
from json import JSONDecodeError

from requests import get


def number_fact(num, not_found_msg, bad_num_msg, header):
    """
    Find a fact about a number
    :param num: the number
    :param not_found_msg: message if fact is not found
    :param bad_num_msg: message if the number isnt valid
    :param header: the header for the return string
    :return: a string representation for the fact
    """
    try:
        if num != 'random':
            num = int(num)
    except ValueError:
        return bad_num_msg
    url = f'http://numbersapi.com/{num}?json=true'
    while True:
        try:
            res = get(url).json()
            break
        except JSONDecodeError:
            continue
    found = res['found']
    return header.format(res['number']) + res['text'] if found \
        else not_found_msg
