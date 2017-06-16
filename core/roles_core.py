"""
Functions to deal with the Roles class
"""

from discord.utils import get

from data_controller import DataManager
from data_controller.data_utils import add_self_role, remove_self_role
from scripts.discord_functions import handle_forbidden_http


def get_role_list(*, guild, data_manager: DataManager, localize):
    """
    Get the role list of the server

    :param guild: the discord guild

    :param data_manager: the data manager.

    :param localize: localization strings

    :return: the string representation of the server role list
    """
    guild_id = int(guild.id)
    lst = data_manager.get_roles(guild_id) or []
    edit = False
    # Check for any non-existing roles and remove them from the db
    for i in range(len(lst)):
        role = lst[i]
        if not get(guild.roles, name=role):
            edit = True
            lst.remove(role)
    if edit:
        data_manager.set_roles(guild_id, lst)
    if lst:
        lst = ['* ' + r for r in lst]
        return localize['has_role_list'] + '```' + '\n'.join(lst) + '```'
    else:
        return localize['no_role_list']


def add_role(*, data_manager: DataManager, guild, localize, role):
    """
    Add a role to the db to be self assignable

    :param guild: the discord guild

    :param data_manager: the data manager.

    :param localize: the localization strings

    :param role: the role to be added

    :return: the response string
    """
    if get(guild.roles, name=role):
        add_self_role(data_manager, int(guild.id), role)
        return localize['role_add_success'].format(role)
    else:
        return localize['role_no_exist']


def remove_role(*, localize, guild, data_manager: DataManager, role):
    """
    Remove a role from the db

    :param role: the role to be removed

    :param localize: the localization strings

    :param guild: the discord guild

    :param data_manager: the data manager.

    :return: the response string
    """
    res = localize['role_no_exist'] if get(guild.roles, name=role) is None \
        else localize['role_remove_success'].format(role)
    remove_self_role(data_manager, int(guild.id), role)
    return res


def role_add_rm(*, role, localize, guild,
                data_manager: DataManager, is_add, check_db=True):
    """
    A helper function for role_unrole

    :param localize: the localization strings

    :param guild: the discord guild

    :param data_manager: the data manager.

    :param role: the role name

    :param is_add: True if the function is add, False if it's remove

    :param check_db: check the db for self assign

    :return: (the response string, the role to be handled)
    """
    lst = get_role_list(guild=guild,
                        data_manager=data_manager, localize=localize) \
        if check_db else []  # To save runtime

    guild_role = get(guild.roles, name=role)
    if (not check_db or role in lst) and guild_role is not None:
        s = localize['role_me_success'] if is_add \
            else localize['unrole_me_success']
        return s.format(role), guild_role
    elif role in lst and guild_role is None:
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
    guild = ctx.message.server
    channel = ctx.message.channel
    res, role = role_add_rm(
        role=role_name,
        localize=localize,
        guild=guild,
        data_manager=bot.data_manager,
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
