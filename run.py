"""
The main run file.
"""
from os import name, path
from sys import platform, version_info

from colorama import init

import core.logger as logger
from cogs import bot_info, testing, channel_reader, nsfw, roles, moderation
from config.settings import TOKEN, SHARD_COUNT, SHARD_ID, SHARDED, SAFE_SHUTDOWN
from core.discord_functions import get_prefix
from launcher import is_internet_on
from shell.hifumi import Hifumi

try:
    import pip  # It will not be used here but still needed
except ImportError:
    pip = None

IS_WINDOWS = name == "nt"
IS_MAC = platform == "darwin"
IS_LINUX = platform.startswith("linux") or name == "posix"
IS_ONE_OF_BOTH = IS_WINDOWS or IS_LINUX
IS_DOCKER = IS_ONE_OF_BOTH and path.exists('.dockerenv')
SYSTEM_OK = IS_WINDOWS or IS_MAC or IS_LINUX or IS_DOCKER

PYTHON_OK = version_info >= (3, 6)

if __name__ == '__main__':
    if not is_internet_on():
        logger.error(
            "You're not connected to Internet! "
            "Please check your connection and try again."
        )
        exit(1)
    elif SAFE_SHUTDOWN:
        logger.warning(
            "Safe shutdown launched as requested in settings."
            "To startup the bot back, toggle SAFE_SHUTDOWN "
            "property to True. Exit code: 126"
        )
        exit(126)
    elif not SYSTEM_OK:
        logger.error("Sorry! This operation system is not compatible with "
                     "Hifumi's environment and might not run at all. Hifumi "
                     "is only supported for Windows, Mac, Linux, Docker and "
                     "Raspberry Pi. Please install one of those OS and try "
                     "again.")
        exit(1)
    elif not PYTHON_OK:
        logger.error(
            "Sorry! This Python version is not compatible. Hifumi needs "
            "Python 3.6 or higher. You have Python version {}.\n"
            .format(platform.python_version()) + " Install the required "
                                                 "version and try again.\n")
        exit(1)
    elif not pip:
        logger.error(
            "Hey! Python is installed but you are missing the pip module."
            "\nPlease reinstall Python without "
            "unchecking any option during the setup >_<")
        exit(1)
    else:
        try:
            init()
            if SHARDED:
                bot = Hifumi(
                    get_prefix, shard_count=SHARD_COUNT, shard_id=SHARD_ID
                )
            else:
                bot = Hifumi(get_prefix)
            cogs = [bot_info.BotInfo(bot), testing.Testing(bot),
                    channel_reader.ChannelReader(bot), nsfw.Nsfw(bot),
                    roles.Roles(bot),
                    moderation.Moderation(bot)]

            bot.start_bot(cogs, TOKEN)
        except (UnicodeEncodeError, UnicodeDecodeError):
            # If locales are not returned
            logger.warning(
                "Hifumi startup error:\n\nLocales failed to load because your "
                "system does not support UTF-8/Unicode encoding. "
                "Please read the docs (Troubleshooting section) "
                "to know how to fix this problem. Exit code: 1"
            )
            exit(1)
        except KeyboardInterrupt:
            logger.info("Hifumi has been terminated.")
        except Exception as e:
            logger.error(
                "Hifumi startup error:\n\nPython returned an exception error "
                "and this instance was triggered with exit code 1.\n\n"
                + str(e) +
                "\n\nPlease fix this and try again. If you don't know how to, "
                "check the Troubleshooting section in the Hifumi documentation "
                "and/or feel free to ask for help in official support server "
                "in Discord."
            )
            exit(1)
