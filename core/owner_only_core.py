"""
Functions for the owner only cog
"""

import ast
from subprocess import check_output, STDOUT, CalledProcessError
from textwrap import wrap

from discord import HTTPException, InvalidArgument


def handle_eval(code):
    """
    Handle the eval request from testing_core
    :param code: the code block
    :return: the eval result
    """
    try:
        block = ast.parse(code, mode='exec')

        last = ast.Expression(block.body.pop().value)

        _globals, _locals = {}, {}
        exec(compile(block, '<string>', mode='exec'), _globals, _locals)
        res = eval(compile(last, '<string>', mode='eval'), _globals, _locals)
        return ':white_check_mark: **Evaluation success!**\n' \
               'Output:```Python\n{}```'.format(res)
    except Exception as e:
        return ':no_entry_sign: **Evaluation failed!**\n' \
               'Output:' + '```Python\n{}```'. \
                   format(e.__class__.__name__ + ': ' + str(e))


def bash_script(command: list):
    """
    Run a bash script
    :param command: the bash command
    :return: (the result of the command in a list, success)
    :rtype: tuple
    """
    try:
        output = check_output(command, stderr=STDOUT)
        res_str = output.decode()
        success = True
    except CalledProcessError as ex:
        res_str = ex.output.decode()
        success = False
    except Exception as ex:
        res_str = str(ex)
        success = False
    return wrap(res_str, 1800, replace_whitespace=False), success


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
