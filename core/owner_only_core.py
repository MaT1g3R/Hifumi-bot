"""
Functions for the owner only cog
"""

import ast

from subprocess import check_output, STDOUT, CalledProcessError
from textwrap import wrap


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
    return wrap(res_str, 1800), success
