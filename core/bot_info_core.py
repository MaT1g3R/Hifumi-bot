"""
Core fuctions for BotInfo cog
"""
import math
import resource
import sys
import time
from os.path import join
from threading import Timer

from discord import ChannelType, version_info

from core.file_io import read_all_files, read_json, write_json
from core.helpers import combine_dicts, get_distro
from core.discord_functions import build_embed, get_prefix
from config.settings import NAME, DEVS, HELPERS, COLOUR, SUPPORT, TWITTER, WEBSITE


def time_elapsed(start_time):
    """
    Get the time elapsed from start_time in a h:mm:ss format
    :param start_time: the start time, in seconds
    :return: time elapsed from start_time in a h:mm:ss format
    :rtype: str
    """
    time_elapsed_ = int(time.time() - start_time)
    hours = math.floor(time_elapsed_ / (60 * 60))
    time_elapsed_ -= hours * 3600
    minutes = math.floor(time_elapsed_ / 60)
    time_elapsed_ -= minutes * 60
    minutes_str = str(minutes) if minutes >= 10 else '0' + str(minutes)
    seconds_str = str(time_elapsed_) if time_elapsed_ >= 10 \
        else '0' + str(time_elapsed_)
    days = ' ({} day(s))'.format(math.floor(hours / 24))
    return '{}:{}:{}'.format(str(hours), minutes_str, seconds_str) + days


def generate_shard_info(bot):
    """
    Generates the shard info for a given shard
    :param bot: the bot
    :return: the shard info of the bot
    """
    servers = bot.servers
    members = bot.get_all_members()
    channels = bot.get_all_channels()
    voice = bot.voice_clients
    server_count = len([s for s in servers])
    user_count = len([u for u in members])
    text_channel_count = len(
        [c for c in channels if c.type == ChannelType.text])
    voice_count = len([v for v in voice])
    ram = float(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024)
    return {
        'ram': ram,
        'server_count': server_count,
        'user_count': user_count,
        'text_channel_count': text_channel_count,
        'voice_count': voice_count,
        'logged_in': bot.is_logged_in()
    }


def update_shard_info(bot):
    """
    Updates the bot shard info every second
    :param bot: the bot
    """
    Timer(1, update_shard_info, args=bot).start()
    shard_id = bot.shard_id
    file_name = join('data', 'shard_info', 'shard_{}.json'.format(shard_id))
    content = generate_shard_info(bot)
    write_json(open(file_name, 'w+'), content)


def get_all_shard_info():
    """
    Get the sum of all shard_info
    :return: The sum of all shard_info minus logged_in
    """
    files = [
        f for f in read_all_files(join('data', 'shard_info'))
        if f.endswith('.json')]
    dicts = []
    for file in files:
        res = read_json(open(file))
        if res['logged_in']:
            del res['logged_in']
            dicts.append(res)
    return combine_dicts(dicts)


def build_info_embed(ctx, bot):
    """
    build the info embed
    :param ctx: the discord context object
    :param bot: the bot object
    :return: the info embed
    """
    shard_stat = generate_shard_info(bot)
    total_stat = get_all_shard_info()
    user = bot.user
    author = {'name': user.name, 'icon_url': '{0.avatar_url}'.format(user)}

    shard_ram = shard_stat['ram']
    total_ram = total_stat['ram'] / 1024
    shard_server = shard_stat['server_count']
    total_server = total_stat['server_count']
    shard_user = shard_stat['user_count']
    total_user = total_stat['user_count']
    shard_text = shard_stat['text_channel_count']
    total_text = total_stat['text_channel_count']
    shard_voice = shard_stat['voice_count']
    total_voice = total_stat['voice_count']

    body = [
        (NAME, 'Stats order are shown as shard/general.', False),
        ('RAM used', '{0:.2f}MB/{0:.2f}GB'.format(shard_ram, total_ram)),
        ('Uptime', time_elapsed(bot.start_time)),
        ('Python version', sys.version[:5]),
        ('Library',
         'Discord.py v{}.{}.{}'.format(
             version_info.major, version_info.minor, version_info.micro)),
        ('System', get_distro()),
        ('Developers', '\n'.join(DEVS)),
        ('Helper', '\n'.join(HELPERS)),
        ('Servers', '{}/{}'.format(shard_server, total_server)),
        ('Users', '{}/{}'.format(shard_user, total_user)),
        ('Text channels', '{}/{}'.format(shard_text, total_text)),
        ('Voice channels', '{}/{}'.format(shard_voice, total_voice)),
        ('Sharding',
         '{}/{}'.format(str(bot.shard_id + 1), str(bot.shard_count)))
    ]
    footer = 'For support please type {0}support. ' \
             'Keep Hifumi alive doing {0}donate. ' \
             'Open source can be found with {0}git.'\
        .format(get_prefix(bot, ctx.message))

    return build_embed(body, COLOUR, author=author, footer=footer)


def handle_support():
    """
    build the message for supoort command
    :return: the support string
    """
    return "Looking for support? Here's our support server (recommendable): " \
           + SUPPORT + '\n\nAnd also our social networks:\nTwitter: ' \
           + TWITTER + '\nWebsite: ' + WEBSITE
