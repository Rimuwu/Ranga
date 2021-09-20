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

client = funs.mongo_c()
db = client.bot
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

    @commands.command(hidden = True)
    async def add_url_button(self, ctx, message_id:int, url:str, emoji:str, *, label:str):
        if funs.roles_check(ctx.author, ctx.guild.id) == False:
            await ctx.send("У вас недостаточно прав для использования этой команды!")
            return

        try:
            mid = await ctx.channel.fetch_message(message_id)
        except Exception:
            await ctx.send('Сообщение не найдено')

        class url_button(discord.ui.View):
            def __init__(self, url:str, emoji:str, label:str):
                super().__init__()
                self.add_item(discord.ui.Button(emoji = emoji, label=label, url=url))

        await mid.edit(content = mid.content, view= url_button(url, emoji, label))

    @commands.command(hidden = True)
    async def test(self, ctx):

        class Dropdown(discord.ui.Select):
            def __init__(self):

                # Set the options that will be presented inside the dropdown
                options = [
                    discord.SelectOption(label='Red', description='Your favourite colour is red', emoji='🟥'),

                ]

                super().__init__(placeholder='Choose your favourite colour...', min_values=1, max_values=5, options=options)

            async def callback(self, interaction: discord.Interaction):
                await interaction.response.send_message(f'{self.values}', ephemeral = True)


        class DropdownView(discord.ui.View):
            def __init__(self):
                super().__init__()
                self.add_item(Dropdown())

        await ctx.send('Pick your favourite colour:', view=DropdownView())



def setup(bot):
    bot.add_cog(remain(bot))
