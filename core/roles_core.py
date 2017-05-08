"""
Functions to deal with the Roles class
"""

from config.settings import DATA_CONTROLLER
from core.discord_functions import handle_forbidden_http


def role_exist(role, server):
    """
    Check if a role exist in the server

    :param role: the role name

    :param server: the server

    :return: True if the role exist
    """
    return role in [r.name for r in server.roles]


def get_role_list(ctx, bot):
    """
    Get the role list of the server

    :param ctx: the discord context object

    :param bot: the hifumi bot

    :return: the string representation of the server role list
    """
    server_id = ctx.message.server.id
    localize = bot.get_language_dict(ctx)
    lst = DATA_CONTROLLER.get_role_list(server_id)
    # Check for any non-existing roles and remove them from the db
    for i in range(len(lst)):
        role = lst[i]
        if not role_exist(role, ctx.message.server):
            DATA_CONTROLLER.remove_role(server_id, role)
            lst.remove(role)
    if lst:
        lst = ['* ' + r for r in lst]
        return localize['has_role_list'] + '```' + '\n'.join(lst) + '```'
    else:
        return localize['no_role_list']


def get_server_role(role, server):
    """
    Get a list of server roles with the name ame as :param role

    :param role: the role name

    :param server: the server

    :return: a list of discord role object
    """
    return [r for r in server.roles if r.name == role]


def add_role(ctx, bot, role):
    """
    Add a role to the db to be self assignable

    :param ctx: the discord context

    :param bot: the bot

    :param role: the role to be added

    :return: the response string
    """
    server = ctx.message.server
    localize = bot.get_language_dict(ctx)
    if not role_exist(role, server):
        return localize['role_no_exist']
    else:
        DATA_CONTROLLER.add_role(server.id, role)
        return localize['role_add_success'].format(role)


def remove_role(ctx, bot, role):
    """
    Remove a role from the db

    :param ctx: the discord context

    :param bot: the bot

    :param role: the role to be removed

    :return: the response string
    """
    localize = bot.get_language_dict(ctx)
    server = ctx.message.server
    res = localize['role_no_exist'] if not role_exist(role, server) \
        else localize['role_remove_success'].format(role)
    DATA_CONTROLLER.remove_role(server.id, role)
    return res


def role_add_rm(ctx, bot, role, is_add, check_db=True):
    """
    A helper function for role_unrole

    :param ctx: the discord context

    :param bot: the bot

    :param role: the role name

    :param is_add: True if the function is add, False if it's remove

    :param check_db: check the db for self assign

    :return: (the response string, the role to be handled)
    """
    lst = get_role_list(ctx, bot) if check_db else []  # To save runtime
    server = ctx.message.server
    localize = bot.get_language_dict(ctx)
    if (not check_db or role in lst) and role_exist(role, server):
        s = localize['role_me_success'] if is_add \
            else localize['unrole_me_success']
        return s.format(role), get_server_role(role, server)
    elif role in lst and not role_exist(role, server):
        return localize['role_unrole_no_exist'], None
    elif role not in lst:
        return localize['not_assignable'], None


async def role_unrole(bot, ctx, role_name, is_add, check_db=True, target=None):
    """
    A helper function to handle adding/removing role from a member

    :param bot: the bot

    :param ctx: the context

    :param role_name: The role name, can be either a string
    or a collection of strings. Will join the collection with a white space
    character to produce a single role name

    :param is_add: wether if the method is add or remove

    :param check_db: If it's True then this function will check the db
    for self assign roles

    :param target: the role assignment target, if it's None the role assignment
    target will be the message author
    """
    role_name = role_name if isinstance(role_name, str) else ' '.join(role_name)
    is_mute = target is not None
    target = ctx.message.author if target is None else target
    res, roles = role_add_rm(ctx, bot, role_name, is_add, check_db)
    localize = bot.get_language_dict(ctx)
    func = bot.add_roles if is_add else bot.remove_roles
    try:
        if roles:
            for role in roles:
                await func(target, role)
        if is_mute:
            action = 'muted' if is_add else 'unmuted'
            res = localize['mute_unmute_success'].format(action, target.name)
        await bot.say(res)
    except Exception as e:
        action = 'assign' if is_add else 'remove'
        await handle_forbidden_http(
            e, bot, ctx.message.channel, localize, '{} role'.format(action)
        )
