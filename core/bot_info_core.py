"""
Core fuctions for BotInfo cog
"""
import platform
import resource
from time import time

from discord import ChannelType, version_info
from discord.embeds import Embed
from psutil import virtual_memory

from config import *
from data_controller.data_utils import get_prefix
from scripts.discord_functions import add_embed_fields
from scripts.helpers import comma, get_system_name, \
    get_time_elapsed


def get_uptime(start_time, day_str):
    """
    Get the uptime from start_time in a hh:mm:ss format
    :param start_time: the start time for the elapsed time calculation
    :param day_str: the localization string that says "day"
    :return: time elapsed from start_time in a hh:mm:ss format
    :rtype: str
    """
    days, hours, minutes, seconds = (
        int(t) for t in get_time_elapsed(start_time, time())
    )
    return '{:02d}:{:02d}:{:02d} {}'.format(
        hours, minutes, seconds, '({} {})'.format(days, day_str)
    )


def generate_info(*, guilds, members, channels, voice, logged_in):
    """
    Generates the info for the bot

    :param guilds: the list of guilds the bot is in

    :param members: the list of members in all the guilds the bot is in

    :param channels: the lsit of channels the bot is in

    :param voice: the list of voice channels the bot is in

    :param logged_in: is the bot logged in

    :return: the info of the bot
    """
    server_count = len(list(guilds))
    user_count = len(list(members))
    text_channel_count = len(
        [c for c in channels if c.type == ChannelType.text])
    voice_count = len(list(voice))
    ram = float(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024)
    return {
        'ram': ram,
        'guild_count': server_count,
        'user_count': user_count,
        'text_channel_count': text_channel_count,
        'voice_count': voice_count,
        'logged_in': logged_in
    }


def build_info_embed(ctx, bot):
    """
    build the info embed
    :param ctx: the discord context object
    :param bot: the bot object
    :return: the info embed
    """
    stats = generate_info(
        guilds=bot.servers,
        members=bot.get_all_members(),
        channels=bot.get_all_channels(),
        voice=bot.voice_clients,
        logged_in=bot.is_logged_in
    )
    user = bot.user
    lan = bot.get_language_dict(ctx)

    ram = stats['ram']
    guild_count = comma(stats['guild_count'])
    user_count = comma(stats['user_count'])
    text_count = comma(stats['text_channel_count'])
    voice_count = comma(stats['voice_count'])

    if ram < 1024:
        ram_str = '{0:.2f}MB'.format(ram)
    else:
        ram_str = '{0:.2f}GB'.format(ram / 1024)
    total_ram = virtual_memory().total / 1024 / 1024 / 1024
    total_ram_str = '{0:.2f}GB'.format(total_ram)
    body = [
        (lan['ram_used'] + '/' + lan['total_ram'],
         f'{ram_str}/{total_ram_str}'),
        (lan['uptime'], get_uptime(bot.start_time, lan['days'])),
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
        (lan['guilds'], guild_count),
        (lan['users'], user_count),
        (lan['text_channels'], text_count),
        (lan['voice_channels'], voice_count)
    ]
    footer = lan['info_footer'].format(get_prefix(bot, ctx.message))

    embed = Embed(colour=COLOUR)
    embed.set_author(name=user.name, icon_url='{0.avatar_url}'.format(user))
    embed.set_footer(text=footer)
    return add_embed_fields(embed, body)
