import discord
from discord.ext import commands
import requests
from PIL import Image, ImageFont, ImageDraw, ImageOps
import io
import sys
import random
from random import choice
import asyncio
import nekos
import time
import os
import pymongo
from bs4 import BeautifulSoup as BS
from collections import Counter


client = pymongo.MongoClient("mongodb+srv://host:1394@cluster0.jy3nj.mongodb.net/<dbname>?retryWrites=true&w=majority")
db = client.bot

users = db.users
backs = db.bs
servers = db.servers


class MainCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot



    @commands.command(aliases = 'waifu')
    async def waifu_info(self, ctx, member: discord.Member):
    
    


def setup(bot):
    bot.add_cog(MainCog(bot))