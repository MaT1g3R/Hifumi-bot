"""
The main run file.
"""
from asyncio import get_event_loop, set_event_loop_policy
from sys import argv

from colorama import init
from uvloop import EventLoopPolicy

from bot import Hifumi
from cogs import *
from config import Config


async def run(args, loop_):
    init()
    config = Config()
    try:
        shard_id = int(args[-1])
    except ValueError:
        shard_id = 0
    bot = Hifumi(config, shard_id, loop_)
    cogs = [BotInfo(bot), OwnerOnly(bot), ChannelReader(bot), Nsfw(bot),
            Roles(bot), Moderation(bot), Currency(bot), Utilities(bot),
            Music(bot)]

    await bot.start_bot(cogs)


if __name__ == '__main__':
    try:
        set_event_loop_policy(EventLoopPolicy())
        loop = get_event_loop()
        loop.run_until_complete(run(argv, loop))
    except KeyboardInterrupt:
        exit(0)
