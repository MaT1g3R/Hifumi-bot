"""
Functions to deal with the Roles class
"""
from config.settings import DATA_CONTROLLER


def __role(ctx, bot):
    """
    Helper function the return some useful things for other role functions
    :param ctx: the discord context 
    :param bot: the bot
    :return: (server_id, server_roles, localize)
    """
    server = ctx.message.server
    localize = bot.get_language_dict(ctx)
    server_roles = [role.name for role in server.roles]
    return str(server.id), server_roles, localize


def get_role_list(ctx, bot):
    """
    Get the role list of the server
    :param ctx: the discord context object
    :param bot: the hifumi bot
    :return: the string representation of the server role list
    """
    server_id, server_roles, localize = __role(ctx, bot)
    lst = DATA_CONTROLLER.get_role_list(server_id)
    # Check for any non-existing roles and remove them from the db
    for i in range(len(lst)):
        role = lst[i]
        if role not in server_roles:
            DATA_CONTROLLER.remove_role(server_id, role)
            lst.remove(role)
    if lst:
        lst = ['* ' + r for r in lst]
        return localize['has_role_list'] + '```' + '\n'.join(lst) + '```'
    else:
        return localize['no_role_list']


def add_role(ctx, bot, role):
    """
    Add a role to the db to be self assignable
    :param ctx: the discord context 
    :param bot: the bot
    :param role: the role to be added
    :return: the response string
    """
    server_id, server_roles, localize = __role(ctx, bot)
    if role not in server_roles:
        return localize['role_no_exist']
    else:
        DATA_CONTROLLER.add_role(server_id, role)
        return localize['role_add_success'].format(role)


def remove_role(ctx, bot, role):
    """
    Remove a role from the db
    :param ctx: the discord context
    :param bot: the bot 
    :param role: the role to be removed
    :return: the response string
    """
    server_id, server_roles, localize = __role(ctx, bot)
    res = localize['role_no_exist'] if role not in server_roles \
        else localize['role_remove_success'].format(role)
    DATA_CONTROLLER.remove_role(server_id, role)
    return res


def __role_add_rm(ctx, bot,  role, is_add):
    """
    A helper function for roleme and unrole me
    :param ctx: the discord context
    :param role: the role name
    :param is_add: True if the function is add, False if it's remove
    :return: (the response string, the role to be handled)
    """
    lst = get_role_list(ctx, bot)
    server_id, server_roles, localize = __role(ctx, bot)
    if role in lst and role in server_roles:
        res = [r for r in ctx.message.server.roles if r.name == role]
        s = localize['role_me_success'] if is_add \
            else localize['unrole_me_success']
        return s.format(role), res
    elif role in lst and role not in server_roles:
        return localize['role_unrole_no_exist'], None
    elif role not in lst:
        return localize['not_assignable'], None
    else:
        return localize['role_unrole_fail'], None


def role_me(ctx, bot, role):
    """
    Give a user self assignable role
    :param ctx: the discord context
    :param bot: the bot object
    :param role: the role to be added
    :return: (the response string, the role to be added)
    """
    return __role_add_rm(ctx, bot, role, True)


def unroleme(ctx, bot, role):
    """
    Remove a role from a user
    :param ctx: the discord context
    :param bot: the bot
    :param role: the role to be removed
    :return: (the response string, the role to be removed)
    """
    return __role_add_rm(ctx, bot, role, False)
