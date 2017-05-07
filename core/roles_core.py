"""
Functions to deal with the Roles class
"""
from config.settings import DATA_CONTROLLER


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
    Get a list of server roles with the name <role>
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


def __role_add_rm(ctx, bot, role, is_add):
    """
    A helper function for roleme and unrole me
    :param ctx: the discord context
    :param role: the role name
    :param is_add: True if the function is add, False if it's remove
    :return: (the response string, the role to be handled)
    """
    lst = get_role_list(ctx, bot)
    server = ctx.message.server
    localize = bot.get_language_dict(ctx)
    if role in lst and role_exist(role, server):
        s = localize['role_me_success'] if is_add \
            else localize['unrole_me_success']
        return s.format(role), get_server_role(role, server)
    elif role in lst and not role_exist(role, server):
        return localize['role_unrole_no_exist'], None
    elif role not in lst:
        return localize['not_assignable'], None


def role_me(ctx, bot, role):
    """
    Give a user self assignable role
    :param ctx: the discord context
    :param bot: the bot object
    :param role: the role to be added
    :return: (the response string, the role to be added)
    """
    return __role_add_rm(ctx, bot, role, True)


def unrole_me(ctx, bot, role):
    """
    Remove a role from a user
    :param ctx: the discord context
    :param bot: the bot
    :param role: the role to be removed
    :return: (the response string, the role to be removed)
    """
    return __role_add_rm(ctx, bot, role, False)
