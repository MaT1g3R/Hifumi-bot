import logging
import time
from pathlib import Path
from sys import stdout

from colorlog import ColoredFormatter

CONSOLE_FORMAT = '\n%(asctime)s:%(log_color)s%(levelname)s:%(name)s: ' \
                 '\033[0m%(message)s\n'
FILE_FORMAT = '\n%(asctime)s:%(levelname)s:%(name)s: %(message)s\n'


def setup_logging(start_time, path: Path):
    """
    Set up logging
    :param start_time: the start time of the log
    :param path: the path to the log folder
    :return: the logger object
    """
    logger = logging.getLogger('discord')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(get_file_handler(path, start_time))
    return logger


def get_file_handler(path: Path, start_time):
    """
    Get a file handler for logging
    :param path: the log file path
    :param start_time: the start time
    :return: the file handler
    """
    handler = logging.FileHandler(
        filename=path.joinpath('{}.log'.format(int(start_time))),
        encoding='utf-8',
        mode='w+'
    )
    handler.setFormatter(logging.Formatter(FILE_FORMAT))
    return handler


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
    console.setLevel(logging.WARNING)
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
