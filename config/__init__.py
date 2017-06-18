from os import name
from platform import machine, platform
from sys import platform as pl, version_info

from .settings import BAD_WORD, COLOUR, DANBOORU_API, DANBOORU_USERNAME, \
    DEFAULT_PREFIX, DEVS, EDAMAM_API, ENABLE_CONSOLE_LOGGING, HELPERS, INVITE, \
    NAME, OWNER, SAFE_SHUTDOWN, SHARD_COUNT, SUPPORT, TOKEN, TWITTER, WEBSITE

IS_WINDOWS = name == "nt"
IS_MAC = pl == "darwin"
IS_LINUX = platform().lower().startswith("linux") or name == "posix"
SYSTEM_OK = IS_WINDOWS or IS_MAC or IS_LINUX
IS_64BIT = machine().endswith("64")
PYTHON_OK = version_info >= (3, 6)

__all__ = ['COLOUR', 'NAME', 'DEVS', 'HELPERS', 'DEFAULT_PREFIX', 'SUPPORT',
           'TWITTER', 'WEBSITE', 'TOKEN', 'INVITE', 'OWNER',
           'DANBOORU_USERNAME', 'DANBOORU_API', 'EDAMAM_API', 'BAD_WORD',
           'SHARD_COUNT', 'ENABLE_CONSOLE_LOGGING',
           'SAFE_SHUTDOWN', 'IS_WINDOWS', 'IS_MAC', 'IS_LINUX', 'SYSTEM_OK',
           'IS_64BIT', 'PYTHON_OK']
