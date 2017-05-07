"""
The main run file.
"""
from cogs import bot_info, testing, channel_reader, nsfw, roles, moderation
from config.settings import TOKEN, SHARD_COUNT, SHARD_ID, SHARDED
from core.discord_functions import get_prefix
from shell.hifumi import Hifumi
from autoclean import autoclean


if __name__ == '__main__':
    autoclean()
    if SHARDED:
        bot = Hifumi(get_prefix, shard_count=SHARD_COUNT, shard_id=SHARD_ID)
    else:
        bot = Hifumi(get_prefix)
    cogs = [bot_info.BotInfo(bot), testing.Testing(bot),
            channel_reader.ChannelReader(bot), nsfw.Nsfw(bot), roles.Roles(bot),
            moderation.Moderation(bot)]

    bot.start_bot(cogs, TOKEN)
