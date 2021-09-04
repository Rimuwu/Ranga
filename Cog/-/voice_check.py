import discord
from discord.ext import commands
from discord.ext import tasks
import requests
from PIL import Image, ImageFont, ImageDraw, ImageOps
import io
from io import BytesIO
import sys
import random
from random import choice
import asyncio
import nekos
import time
import os
from Cybernator import Paginator
import pymongo
from bs4 import BeautifulSoup as BS
from collections import Counter
from itertools import cycle

client = pymongo.MongoClient("mongodb+srv://host:1394@cluster0.jy3nj.mongodb.net/<dbname>?retryWrites=true&w=majority")
db = client.bot

users = db.users
backs = db.bs
servers = db.servers
guilds = db.guilds

client2 = pymongo.MongoClient("mongodb+srv://host:1394@cluster0.rkh6o.mongodb.net/<dbname>?retryWrites=true&w=majority")
rpg = client2.bot

auc = rpg.auc
bback = rpg.backs
items = rpg.items
players = rpg.players
regions = rpg.regions
kingdoms = rpg.kingdoms


class voice_check(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.bot.loop.create_task(self.update())

    async def update(self):
        global servers
        await self.bot.wait_until_ready()
        while self.bot.is_closed:
            server = servers.find_one({"server": guild.id})
            v = server['private_voices']
            for i in v:
                chan = self.bot.get_channel(i)
                if len(chan.members) < 1:
                    await chan.delete()
                    print('del')

            await asyncio.sleep(3)


def setup(bot: commands.Bot):
    bot.add_cog(voice_check(bot))