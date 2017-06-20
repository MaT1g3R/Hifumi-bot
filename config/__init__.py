from os import name
from platform import machine, platform
from sys import platform as pl, version_info

from .config import Config

IS_WINDOWS = name == "nt"
IS_MAC = pl == "darwin"
IS_LINUX = platform().lower().startswith("linux") or name == "posix"
SYSTEM_OK = IS_WINDOWS or IS_MAC or IS_LINUX
IS_64BIT = machine().endswith("64")
PYTHON_OK = version_info >= (3, 6)

__all__ = ['Config', 'IS_64BIT', 'IS_LINUX', 'IS_MAC', 'IS_WINDOWS',
           'SYSTEM_OK', 'PYTHON_OK']
