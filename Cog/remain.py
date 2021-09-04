import nextcord as discord
from nextcord.ext import tasks, commands
import sys
import random
from random import choice
import asyncio
import time
import pymongo
from PIL import Image, ImageFont, ImageDraw, ImageOps, ImageSequence, ImageFilter
import requests
import io
from io import BytesIO
from datetime import datetime, timedelta

sys.path.append("..")
from ai3 import functions as funs
import config

client = pymongo.MongoClient(config.cluster_token)
db = client.bot
users = db.users
backs = db.bs
servers = db.servers
settings = db.settings


class remain(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(usage = '[message]', description = 'Создать опрос.')
    async def poll(self,ctx, *, args="Тут пусто?"):
        await ctx.channel.purge(limit = 1)
        ok = self.bot.get_emoji(744137747639566346)
        no = self.bot.get_emoji(744137801804546138)
        message = await ctx.send(embed = discord.Embed(
            title="Опрос",
            description=args,
            color=0xf03e65).set_footer(
            text = ctx.author).set_thumbnail(
            url= ctx.author.avatar.url)
        )
        await message.add_reaction(ok), await message.add_reaction(no)

    @commands.command(hidden = True)
    async def em(self, ctx,*, args):
        await ctx.send(f"{args} | `{args}`")

    @commands.command(hidden = True)
    async def text(self, ctx, *, text):
        text = str(funs.text_replase(text, ctx.author))
        await ctx.send(text)

    @commands.command(hidden = True)
    async def time(self, ctx, time:int):
        text = funs.time_end(time)
        await ctx.send(text)

    # @commands.command()
    # async def sendi(self, ctx):
    #     creator = 323512096350535680
    #     if ctx.author.id != creator:
    #         return
    #
    #     for i in users.find({}):
    #         member = await self.bot.fetch_user(i['userid'])
    #         emb = discord.Embed(description = f"Здравствуйте {member.mention}, команда бота IT Котик поздравляет вас с наступающим новым годом! Мы благодарим каждого пользователя за использование бота и дарим ва подарки!\n Переходить на **[Ссылка](https://discord.gg/cFa8K37pBa)** и прописывайте в <@792687534727102502> `+2021` что бы получить `2021 монетку` и новогоднюю роль.\nС наступающим!", color=0xf03e65)
    #         emb.set_author(icon_url = '{}'.format(ctx.author.avatar_url), name = '{}'.format(ctx.author))
    #         try:
    #             await member.send(embed = emb)
    #         except Exception:
    #             pass
    #
    # @commands.command(aliases=["2021","Press_F_to_pay_2020"])
    # async def NewYear(self,ctx):
    #     global settings
    #     s = settings.find_one({"sid": 1})
    #     if ctx.guild.id != 792687533792034827:
    #         emb = discord.Embed(description = f"Эту команду можно использовать только на официальном сервере бота **[Ссылка](https://discord.gg/cFa8K37pBa)**", color=0xf03e65)
    #         emb.set_author(icon_url = '{}'.format(ctx.author.avatar_url), name = '{}'.format(ctx.author))
    #         await ctx.send(embed = emb)
    #     else:
    #         if ctx.author.id not in s['newyear']:
    #             emb = discord.Embed(description = f"С наступающим! Держи 2021 монеток и роль <@&794164924124364820>!", color=0xf03e65)
    #             emb.set_author(icon_url = '{}'.format(ctx.author.avatar_url), name = '{}'.format(ctx.author))
    #             emb.set_footer(text='Жинозавр')
    #             await ctx.send(embed = emb)
    #             users.update_one({'userid':ctx.author.id},{'$inc':{"money": 2021}})
    #             await ctx.author.add_roles(ctx.guild.get_role(794164924124364820))
    #
    #             s['newyear'].append(ctx.author.id)
    #             settings.update_one({'sid':1},{'$set': {'newyear': s['newyear'] }})
    #         else:
    #             await ctx.send('Вы уже забрали подарочек!')


def setup(bot):
    bot.add_cog(remain(bot))
