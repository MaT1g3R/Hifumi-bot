"""
The main run file.
"""

from sys import argv

from colorama import init

from bot import Hifumi
from cogs import *
from config import SHARD_COUNT, TOKEN


def run(args):
    init()
    try:
        shard_id = int(args[-1])
    except ValueError:
        shard_id = 0
    bot = Hifumi(shard_count=SHARD_COUNT, shard_id=shard_id)
    cogs = [BotInfo(bot), OwnerOnly(bot), ChannelReader(bot), Nsfw(bot),
            Roles(bot), Moderation(bot), Currency(bot), Utilities(bot)]

    bot.start_bot(cogs, TOKEN)


if __name__ == '__main__':
    run(argv)
