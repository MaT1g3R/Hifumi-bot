"""
The main run file.
"""
from asyncio import get_event_loop, set_event_loop_policy
from sys import argv

from uvloop import EventLoopPolicy

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
    run(argv)