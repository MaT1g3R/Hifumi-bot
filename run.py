"""
The main run file.
"""
from asyncio import set_event_loop_policy
from sys import argv

from colorama import init
from uvloop import EventLoopPolicy

from bot import Hifumi
from cogs import *
from config import Config


def run(args):
    init()
    config = Config()
    try:
        shard_id = int(args[-1])
    except ValueError:
        shard_id = 0
    bot = Hifumi(config, shard_id)
    cogs = [BotInfo(bot), ChannelReader(bot), Currency(bot), Fun(bot),
            Interactions(bot), Moderation(bot), Music(bot), Nsfw(bot),
            OwnerOnly(bot), Roles(bot), Tags(bot), Utilities(bot)]

    bot.start_bot(cogs)


if __name__ == '__main__':
    set_event_loop_policy(EventLoopPolicy())
    run(argv)
