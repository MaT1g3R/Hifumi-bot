"""
Core fuctions for BotInfo cog
"""
import math
import platform
import resource
import time
from os.path import join

from discord import ChannelType, version_info

from config.settings import NAME, DEVS, HELPERS, COLOUR, SHARDED
from core.discord_functions import build_embed, get_prefix
from core.file_io import read_all_files, read_json
from core.helpers import combine_dicts, get_system_name, comma


def time_elapsed(start_time, day_str):
    """
    Get the time elapsed from start_time in a hh:mm:ss format
    :param start_time: the start time for the elapsed time calculation
    :param day_str: the localization string that says "day"
    :return: time elapsed from start_time in a hh:mm:ss format
    :rtype: str
    """
    time_elapsed_ = int(time.time() - start_time)
    days = math.floor(time_elapsed_ / (60 * 60 * 24))
    time_elapsed_ -= days * 60 * 60 * 24
    hours = math.floor(time_elapsed_ / (60 * 60))
    time_elapsed_ -= hours * 3600
    minutes = math.floor(time_elapsed_ / 60)
    time_elapsed_ -= minutes * 60
    minutes_str = str(minutes) if minutes >= 10 else '0' + str(minutes)
    seconds_str = str(time_elapsed_) if time_elapsed_ >= 10 \
        else '0' + str(time_elapsed_)
    days = ' ({} {})'.format(days, day_str)
    return '{}:{}:{}'.format(str(hours), minutes_str, seconds_str) + days


def generate_shard_info(*, servers, members, channels, voice, logged_in):
    """
    Generates the shard info for a given shard

    :param servers: the list of servers the bot is in

    :param members: the list of members in all the servers the bot is in

    :param channels: the lsit of channels the bot is in

    :param voice: the list of voice channels the bot is in

    :param logged_in: is the bot logged in

    :return: the shard info of the bot
    """
    server_count = len(list(servers))
    user_count = len(list(members))
    text_channel_count = len(
        [c for c in channels if c.type == ChannelType.text])
    voice_count = len(list(voice))
    ram = float(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024)
    return {
        'ram': ram,
        'server_count': server_count,
        'user_count': user_count,
        'text_channel_count': text_channel_count,
        'voice_count': voice_count,
        'logged_in': logged_in
    }


def get_all_shard_info(path=join('data', 'shard_info')):
    """
    Get the sum of all shard_info
    :param path: the path that points to the shard_info folder
    :return: The sum of all shard_info minus logged_in
    """
    files = [
        f for f in read_all_files(path)
        if f.endswith('.json')]
    dicts = []
    for file in files:
        res = read_json(open(file))
        if res['logged_in']:
            del res['logged_in']
            dicts.append(res)
    return combine_dicts(dicts)


def build_info_embed(ctx, bot, path=join('data', 'shard_info')):
    """
    build the info embed
    :param ctx: the discord context object
    :param bot: the bot object
    :param path: the path that points to the shard_info folder
    :return: the info embed
    """
    shard_stat = generate_shard_info(
        servers=bot.servers,
        members=bot.get_all_members(),
        channels=bot.get_all_channels(),
        voice=bot.voice_clients,
        logged_in=bot.is_logged_in
    )
    total_stat = get_all_shard_info(path)
    user = bot.user
    author = {'name': user.name, 'icon_url': '{0.avatar_url}'.format(user)}
    lan = bot.get_language_dict(ctx)

    shard_ram = shard_stat['ram']
    shard_server = comma(shard_stat['server_count'])
    shard_user = comma(shard_stat['user_count'])
    shard_text = comma(shard_stat['text_channel_count'])
    shard_voice = comma(shard_stat['voice_count'])

    ram_str = '{0:.2f}MB'.format(shard_ram)
    server_str = shard_server
    users_str = shard_user
    text_str = shard_text
    voice_str = shard_voice
    if SHARDED:
        total_ram = total_stat['ram'] / 1024
        total_server = comma(total_stat['server_count'])
        total_user = comma(total_stat['user_count'])
        total_text = comma(total_stat['text_channel_count'])
        total_voice = comma(total_stat['voice_count'])
        ram_str += '/{0:.2f}GB'.format(total_ram)
        server_str += '/' + total_server
        users_str += '/' + total_user
        text_str += '/' + total_text
        voice_str += '/' + total_voice

    body = [(NAME, lan['stats_order'], False)] if SHARDED else []
    body += [
        (lan['ram_used'], ram_str),
        (lan['uptime'], time_elapsed(bot.start_time, lan['days'])),
        (lan['python_ver'], platform.python_version()),
        (lan['lib'],
         'Discord.py v{}.{}.{}'.format(
             version_info.major, version_info.minor, version_info.micro)),
        (lan['sys'], get_system_name())
    ]
    if DEVS:
        body += [(lan['devs'], '\n'.join(DEVS))]
    if HELPERS:
        body += [(lan['helper'], '\n'.join(HELPERS))]
    body += [
        (lan['servers'], server_str),
        (lan['users'], users_str),
        (lan['text_channels'], text_str),
        (lan['voice_channels'], voice_str)
    ]
    if SHARDED:
        body += [(lan['sharding'],
                  '{}/{}'.format(str(bot.shard_id + 1), str(bot.shard_count)))]
    # cur, server, default_prefix
    footer = lan['info_footer'].format(get_prefix(
        bot.cur, ctx.message.server, bot.default_prefix)
    )

    return build_embed(body, COLOUR, author=author, footer=footer)
