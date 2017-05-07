import logging
import os
import time
from copy import copy
from os.path import join
from sys import stdout

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

CONSOLE_FORMAT = "[$BOLD%(name)-20s$RESET][%(levelname)-18s] " \
                 "%(asctime)s %(message)s ($BOLD%(filename)s$RESET:%(lineno)d)"
FILE_FORMAT = '\n%(asctime)s:%(levelname)s:%(name)s: %(message)s\n'


class ColoredFormatter(logging.Formatter):
    """
    A formatter that uses colours
    """

    def __init__(self, msg):
        """
        Initialize the formatter
        :param msg: the formatter message
        """
        logging.Formatter.__init__(self, msg)

    def format(self, record):
        """
        Formats the recoed
        :param record: the log record
        :return: the formatted text
        """
        record = copy(record)
        levelname = record.levelname
        if IS_UNIX and levelname in COLORS:
            levelname_color = \
                COLOR_SEQ % (30 + COLORS[levelname]) + levelname + RESET_SEQ
            record.levelname = levelname_color
        return logging.Formatter.format(self, record)


def formatter_message(message, use_color):
    """
    The message the formatter uses
    :param message: the message input
    :param use_color: to use colour or not
    :return: the formatter message
    """
    if use_color:
        message = message.replace("$RESET", RESET_SEQ) \
            .replace("$BOLD", BOLD_SEQ)
    else:
        message = message.replace("$RESET", "").replace("$BOLD", "")
    return message


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
        mode='w'
    )
    handler.setFormatter(logging.Formatter(FILE_FORMAT))
    console = logging.StreamHandler(stdout)
    console.setFormatter(
        ColoredFormatter(formatter_message(CONSOLE_FORMAT, IS_UNIX))
    )
    logger.addHandler(handler)
    logger.addHandler(console)
    return logger


def warning(text, end=None, date=False):
    """
    Prints a yellow warning.
    At the moment it's only supported for Linux and Mac.
    """
    if date:
        text = "[" + time.strftime(
            '%Y-%m-%d %I:%M:%S %p') + "] | WARNING: " + text
    if not IS_UNIX:
        # Normal white text because Windows shell doesn't support ANSI color :(
        if end:
            print(text, end=end)
        else:
            print(text)
    else:
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
    if not IS_UNIX:
        # Normal white text because Windows shell doesn't support ANSI color :(
        if end:
            print(text, end=end)
        else:
            print(text)
    else:
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
    if not IS_UNIX:
        # Normal white text because Windows shell doesn't support ANSI color :(
        if end:
            print(text, end=end)
        else:
            print(text)
    else:
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
    if not IS_UNIX:
        # Normal white text because Windows shell doesn't support ANSI color :(
        if end:
            print(text, end=end)
        else:
            print(text)
    else:
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
    if not IS_UNIX:
        # Normal white text because Windows shell doesn't support ANSI color :(
        if end:
            print(text, end=end)
        else:
            print(text)
    else:
        if end:
            print('\x1b[35m{}\x1b[0m'.format(text), end=end)
        else:
            print('\x1b[35m{}\x1b[0m'.format(text))
