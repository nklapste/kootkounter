# -*- coding: utf-8 -*-

""""""

from logging import getLogger

from discord.ext import commands

BOT = commands.Bot(command_prefix="#KK")

__log__ = getLogger(__name__)


@BOT.command(name='list')
async def _list(ctx, arg):
    pass


@BOT.event
async def on_message(message):
    print("The message's content was", message.content)


@BOT.event
async def on_ready():
    __log__.info("logged in as: {}".format(BOT.user.id))
