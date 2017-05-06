"""
Useful helper functions
"""
import logging
import re
from os.path import join


def combine_dicts(dicts):
    """
    combine (nested) dictionaries with numbers as values,
    assuming same key in all dicts maps to the same data type
    :param dicts: an iterable of dicts
    :return: the combined dict
    >>> d1 = {'a': 1, 'b': 2}
    >>> d2 = {'a': 1, 'c':1}
    >>> d3 = combine_dicts((d1, d2))
    >>> d3 == {'a': 2, 'b': 2, 'c': 1}
    True
    >>> d4 = {'d1': d1, 'd2': d2}
    >>> d5 = {'d1': d1, 'c':100}
    >>> d6 = combine_dicts((d4, d5))
    >>> d6 == {'d1': {'a': 2, 'b': 4}, 'd2': d2, 'c': 100}
    True
    >>> combine_dicts((d1, d2, d3)) == {'a': 4, 'b': 4, 'c': 2}
    True
    >>> combine_dicts((d4, d5, d6)) == \
    {'d1':{'a': 4,'b':8}, 'd2': {'a':2,'c':2}, 'c': 200}
    True
    """
    if len(dicts) == 0:
        return None
    elif len(dicts) == 1:
        return dicts[0]
    elif len(dicts) == 2:
        d1, d2 = dicts
        res = {}
        all_keys = set(list(d1.keys()) + list(d2.keys()))
        for key in all_keys:
            if key in d1 and key in d2:
                if isinstance(d1[key], dict):
                    res[key] = combine_dicts((d1[key], d2[key]))
                else:
                    a, b = d1[key], d2[key]
                    if a is not None and b is not None:
                        s = a + b
                    elif a is not None:
                        s = a
                    else:
                        s = b
                    res[key] = s
            elif key in d1:
                res[key] = d1[key]
            elif key in d2:
                res[key] = d2[key]
        return res
    elif len(dicts) > 2:
        l = len(dicts)
        return combine_dicts(
            (combine_dicts(dicts[:l // 2]), combine_dicts(dicts[l // 2:])))


def get_distro():
    """
    You linux distro version info.
    """
    raw = ' '.join((open(join('/', 'etc', 'issue'))).readlines())
    res = ''
    for s in raw:
        if s != '\\':
            res += s
        else:
            break
    while res.endswith(' '):
        res = res[:-1]

    return res


def strip_letters(s: str):
    """
    Strip all letters from a input string and leave only the numbers
    :param s: the input
    :return: the stripped string
    :rtype: list
    >>> strip_letters('You are on cooldown. Try again in 2.16s')
    ['2.16']
    """
    regex = re.compile('[-.0-9]+')
    return [r for r in regex.findall(s) if r != '.']


def comma(val):
    """
    Return a comma seprated number
    :param val: the number
    :return: the comma seprated number
    """
    return "{:,}".format(int(val))


def setup_logging(start_time):
    """
    Set up logging
    :param start_time: the start time of the log
    :return: the logger object
    """
    logger = logging.getLogger('discord')
    logger.setLevel(logging.DEBUG)
    handler = logging.FileHandler(
        filename=join('data', 'logs', '{}.log'.format(start_time)),
        encoding='utf-8',
        mode='w')
    handler.setFormatter(
        logging.Formatter(
            '\n%(asctime)s:%(levelname)s:%(name)s: %(message)s\n'))
    logger.addHandler(handler)
    return logger
