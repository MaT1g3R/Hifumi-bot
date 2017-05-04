"""
The main run file.
"""
from os.path import join

from cogs import bot_info, testing, channel_reader, nsfw
from config.settings import TOKEN
from core.data_controller import DataController
from core.discord_functions import get_prefix
from shell.hifumi import Hifumi

if __name__ == '__main__':
    d = DataController(join('data', 'hifumi_db'))
    bot = Hifumi(get_prefix, d)
    cogs = [bot_info.BotInfo(bot), testing.Testing(bot),
            channel_reader.ChannelReader(bot), nsfw.Nsfw(bot)]

    bot.start_bot(cogs, TOKEN)
