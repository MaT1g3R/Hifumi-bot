'''
from discord.ext import commands

from bot import Hifumi
from datetime import date
from random import randint

import time

# from core.fun_core import *

class Fun:
    """
    Fun cog
    """
    __slots__ = ['bot']

    def __init__(self, bot: Hifumi):
        """
        Initialize the Fun class
        :param bot: the discord bot object
        """
        self.bot = bot
        
    @commands.command(pass_context=True)  
        async def garfield(self, ctx, *args):
        """
        Gets a random Garfield comic
        :param ctx: the discord context object
        """
        firstdate = int(time.mktime(date(1978, 6, 19).timetuple()))
        todaydate = int(time.mktime(date.today().timetuple()))
        todayyear = time.strftime('%Y', time.gmtime(today))
        res = randint(firstdate, todaydate)
        res_year = time.strftime('%Y', time.gmtime(res))
        res_date = time.strftime('%Y-%m-%d', time.gmtime(res))
        archive = "https://d1ejxu6vysztl5.cloudfront.net"
        
        if args is "latest":
            await self.bot.say("https://d1ejxu6vysztl5.cloudfront.net/" +
                               "comics/garfield/" + todayyear + "/" +
                               todaydate + ".gif")
        else:
            await self.bot.say("https://d1ejxu6vysztl5.cloudfront.net/" +
                           "comics/garfield/" + res_year + "/" +
                           res_date + ".gif")
        
'''
