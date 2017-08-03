"""
Functions for the owner only cog
"""

import sys
from io import StringIO
from subprocess import check_output, STDOUT, CalledProcessError
from textwrap import wrap

from discord import HTTPException, InvalidArgument


def handle_eval(code):
    """
    Handle the eval request from testing_core
    :param code: the code block
    :return: (the eval result, success)
    :rtype: tuple
    """
    try:
        buffer = StringIO()
        sys.stdout = buffer
        exec(code)
        res = buffer.getvalue()
        sys.stdout = sys.__stdout__
        success = True
    except Exception as e:
        success = False
        res = format(e.__class__.__name__ + ': ' + str(e))
    return res, success


async def setavatar(bot, localize, channel, avatar, retry=0):
    """
    I'm going to hell with this.
    Set the bot's avatar.
    :param bot: the bot
    :param localize: the localization strings
    :param channel: the discord channel
    :param avatar: the url that points to the image
    :param retry: the retry count
    """
    while True:
        try:
            await bot.edit_profile(avatar=avatar)
            await bot.send_message(channel, localize['avatar_success'])
            break
        except InvalidArgument:
            await bot.send_message(channel, localize['avatar_fail'])
            break
        except HTTPException:
            await bot.send_message(
                channel, localize['avatar_error'].format(retry)
            )
            retry += 1
