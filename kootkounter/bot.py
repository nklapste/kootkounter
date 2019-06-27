#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Definition of the kootkounter discord bot"""

import re
import time
from functools import partial, wraps
from logging import getLogger
from typing import List

from discord import Message, User
from discord.ext import commands
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session

BOT = commands.Bot(command_prefix="!KK")

__log__ = getLogger(__name__)

DEGENERATE_TERMS = [
    "koot",
    "uwu",
    "owo",
    "boi",
    "nuu",
    "nerd",
    "isha"
]

BASE = declarative_base()

# to be set within invoking __main__.py
DB: Session = None


class Degenerate(BASE):
    __tablename__ = "degenerate"
    id = Column(Integer, primary_key=True)
    name = Column(String(250), default="Unknown")
    koot_count = Column(Integer, default=0)
    uwu_count = Column(Integer, default=0)
    owo_count = Column(Integer, default=0)
    boi_count = Column(Integer, default=0)
    nuu_count = Column(Integer, default=0)
    nerd_count = Column(Integer, default=0)
    isha_count = Column(Integer, default=0)


def get_or_create(model, **kwargs):
    """Get or create a sqlalchemy model"""
    instance = DB.query(model).filter_by(**kwargs).first()
    if instance:
        return instance
    instance = model(**kwargs)
    DB.add(instance)
    DB.commit()
    return instance


def update_degenerate_terms(author: User, terms: List[str]):
    """Update the database of degeneracy"""
    degenerate = get_or_create(Degenerate, id=author.id)
    setattr(degenerate, "name", author.name)
    for term in terms:
        setattr(degenerate, "{}_count".format(term),
                getattr(degenerate, "{}_count".format(term), 0) + 1)
    DB.commit()


async def help_(message: Message):
    await message.channel.send("""```
kootkounter: Tracking degeneracy across Discord!

Available commands:

!KKhelp
    Print this help message

!KKregister DISCORD_USER_ID
    Register a Discord User for degeneracy tracking with the 
    specified DISCORD_USER_ID
    
!KKunregister DISCORD_USER_ID
    Unregister a Discord User from degeneracy tracking with the 
    specified DISCORD_USER_ID
    
!KKshow
    List collected degeneracy statistics on all registered Discord Users
```""")


async def register(message: Message):
    """Register a Discord user for degeneracy tracking"""
    try:
        degenerate_id = int(message.content.split()[1])
        get_or_create(Degenerate, id=degenerate_id)
        DB.commit()
    except (IndexError, ValueError):
        await message.channel.send(
            "Registering user failed: Invalid arguments")
    else:
        await message.channel.send(
            "Registered user: {}".format(degenerate_id))


async def unregister(message: Message):
    """Unregister a Discord user from degeneracy tracking"""
    try:
        degenerate_id = int(message.content.split()[1])
        DB.delete(get_or_create(Degenerate, id=degenerate_id))
        DB.commit()
    except (IndexError, ValueError):
        await message.channel.send(
            "Unregistering user failed: Invalid arguments")
    else:
        await message.channel.send(
            "Unregistered user: {}".format(degenerate_id))


async def show(message: Message):
    """Show the collected degeneracy statistics on registered Discord users"""
    for degenerate in DB.query(Degenerate):
        await message.channel.send(
            f"``"
            f"id: {degenerate.id:<20}"
            f"name: {degenerate.name:<34}"
            f"koot: {degenerate.koot_count:<5}"
            f"owo: {degenerate.owo_count:<5}"
            f"uwu: {degenerate.uwu_count:<5}"
            f"boi: {degenerate.boi_count:<5}"
            f"nuu: {degenerate.nuu_count:<5}"
            f"nerd: {degenerate.nerd_count:<5}"
            f"isha: {degenerate.ish_count:<5}"
            f"``"
        )


WARN_COOLDOWN = 10


class ThrottleException(Exception):
    """Operation is being called too soon"""


class ThrottleDecorator(object):
    def __init__(self, func, interval):
        self.func = func
        self.interval = interval
        self.last_run = 0

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self.func
        return partial(self, obj)

    def __call__(self, *args, **kwargs):
        now = time.time()
        if now - self.last_run < self.interval:
            raise ThrottleException("Call after {0} seconds".format(
                self.last_run + self.interval - now))
        else:
            self.last_run = now
            return self.func(*args, **kwargs)


def throttle(interval):
    """Decorator that throttles a function from called multiple times within
    a specified interval"""

    def apply_decorator(func):
        decorator = ThrottleDecorator(func=func, interval=interval)
        return wraps(func)(decorator)

    return apply_decorator


@throttle(WARN_COOLDOWN)
async def warn_degenerate(message: Message):
    """Warn a Discord user of their degeneracy"""
    await message.channel.send("*{} will remember this*".format(BOT.user.name))


def degeneracy_detector(string: str) -> List[str]:
    """Detect degeneracy within a string"""
    tokens = re.sub("[^a-zA-Z\\s]", "",
                    string.replace("0", "o").lower()).split()
    degeneracy = [token for token in tokens if token in DEGENERATE_TERMS]
    return degeneracy


@BOT.event
async def on_message(message: Message):
    if str(message.content).startswith("!KKhelp"):
        await help_(message)
    elif str(message.content).startswith("!KKregister"):
        await register(message)
    elif str(message.content).startswith("!KKunregister"):
        await unregister(message)
    elif str(message.content).startswith("!KKshow"):
        await show(message)
    elif DB.query(Degenerate) \
            .filter(Degenerate.id == message.author.id).first():
        degeneracy = degeneracy_detector(message.content)
        if degeneracy:
            __log__.info(
                f"Degeneracy detected: user: {message.author.id} message: {message.content} degeneracy: {degeneracy}")
            update_degenerate_terms(message.author, degeneracy)
            await warn_degenerate(message)


@BOT.event
async def on_ready():
    __log__.info("logged in as: {}".format(BOT.user.id))
