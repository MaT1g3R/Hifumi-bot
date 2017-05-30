"""
The main run file.
"""
from platform import python_version

from colorama import init

from cogs import *
from config import *
from launcher import is_internet_on
from scripts import logger
from shell import Hifumi

try:
    import pip  # It will not be used here but still needed
except ImportError:
    pip = None


def __run():
    init()
    if SHARDED:
        bot = Hifumi(
            shard_count=SHARD_COUNT, shard_id=SHARD_ID
        )
    else:
        bot = Hifumi()
    cogs = [BotInfo(bot), OwnerOnly(bot), ChannelReader(bot), Nsfw(bot),
            Roles(bot), Moderation(bot), Currency(bot), Utilities(bot)]

    bot.start_bot(cogs, TOKEN)


def run():
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
                     "is only supported for Windows, Mac, Linux and "
                     "Raspberry Pi. Please install one of those OS and try "
                     "again.")
        exit(1)
    elif not PYTHON_OK:
        logger.error(
            "Sorry! This Python version is not compatible. Hifumi needs "
            "Python 3.6 or higher. You have Python version {}.\n"
            .format(python_version()) +
            " Install the required version and try again.\n")
        exit(1)
    elif not pip:
        logger.error(
            "Hey! Python is installed but you are missing the pip module."
            "\nPlease reinstall Python without "
            "unchecking any option during the setup >_<")
        exit(1)
    else:
        try:
            __run()
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


if __name__ == '__main__':
    __run()
