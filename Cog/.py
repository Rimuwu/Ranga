import nextcord as discord
from nextcord.ext import commands
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
from Cybernator import Paginator
import pymongo
from bs4 import BeautifulSoup as BS
from collections import Counter

sys.path.append("..")
from AI2 import functions as funs

client = pymongo.MongoClient("mongodb+srv://bot:12452987190076@cluster0.jy3nj.mongodb.net/<dbname>?retryWrites=true&w=majority")

db = client.bot
users = db.users
backs = db.bs
servers = db.servers


class MainCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot





def setup(bot):
    bot.add_cog(MainCog(bot))
