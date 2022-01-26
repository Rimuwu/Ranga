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
import pprint
from nextcord.utils import utcnow
from datetime import timedelta

sys.path.append("..")
from functions import functions as funs
import config

client = funs.mongo_c()
db = client.bot
backs = db.bs
servers = db.servers
settings = db.settings


class remain(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(usage = '(type op/v) [message]', description = 'Создать опрос.\nop - вариатны ответов (2, 3, 4, 5)\nv - да\нет')
    async def poll(self, ctx, type, *, args="Тут пусто?"):
        await ctx.channel.purge(limit = 1)
        ok = self.bot.get_emoji(744137747639566346)
        no = self.bot.get_emoji(744137801804546138)

        if type == 'v':
            message = await ctx.send(embed = discord.Embed(
                title="Опрос",
                description=args,
                color=0xf03e65).set_footer(
                text = ctx.author, icon_url = ctx.author.avatar.url).set_thumbnail(
                url= ctx.author.avatar.url)
            )
            await message.add_reaction(ok), await message.add_reaction(no)

        if type == "op":

            try:
                ms1 = await ctx.send('Укажите число от 2 до 5 (варианты ответа)')
                msg = await self.bot.wait_for('message', timeout=120.0, check = lambda message: message.author == ctx.author and message.channel.id == ctx.channel.id)
            except asyncio.TimeoutError:
                await ctx.send("Время вышло.")
                return
            else:
                try:
                    await msg.delete()
                    await ms1.delete()
                except Exception:
                    pass

                try:
                    n = int(msg.content)

                except Exception:
                    await ctx.send('Укажите число!')
                    return

            if n not in list(range(2,6)):
                await ctx.send('Требовалось указать число от 2 до 5!')

            else:

                message = await ctx.send(embed = discord.Embed(
                    title="Опрос",
                    description=args,
                    color=0xf03e65).set_footer(
                    text = ctx.author, icon_url = ctx.author.avatar.url).set_thumbnail(
                    url= ctx.author.avatar.url)
                )

                ln = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣']

                a = 0
                while a != n:
                    await message.add_reaction(ln[a])
                    a += 1


    @commands.command(hidden = True)
    async def em(self, ctx,*, args):
        await ctx.send(f"{args} | `{args}`")

    @commands.command(hidden = True)
    async def text(self, ctx, *, text):
        text = str(funs.text_replase(text, ctx.author))
        await ctx.send(text)

    @commands.command(hidden = True)
    async def time(self, ctx, t:int):
        if t == -1:
            t = int(time.time())
        text = funs.time_end(t)
        await ctx.send(f'{text}\nRT <t:{t}>\nT - <t:{t}:t>\nR - <t:{t}:R>\n\n`{text}\nRT <t:{t}>\nT - <t:{t}:t>\nR - <t:{t}:R>`')

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
    async def tt(self, ctx):

        # class Dropdown(discord.ui.Select):
        #     def __init__(self, ctx, msg, options, placeholder, min_values, max_values:int, rem_args):
        #         #options.append(discord.SelectOption(label=f''))
        #
        #         super().__init__(placeholder=placeholder, min_values=min_values, max_values=min_values, options=options)
        #
        #     async def callback(self, interaction: discord.Interaction):
        #         if ctx.author.id == interaction.user.id:
        #             await interaction.response.send_message(f'ок, {self.values[0]}', ephemeral = True)
        #
        #         else:
        #             await interaction.response.send_message(f'Жми на свои кнопки!', ephemeral = True)
        #
        #
        # class DropdownView(discord.ui.View):
        #     def __init__(self, ctx, msg, options:list, placeholder:str, min_values:int = 1, max_values:int = 1, timeout: float = 20.0, rem_args:list = []):
        #         super().__init__(timeout=timeout)
        #         self.add_item(Dropdown(ctx, msg, options, placeholder, min_values, max_values, rem_args))
        #
        #     async def on_timeout(self):
        #         self.stop()
        #         await msg.edit(view = None)
        #
        # options = []
        # for i in list(range(1,26)):
        #     options.append(discord.SelectOption(label=i))
        #
        # msg = await ctx.send('-')
        # await msg.edit(view=DropdownView(ctx, msg, options = options, placeholder = 'Сделайте выбор...', min_values = 1, max_values=1, timeout = 20.0, rem_args = []))

        options = []
        for i in list(range(1,26)):
            options.append(discord.SelectOption(label=i))

        msg = await ctx.send('-' )
        print(msg.components)

    #
    # @commands.command(hidden = True)
    # async def test(self, ctx, member: discord.Member, time:int):
    #     await member.edit(timeout=utcnow() + timedelta(seconds = time ))

    # @commands.command(hidden = True)
    # async def test(self, ctx):
    #
    #     class Dropdown(discord.ui.Select):
    #         def __init__(self):
    #
    #             # Set the options that will be presented inside the dropdown
    #             options = [
    #                 discord.SelectOption(label='Red', description='Your favourite colour is red', emoji='🟥'),
    #
    #             ]
    #
    #             super().__init__(placeholder='Choose your favourite colour...', min_values=1, max_values=5, options=options)
    #
    #         async def callback(self, interaction: discord.Interaction):
    #             await interaction.response.send_message(f'{self.values}', ephemeral = True)
    #
    #
    #     class DropdownView(discord.ui.View):
    #         def __init__(self):
    #             super().__init__()
    #             self.add_item(Dropdown())
    #
    #     await ctx.send('Pick your favourite colour:', view=DropdownView())
    #
    # @commands.command(hidden = True)
    # async def tr(self, ctx, arg1:int = -1, arg2:int = 172):
    #     if ctx.author.id != 323512096350535680:
    #         return
    #
    #     print('запуск')
    #
    #     er_l = []
    #     for i in list(range(arg1, arg2)):
    #         try:
    #             bc = backs.find_one({"bid": i})
    #             url = bc['url']
    #
    #             if bc['format'] == 'png':
    #                 response = requests.get(url, stream = True)
    #                 response = Image.open(io.BytesIO(response.content))
    #
    #                 image = response
    #                 output = BytesIO()
    #                 image.save(output, 'png')
    #                 image_pix=BytesIO(output.getvalue())
    #
    #                 file = discord.File(fp = image_pix, filename=f"back.png")
    #
    #             else:
    #                 fs = []
    #                 response = requests.get(url, stream=True)
    #                 response.raw.decode_content = True
    #                 img = Image.open(response.raw)
    #
    #                 for frame in ImageSequence.Iterator(img):
    #
    #                     b = io.BytesIO()
    #                     frame.save(b, format="GIF",optimize=True, quality=100)
    #                     frame = Image.open(b)
    #                     fs.append(frame)
    #
    #                 fs[0].save('back.gif', save_all=True, append_images=fs[1:], loop = 0, optimize=True, quality=100)
    #                 file = discord.File(fp = "back.gif", filename="back.gif")
    #
    #             msg = await ctx.send(content = f'🖼 | Фон {i}', file = file)
    #             print(i, msg.attachments[0].url)
    #
    #             backs.update_one({"bid": i}, {"$set": {'link': bc['url'], 'url': msg.attachments[0].url}})
    #         except:
    #             er_l.append(i)
    #             pass
    #
    #     print(er_l)

    @commands.command(hidden = True)
    async def gt(self, ctx):


        def trans_paste(fg_img,bg_img,alpha=10,box=(0,0)):
            fg_img_trans = Image.new("RGBA",fg_img.size)
            fg_img_trans = Image.blend(fg_img_trans,fg_img,alpha)
            bg_img.paste(fg_img_trans,box,fg_img_trans)
            return bg_img

        def prepare_mask(size, antialias = 2):
            mask = Image.new('L', (size[0] * antialias, size[1] * antialias), 0)
            ImageDraw.Draw(mask).ellipse((0, 0) + mask.size, fill=255)
            mask = mask.filter(ImageFilter.GaussianBlur(2.5))
            return mask.resize(size, Image.ANTIALIAS)

        def crop(im, s):
            w, h = im.size
            k = w / s[0] - h / s[1]

            if k > 0:
                im = im.crop(((w - h) / 2, 0, (w + h) / 2, h))
            elif k < 0:
                im = im.crop((0, (h - w) / 2, w, (h + w) / 2))

            return im.resize(s, Image.ANTIALIAS)

        # def bl_f(im):
        #     mask = Image.new('L',(800, 400))
        #     ImageDraw.Draw(mask).polygon(xy=[(0, 0),(340, 0),(500,400),(0,400)], fill = 200)
        #     mask = mask.filter(ImageFilter.BoxBlur(1.5))
        #     im.paste(im.filter( ImageFilter.GaussianBlur(radius=8) ), mask=mask)
        #     return im

        server = servers.find_one({"server": ctx.guild.id})
        guilds = server['rpg']['guilds']
        rpg_guild = server['rpg']['guilds']['-1']

        if rpg_guild['banner_url'] == None:
            url = 'https://cdn.discordapp.com/attachments/932577316649967678/932676860511420436/468ba62d-d841-4f48-8b42-f7b8a50ca2bf_Forgotten_Future___Web___Artstation.jpg'
        else:
            url = rpg_guild['banner_url']

        alpha = Image.open('elements/alpha.png').resize((1600, 400), Image.ANTIALIAS)
        response = requests.get(url, stream = True)
        response = Image.open(io.BytesIO(response.content))
        response = response.convert("RGBA")
        img = response.resize((1600, 400), Image.ANTIALIAS) # улучшение качества


        mask = Image.new('L',(800, 400))
        bar = Image.new('RGB',(800, 400))

        #панель
        ImageDraw.Draw(mask).polygon(xy=[(0, 0),(340, 0),(500,400),(0,400)], fill = 250)
        ImageDraw.Draw(bar).polygon(xy=[(0, 0),(340, 0),(500,400),(0,400)], fill = (0,0,0,0))
        bar = bar.filter(ImageFilter.BoxBlur(0.5))
        mask = mask.filter(ImageFilter.BoxBlur(1.5))
        alpha = Image.composite(bar, alpha, mask)

        # img = bl_f(img)
        bg_img = img
        fg_img = alpha
        img = trans_paste(fg_img, bg_img, 1.0)

        img.show()





def setup(bot):
    bot.add_cog(remain(bot))
