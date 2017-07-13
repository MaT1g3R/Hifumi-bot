"""
The main run file.
"""
from asyncio import get_event_loop, set_event_loop_policy
from sys import argv

from uvloop import EventLoopPolicy
from autoclean import autoclean
from cogs import bot_info, testing, channel_reader, nsfw, roles, moderation
from config.settings import TOKEN, SHARD_COUNT, SHARD_ID, SHARDED
from core.discord_functions import get_prefix
import core.logger as logger
from shell.hifumi import Hifumi

from bot import Hifumi, version_info as v
from cogs import *


def run(args):
    set_event_loop_policy(EventLoopPolicy())
    loop = get_event_loop()
    try:
        shard_id = int(args[-1])
    except ValueError:
        shard_id = 0
    version = f'{v.releaselevel} {v.major}.{v.minor}.{v.micro}'
    if v.serial > 0:
        version += f'-{v.serial}'
    bot = loop.run_until_complete(Hifumi.get_bot(version, shard_id))
    cogs = [
        BotInfo(bot),
        ChannelReader(bot),
        Currency(bot),
        Fun(bot),
        Interactions(bot),
        Moderation(bot),
        Nsfw(bot),
        OwnerOnly(bot),
        Roles(bot),
        Tags(bot),
        Utilities(bot)
    ]
    bot.start_bot(cogs)

if __name__ == '__main__':
    try:
        run(argv)
        bot.start_bot(cogs, TOKEN)
    except (UnicodeEncodeError, UnicodeDecodeError): # If locales are not returned
        logger.error("Hifumi startup error:\n"
                     "\nLocales failed to load because your system does not support "
                     "UTF-8/Unicode encoding. Please read the docs (Troubleshooting "
                     "section) to know how to fix this problem. Exit code: 1")
        exit(1)
