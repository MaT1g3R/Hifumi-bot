"""
Utility functions to interact with the database
"""
from typing import List

from discord import Server
from discord.utils import get

from data_controller.data_manager import DataManager
from data_controller.errors import LowBalanceError, NegativeTransferError
from scripts.discord_functions import get_server_role
from scripts.language_support import generate_language_entry


async def set_language(bot, ctx, language: str) -> str:
    """
    Set the language for the guild, and return the message
    :param bot: bot
    :param ctx: the discord context
    :param language: the language to set to
    :return: the message
    """
    # FIXME Remove casting after library rewrite
    guild_id = int(ctx.message.server.id)
    await bot.data_manager.set_language(guild_id, language)
    localize = bot.localize(ctx)
    language_data = localize['language_data']
    translators = language_data['translators']
    return localize['lan_set_success'].format(
        generate_language_entry(language_data), ', '.join(translators)
    )


def get_prefix(bot, message):
    """
    Get the command prefix based on a discord message.
    :param bot: the bot.
    :param message: the discord message.
    :return: the command prefix.
    """
    try:
        server_id = int(message.server.id)
    except AttributeError:
        return bot.default_prefix
    else:
        r = bot.data_manager.get_prefix(server_id)
        return r if r else bot.default_prefix


async def change_balance(data_manager: DataManager, user_id: int, delta: int):
    """
    Change the balance of a user.
    :param data_manager: the data manager.
    :param user_id: the user id.
    :param delta: the amout to change.
    :raises LowBalanceError: if the user doesnt have enough balance.
    """
    current_balance = data_manager.get_user_balance(user_id) or 0
    new_balance = current_balance + delta
    if new_balance < 0:
        raise LowBalanceError(str(current_balance))
    await data_manager.set_user_balance(user_id, new_balance)


async def transfer_balance(
        data_manager: DataManager, from_id: int, to_id, amount: int) -> tuple:
    """
    Transfer balance from one user to another.
    :param data_manager: the data manager.
    :param from_id: the user id to transfer from.
    :param to_id: the user id to transfer to.
    :param amount: the amount for the transfer.

    :return: the new balance for the sending user and the reciving user

    :raises LowBalanceError: if the user to transfer from
    doesnt have enough balance.

    :raises NegativeTransferError: if the user try to transfer negative amount.
    """
    if amount < 0:
        raise NegativeTransferError
    if amount > 0:
        await change_balance(data_manager, from_id, -amount)
        await change_balance(data_manager, to_id, amount)
    return (data_manager.get_user_balance(from_id),
            data_manager.get_user_balance(to_id))


async def add_self_role(data_manager: DataManager, guild_id: int, role):
    """
    Add a self role to the guild role list.
    :param data_manager: the data manager.
    :param guild_id: the guild id.
    :param role: the role name.
    """
    lst = data_manager.get_roles(guild_id) or []
    if role not in lst:
        lst.append(role)
        await data_manager.set_roles(guild_id, lst)


async def remove_self_role(data_manager: DataManager, guild_id: int, role):
    """
    Remove a self role from the guild role list.
    :param data_manager: the data manager.
    :param guild_id: the guild id.
    :param role: the role name.
    """
    lst = data_manager.get_roles(guild_id) or []
    new = [s for s in lst if s != role]
    await data_manager.set_roles(guild_id, new)


# FIXME Change Server to Guild after lib rewrite
async def self_role_names(
        guild: Server, data_manager: DataManager) -> List[str]:
    """
    Get the role list of the server

    :param guild: the discord guild

    :param data_manager: the data manager.

    :return: a list of role names of self assignable roles in the guild.
    """
    # FIXME Remove casting after lib rewrite
    guild_id = int(guild.id)
    lst = data_manager.get_roles(guild_id) or []
    # Check for any non-existing roles and remove them from the db
    new = [r for r in lst if get_server_role(r, guild)]
    if new != lst:
        await data_manager.set_roles(guild_id, new)
    return new


async def get_modlog(data_manager: DataManager, guild):
    """
    Get the mod log channel of a server, remove it from the db if the
    channel no longer exists
    :param data_manager: the data manager
    :param guild: the guild
    :return: the mod log channel id
    """
    # FIXME Remove casting after library rewrite
    modlog = data_manager.get_mod_log(int(guild.id))
    guild_channel = get(guild.channels, id=str(modlog))
    if guild_channel:
        return guild_channel
    else:
        await data_manager.set_mod_log(int(guild.id), None)
