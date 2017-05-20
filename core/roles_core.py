"""
Functions to deal with the Roles class
"""

from discord.utils import get

from .data_controller import get_role_list_, remove_role_, add_role_
from .discord_functions import handle_forbidden_http


def get_server_role(role, server):
    """
    Get a list of server roles with the name ame as :param role

    :param role: the role name

    :param server: the server

    :return: a list of discord role object
    """
    return get(server.roles, name=role)


def get_role_list(*, server, conn, cur, localize):
    """
    Get the role list of the server

    :param server: the discord server

    :param conn: the db connection

    :param cur: the db cursor

    :param localize: localization strings

    :return: the string representation of the server role list
    """
    lst = get_role_list_(cur, server.id)
    # Check for any non-existing roles and remove them from the db
    for i in range(len(lst)):
        role = lst[i]
        if get_server_role(role, server) is None:
            remove_role_(conn, cur, server.id, role)
            lst.remove(role)
    if lst:
        lst = ['* ' + r for r in lst]
        return localize['has_role_list'] + '```' + '\n'.join(lst) + '```'
    else:
        return localize['no_role_list']


def add_role(*, conn, cur, server, localize, role):
    """
    Add a role to the db to be self assignable

    :param conn: the database connection

    :param cur: the database cursor

    :param server: the discord server

    :param localize: the localization strings

    :param role: the role to be added

    :return: the response string
    """
    if get_server_role(role, server) is None:
        return localize['role_no_exist']
    else:
        add_role_(conn, cur, server.id, role)
        return localize['role_add_success'].format(role)


def remove_role(*, localize, server, conn, cur, role):
    """
    Remove a role from the db

    :param role: the role to be removed

    :param localize: the localization strings

    :param server: the discord server

    :param conn: the database connection

    :param cur: the database cursor

    :return: the response string
    """
    res = localize['role_no_exist'] if get_server_role(role, server) is None \
        else localize['role_remove_success'].format(role)
    remove_role_(conn, cur, server.id, role)
    return res


def role_add_rm(*, role, localize, server, cur, conn, is_add, check_db=True):
    """
    A helper function for role_unrole

    :param localize: the localization strings

    :param server: the discord server

    :param cur: the database cursor

    :param conn: the database connection

    :param role: the role name

    :param is_add: True if the function is add, False if it's remove

    :param check_db: check the db for self assign

    :return: (the response string, the role to be handled)
    """
    lst = get_role_list(server=server, conn=conn, cur=cur, localize=localize) \
        if check_db else []  # To save runtime
    server_role = get_server_role(role, server)
    if (not check_db or role in lst) and server_role is not None:
        s = localize['role_me_success'] if is_add \
            else localize['unrole_me_success']
        return s.format(role), server_role
    elif role in lst and server_role is None:
        return localize['role_unrole_no_exist'], None
    elif role not in lst:
        return localize['not_assignable'], None


async def role_unrole(*, bot, ctx, target, role_name, is_add,
                      is_mute, check_db, reason=None):
    """
    A helper function to handle adding/removing role from a member

    :param bot: the bot

    :param ctx: the discord context

    :param is_mute: If the action is a mute role assignment

    :param role_name: The role name, can be either a string
    or a collection of strings. Will join the collection with a white space
    character to produce a single role name

    :param is_add: wether if the method is add or remove


    :param check_db: if need to check the db for self role

    :param reason: the reason for mute/unmute

    :param target: the role assignment target
    """
    from core.moderation_core import send_mod_log
    localize = bot.get_language_dict(ctx)
    server = ctx.message.server
    channel = ctx.message.channel
    res, role = role_add_rm(
        role=role_name,
        localize=localize,
        server=server,
        cur=bot.cur,
        conn=bot.conn,
        is_add=is_add,
        check_db=check_db
    )
    func = bot.add_roles if is_add else bot.remove_roles
    try:
        if role is not None:
            await func(target, role)
        if is_mute:
            action = localize['muted'] if is_add else localize['unmuted']
            mod_log_action = localize['mute'] if is_add else localize['unmute']
            res = localize['mute_unmute_success'].format(
                action, target.name, reason
            )
            await send_mod_log(ctx, bot, mod_log_action, target, reason)
        await bot.say(res)
    except Exception as e:
        action = localize['assign'] if is_add else localize['remove']
        await handle_forbidden_http(
            e, bot, channel, localize, '{} {}'.format(
                action, localize['role']
            )
        )
