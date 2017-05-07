import logging
import os
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
