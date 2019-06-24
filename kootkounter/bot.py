#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Definition of the kootkounter discord bot"""

from logging import getLogger
import sqlite3
from typing import List

from discord.ext import commands

BOT = commands.Bot(command_prefix="#KK")

__log__ = getLogger(__name__)

__database_path__: str = "degeneracy.db"

__database__: sqlite3.Connection = None


degenerate_terms = [
    "koot",
    "uwu",
    "owo",
    "boi",
    "nuu",
    "nerd",
    "ishh"
]


def degeneracy_detector(string: str) -> List[str]:
    tokens = string.lower().split()
    degeneracy = [token for token in tokens if token in degenerate_terms]
    return degeneracy


@BOT.command(name='list')
async def _list(ctx, arg):
    pass


@BOT.event
async def on_message(message):
    print("The message's content was", message.content)
    print("Total degeneracy: {}".format(len(degeneracy_detector(message.content))))


@BOT.event
async def on_ready():
    __log__.info("logged in as: {}".format(BOT.user.id))
    __database__ = sqlite3.connect(__database_path__)
