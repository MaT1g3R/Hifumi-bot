"""
Useful helper functions/classes
"""
import re
from _codecs import decode
from collections import Iterable
from datetime import date, timedelta
from pathlib import Path
from platform import platform
from random import choice
from subprocess import PIPE, Popen, STDOUT
from typing import Collection, List, Sequence


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


def suplement_dict(parent: dict, child: dict):
    """
    Add all values in parent into child if child doesnt have the key
    :param parent: the parent dict
    :param child: the child dict
    :return: the child dict with added values
    """
    child = dict(child)
    for key, val in parent.items():
        if key not in child:
            child[key] = val
    return child


def get_system_name():
    """
    You system name.
    """
    res = platform()
    regex = re.compile('[Ww]ith-.*')
    res = regex.findall(res)[0] \
        .lower().replace('-', ' ').replace('with', '').title()
    return res.strip()


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


def dict_has_empty(d: dict):
    """
    Check if a dict has empty or None values
    :param d: the input dict
    :return: True if it has an empty or None value
    >>> dict_has_empty({'d': ''})
    True
    >>> dict_has_empty({1: 'asd', 2: {2: ''}})
    True
    >>> dict_has_empty({1: 'asd', 2: {2: []}})
    True
    >>> dict_has_empty({1: 'asd', 2: {2: None}})
    True
    >>> dict_has_empty({1: 'asd', 2: {2: 'bar'}})
    False
    """
    for key, val in d.items():
        if isinstance(val, dict) and dict_has_empty(val):
            return True
        if (not val or val is None) and not isinstance(val, int):
            return True
    return False


def get_date(diff=0):
    """
    Return a date in YYYYMMDD format
    :param diff: the amount of days to go back, 0 for today
    :return: yesterday's date in YYYYMMDD format
    """
    yesterday = date.today() - timedelta(diff)
    return yesterday.strftime('%Y/%m/%d')


def get_time_elapsed(start, finish):
    """
    Get the time elapsed between start time and finish time
    :param start: the start time
    :param finish: the finish time
    :return: (days, hours, minutes, seconds) elapsed
    :rtype: tuple
    """
    days, seconds = divmod(finish - start, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    return days, hours, minutes, seconds


def assert_types(values: Sequence, types, ignore_none: bool):
    """
    Check lengh and types match for a Sequence, NoneType is ignored
    :param values: the Sequence to be checked
    :param types: the expected Types
    :param ignore_none: if False will raise AssertionError when a NoneType
    is in the values, if True it will be ignored
    """
    if isinstance(types, type):
        for v in values:
            assert (v is None and ignore_none) or isinstance(v, types)
    else:
        assert len(values) == len(types)
        for v, t in zip(values, types):
            assert (v is None and ignore_none) or isinstance(v, t)


def random_word(length: int, source: Collection):
    """
    Generate a random word.
    :param length: the length of the word.
    :param source: the source of characters the word can choose from.
    :return: a random word of length of <length>
    """
    return ''.join(choice(source) for _ in range(length))


def flatten(in_) -> list:
    """
    Flaten a input list/tuple into a list
    :param in_: the input
    :return: a flattened list of the input
    >>> flatten(([0, 1], [2, 3], [[4, 5], 6]))
    [0, 1, 2, 3, 4, 5, 6]
    >>> flatten((['0', '1'], ['2', '34'], [[4, 5], 6]))
    ['0', '1', '2', '34', 4, 5, 6]
    >>> flatten(([None, '1'], ['2', '34'], [[4, 5], 6]))
    ['1', '2', '34', 4, 5, 6]
    """
    if in_ is None:
        return []
    elif isinstance(in_, Iterable) and not isinstance(in_, str):
        res = []
        for l in in_:
            res += flatten(l)
        return res
    else:
        return [in_]


def read_all_files(path: Path) -> List[Path]:
    """
    Reads all files in a folder
    :param path: the path to the folder
    :return: All path of the files
    :rtype: list
    """
    return [Path(Path.joinpath(f)) for f in path.iterdir() if f.is_file()]


def shell_command(cmd: str, print_output=True):
    """
    Run a shell command and prints its output to stdout
    :param cmd: the shell command
    :param print_output: if True this will print the output, if false this will
    yield the output
    """
    process = Popen(cmd, stdout=PIPE, stderr=STDOUT, shell=True)
    lines = []
    for line in process.stdout:
        res = decode(line)
        if print_output:
            print(res)
        else:
            lines.append(res)
    return lines
