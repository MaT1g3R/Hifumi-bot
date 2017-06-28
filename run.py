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


def run(args):
    init()
    config = Config()
    set_event_loop_policy(EventLoopPolicy())

    try:
        shard_id = int(args[-1])
    except ValueError:
        shard_id = 0
    bot = Hifumi(config, shard_id)
    cogs = [BotInfo(bot), ChannelReader(bot), Currency(bot), Fun(bot),
            Interactions(bot), Moderation(bot), Music(bot), Nsfw(bot),
            OwnerOnly(bot), Roles(bot), Tags(bot), Utilities(bot)]
    loop = get_event_loop()
    loop.run_until_complete(bot.init())
    bot.start_bot(cogs)


if __name__ == '__main__':
    run(argv)
