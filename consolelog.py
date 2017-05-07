import time
IS_WINDOWS = os.name == "nt"

def warning(text, end=None, date=False):
    """
    Prints a yellow warning. 
    At the moment it's only supported for Linux and Mac.
    :return: A warning.
    """
    if date:
        text = "[" + time.strftime('%Y-%m-%d %I:%M:%S %p') + "] | WARNING: " + text
    if IS_WINDOWS:
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
    :return: An error.
    """
    if date:
        text = "[" + time.strftime('%Y-%m-%d %I:%M:%S %p') + "] | ERROR: " + text
    if IS_WINDOWS:
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
    :return: An info.
    """
    if date:
        text = "[" + time.strftime('%Y-%m-%d %I:%M:%S %p') + "] | INFO: " + text
    if IS_WINDOWS:
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
    :return: A debug info.
    """
    if date:
        text = "[" + time.strftime('%Y-%m-%d %I:%M:%S %p') + "] | DEBUG: " + text
    if IS_WINDOWS:
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
    Prints a magenta/purple silly. At the moment it's only supported for Linux and Mac.
    :return: A silly info.
    """
    if date:
        text = "[" + time.strftime('%Y-%m-%d %I:%M:%S %p') + "] | SILLY: " + text
    if IS_WINDOWS:
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
