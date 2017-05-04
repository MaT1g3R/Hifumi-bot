"""
Core fuctions for BotInfo cog
"""
import math
import platform
import resource
import time
from os.path import join

from discord import ChannelType, version_info

from config.settings import NAME, DEVS, HELPERS, COLOUR
from core.discord_functions import build_embed, get_prefix
from core.file_io import read_all_files, read_json
from core.helpers import combine_dicts, get_distro, comma


def time_elapsed(bot, ctx):
    """
    Get the time elapsed from start_time in a h:mm:ss format
    :param bot: the bot object
    :param ctx: the discord context
    :return: time elapsed from start_time in a h:mm:ss format
    :rtype: str
    """
    start_time = bot.start_time
    time_elapsed_ = int(time.time() - start_time)
    hours = math.floor(time_elapsed_ / (60 * 60))
    time_elapsed_ -= hours * 3600
    minutes = math.floor(time_elapsed_ / 60)
    time_elapsed_ -= minutes * 60
    minutes_str = str(minutes) if minutes >= 10 else '0' + str(minutes)
    seconds_str = str(time_elapsed_) if time_elapsed_ >= 10 \
        else '0' + str(time_elapsed_)
    day_str = bot.get_language_dict(ctx)['days']
    days = ' ({} {})'.format(math.floor(hours / 24), day_str)
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
        'logged_in': bot.is_logged_in
    }


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
    shard_server = comma(shard_stat['server_count'])
    total_server = comma(total_stat['server_count'])
    shard_user = comma(shard_stat['user_count'])
    total_user = comma(total_stat['user_count'])
    shard_text = comma(shard_stat['text_channel_count'])
    total_text = comma(total_stat['text_channel_count'])
    shard_voice = comma(shard_stat['voice_count'])
    total_voice = comma(total_stat['voice_count'])

    lan = bot.get_language_dict(ctx)
    body = [
        (NAME, lan['stats_order'], False),
        (lan['ram_used'], '{0:.2f}MB/{1:.2f}GB'.format(shard_ram, total_ram)),
        (lan['uptime'], time_elapsed(bot, ctx)),
        (lan['python_ver'], platform.python_version()),
        (lan['lib'],
         'Discord.py v{}.{}.{}'.format(
             version_info.major, version_info.minor, version_info.micro)),
        (lan['sys'], get_distro()),
        (lan['devs'], '\n'.join(DEVS)),
        (lan['helper'], '\n'.join(HELPERS)),
        (lan['servers'], '{}/{}'.format(shard_server, total_server)),
        (lan['users'], '{}/{}'.format(shard_user, total_user)),
        (lan['text_channels'], '{}/{}'.format(shard_text, total_text)),
        (lan['voice_channels'], '{}/{}'.format(shard_voice, total_voice)),
        (lan['sharding'],
         '{}/{}'.format(str(bot.shard_id + 1), str(bot.shard_count)))
    ]
    footer = lan['footer'].format(get_prefix(bot, ctx.message))

    return build_embed(body, COLOUR, author=author, footer=footer)
