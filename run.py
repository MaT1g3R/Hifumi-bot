"""
The main run file.
"""
from colorama import init

import core.logger as logger
from cogs import bot_info, testing, channel_reader, nsfw, roles, moderation
from config.settings import TOKEN, SHARD_COUNT, SHARD_ID, SHARDED
from core.discord_functions import get_prefix
from shell.hifumi import Hifumi

if __name__ == '__main__':
    try:
        init()
        if SHARDED:
            bot = Hifumi(get_prefix, shard_count=SHARD_COUNT, shard_id=SHARD_ID)
        else:
            bot = Hifumi(get_prefix)
        cogs = [bot_info.BotInfo(bot), testing.Testing(bot),
                channel_reader.ChannelReader(bot), nsfw.Nsfw(bot),
                roles.Roles(bot),
                moderation.Moderation(bot)]

        bot.start_bot(cogs, TOKEN)
    except (UnicodeEncodeError, UnicodeDecodeError):
        # If locales are not returned
        logger.error(
            "Hifumi startup error:\n\nLocales failed to load because your "
            "system does not support UTF-8/Unicode encoding. "
            "Please read the docs (Troubleshooting section) "
            "to know how to fix this problem. Exit code: 1"
        )
        exit(1)
