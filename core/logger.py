import logging
import os
import time
from os.path import join
from sys import stdout

from colorlog import ColoredFormatter

IS_UNIX = os.name != "nt"

BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)

RESET_SEQ = "\033[0m"
COLOR_SEQ = "\033[1;%dm"
BOLD_SEQ = "\033[1m"

COLORS = {
    'WARNING': YELLOW,
    'INFO': WHITE,
    'DEBUG': BLUE,
    'CRITICAL': YELLOW,
    'ERROR': RED
}

CONSOLE_FORMAT = '\n%(asctime)s:%(log_color)s%(levelname)s:%(name)s: ' \
                 '%(message)s\n'
FILE_FORMAT = '\n%(asctime)s:%(levelname)s:%(name)s: %(message)s\n'


def setup_logging(start_time):
    """
    Set up logging
    :param start_time: the start time of the log
    :return: the logger object
    """
    logger = logging.getLogger('discord')
    handler = logging.FileHandler(
        filename=join('data', 'logs', '{}.log'.format(start_time)),
        encoding='utf-8',
        mode='w'
    )
    handler.setFormatter(logging.Formatter(FILE_FORMAT))
    logger.addHandler(handler)
    return logger


def get_console_handler():
    """
    Get a colourful console handler
    :return: the console handler
    """
    console = logging.StreamHandler(stdout)
    console.setFormatter(
        ColoredFormatter(
            CONSOLE_FORMAT,
            datefmt=None,
            reset=True,
            log_colors={
                'DEBUG': 'black,bg_blue',
                'INFO': 'black,bg_green',
                'WARNING': 'black,bg_yellow',
                'ERROR': 'black,bg_red',
                'CRITICAL': 'red,bg_white',
                'SILLY': 'black,bg_magenta'
            },
            secondary_log_colors={},
            style='%'
        )
    )
    return console


def warning(text, end=None, date=False):
    """
    Prints a yellow warning.
    At the moment it's only supported for Linux and Mac.
    """
    if date:
        text = "[" + time.strftime(
            '%Y-%m-%d %I:%M:%S %p') + "] | WARNING: " + text
    if end:
        print('\x1b[33m{}\x1b[0m'.format(text), end=end)
    else:
        print('\x1b[33m{}\x1b[0m'.format(text))


def error(text, end=None, date=False):
    """
    Prints a red error. At the moment it's only supported for Linux and Mac.
    """
    if date:
        text = "[" + time.strftime(
            '%Y-%m-%d %I:%M:%S %p') + "] | ERROR: " + text
    if end:
        print('\x1b[31m{}\x1b[0m'.format(text), end=end)
    else:
        print('\x1b[31m{}\x1b[0m'.format(text))


def info(text, end=None, date=False):
    """
    Prints a green info. At the moment it's only supported for Linux and Mac.
    """
    if date:
        text = "[" + time.strftime('%Y-%m-%d %I:%M:%S %p') + "] | INFO: " + text
    if end:
        print('\x1b[32m{}\x1b[0m'.format(text), end=end)
    else:
        print('\x1b[32m{}\x1b[0m'.format(text))


def debug(text, end=None, date=False):
    """
    Prints a blue debug. At the moment it's only supported for Linux and Mac.
    """
    if date:
        text = "[" + time.strftime(
            '%Y-%m-%d %I:%M:%S %p') + "] | DEBUG: " + text
    if end:
        print('\x1b[34m{}\x1b[0m'.format(text), end=end)
    else:
        print('\x1b[34m{}\x1b[0m'.format(text))


def silly(text, end=None, date=False):
    """
    Prints a magenta/purple silly.
    At the moment it's only supported for Linux and Mac.
    :return: A silly info.
    """
    if date:
        text = "[" + time.strftime(
            '%Y-%m-%d %I:%M:%S %p') + "] | SILLY: " + text
    if end:
        print('\x1b[35m{}\x1b[0m'.format(text), end=end)
    else:
        print('\x1b[35m{}\x1b[0m'.format(text))
