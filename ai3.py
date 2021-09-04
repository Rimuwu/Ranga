# -*- coding: utf-8 -*-
import nextcord as discord
from nextcord.ext import tasks, commands
# from discord_slash import SlashCommand, SlashContext
import requests
from PIL import Image, ImageFont, ImageDraw, ImageOps, ImageSequence, ImageFilter
import io
from io import BytesIO
import random
from random import choice
import asyncio
import time
from datetime import datetime, timedelta
import os
import pymongo
import math
from fuzzywuzzy import fuzz
import config
import pprint


client = pymongo.MongoClient(config.cluster_token)
db = client.bot

users = db.users
backs = db.bs
servers = db.servers
clubs = db.clubs
frames = db.frames
settings = db.settings

peoplesCD = {}
start_time = time.time()

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix='$', intents = intents)

@bot.event
async def on_ready():
    global start_time

    channel = bot.get_channel(813056001229324308)
    ping = bot.latency
    ping_emoji = "🟩🔳🔳🔳🔳"

    ping_list = [
        {"ping": 0.10000000000000000, "emoji": "🟧🟩🔳🔳🔳"},
        {"ping": 0.15000000000000000, "emoji": "🟥🟧🟩🔳🔳"},
        {"ping": 0.20000000000000000, "emoji": "🟥🟥🟧🟩🔳"},
        {"ping": 0.25000000000000000, "emoji": "🟥🟥🟥🟧🟩"},
        {"ping": 0.30000000000000000, "emoji": "🟥🟥🟥🟥🟧"},
        {"ping": 0.35000000000000000, "emoji": "🟥🟥🟥🟥🟥"}]

    for ping_one in ping_list:
        if ping > ping_one["ping"]:
            ping_emoji = ping_one["emoji"]
            break

    time2 = time.time()
    try:
        await channel.send(f"Бот онлайн - Серверов: {len(bot.guilds)} - Команд: {len(bot.commands)}\n{ping_emoji} `{ping * 1000:.0f}ms`\nВремя на запуск: {functions.time_end(time2 - start_time)}")
        print(f"Бот онлайн - Серверов: {len(bot.guilds)} - Команд: {len(bot.commands)} - Время на запуск: {functions.time_end(time2 - start_time)}")
    except Exception:
        await channel.send(f"Бот онлайн - Серверов: {len(bot.guilds)} - Команд: {len(bot.commands)}\n{ping_emoji} `{ping * 1000:.0f}ms`")
        print(f"Бот онлайн - Серверов: {len(bot.guilds)} - Команд: {len(bot.commands)}")

@bot.command()
async def ping(ctx):
    await ctx.reply('Pong!')

bot.run(config.bot_token)
