"""
Owner only commands
bash                ✕
setavatar           ✕
eval                ✔
shard               ✕
shardinfo           ✕
editsettings        ✕
reload              ✕
restart             ✕
shutdown            ✕
blacklist           ✕
"""

from discord.ext import commands

from config.settings import OWNER
from core.checks import is_owner
from core.discord_functions import check_message_startwith, clense_prefix, \
    get_prefix
from core.owner_only_core import handle_eval, bash_script


class OwnerOnly:
    """
    OwnerOnly commands
    """
    __slots__ = ['bot']

    def __init__(self, bot):
        """
        Initialize the OwnerOnly class
        :param bot: the bot object
        """
        self.bot = bot

    async def on_message(self, message):
        """
        Events for reading messages
        :param message: the message
        """
        prefix = get_prefix(
            self.bot.cur, message.server, self.bot.default_prefix
        )
        if check_message_startwith(self.bot, message, '{}eval'.format(prefix)):
            if str(message.author.id) in OWNER:
                args = clense_prefix(message, '{}eval'.format(prefix))
                await self.bot.send_message(message.channel, handle_eval(args))
            else:
                await self.bot.send_message(
                    message.channel,
                    self.bot.get_language_dict(message)['owner_only'])

    @commands.command(pass_context=True)
    @commands.check(is_owner)
    async def bash(self, ctx, *args):
        localize = self.bot.get_language_dict(ctx)
        result, success = bash_script(list(args))
        str_out = ['```\n' + s + '\n```' for s in result]
        header = localize['bash_success'] if success else localize['bash_fail']
        await self.bot.say(header)
        for s in str_out:
            await self.bot.say(s)
