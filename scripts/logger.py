from logging import FileHandler, Formatter, INFO, StreamHandler, getLogger
from pathlib import Path
from sys import stdout

from colorlog import ColoredFormatter

CONSOLE_FORMAT = '%(asctime)s %(log_color)s%(levelname)s %(name)s: ' \
                 '%(message)s'
FILE_FORMAT = '%(asctime)s %(levelname)s %(name)s: %(message)s'


def setup_logging(start_time, path: Path):
    """
    Set up logging
    :param start_time: the start time of the log
    :param path: the path to the log folder
    :return: the logger object
    """
    logger = getLogger()
    logger.setLevel(INFO)
    logger.addHandler(get_file_handler(path, start_time))
    return logger


def get_file_handler(path: Path, start_time):
    """
    Get a file handler for logging
    :param path: the log file path
    :param start_time: the start time
    :return: the file handler
    """
    handler = FileHandler(
        filename=path.joinpath('{}.log'.format(int(start_time))),
        encoding='utf-8',
        mode='w+'
    )
    handler.setFormatter(Formatter(FILE_FORMAT))
    return handler


def get_console_handler():
    """
    Get a colourful console handler
    :return: the console handler
    """
    console = StreamHandler(stdout)
    console.setFormatter(
        ColoredFormatter(
            CONSOLE_FORMAT,
            datefmt='%y-%m-%d %H:%M:%S',
            reset=True,
            log_colors={
                'DEBUG': 'cyan',
                'INFO': 'blue',
                'WARNING': 'yellow',
                'ERROR': 'red',
                'CRITICAL': 'red,bg_white',
            },
            secondary_log_colors={},
            style='%'
        )
    )
    return console
