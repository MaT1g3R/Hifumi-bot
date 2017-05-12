"""
Functions for the owner only cog
"""

import ast


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
