import nextcord as discord
from nextcord.ext import tasks, commands
import requests
from PIL import Image, ImageFont, ImageDraw, ImageOps, ImageSequence, ImageFilter
import io
from io import BytesIO
import sys
import random
from random import choice
import asyncio
import time
import pymongo
import os

sys.path.append("..")
from ai3 import functions as funs
import config

client = funs.mongo_c()
db = client.bot
users = db.users
backs = db.bs
servers = db.servers
clubs = db.clubs
frames = db.frames

class profile(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.command(usage = '(@member) [+\-]', description = 'Повысить\понизить репутацию пользователя.')
    async def rep(self,ctx, member: discord.Member=None, arg=None):

        user = users.find_one({"userid": member.id})
        server = servers.find_one({"server": ctx.guild.id})

        if member == ctx.author:
            await ctx.send(f"<@{ctx.author.id}> не хитри")
            return

        if member == None:
            await ctx.send(f"Укажите пользователя")
            return

        else:
            if arg == "+" or arg == None:
                if ctx.author.id in user['rep'][0]:
                    await ctx.send("Повторно нельзя повысить репутацию пользователю")
                    return
                if ctx.author.id in user['rep'][1]:
                    user['rep'][1].remove(ctx.author.id)


                user['rep'][0].append(ctx.author.id)
                users.update_one({'userid':member.id},{'$set':{"rep": user['rep']}})
                embed = discord.Embed(title="+rep!", description=f"<@{member.id}> получает **+rep** от <@{ctx.author.id}>!",color=0x63d955)
                await ctx.send(embed=embed)

            elif arg == "-":
                if ctx.author.id in user['rep'][1]:
                    await ctx.send("Повторно нельзя понизить репутацию пользователю")
                    return
                if ctx.author.id in user['rep'][0]:
                    user['rep'][0].remove(ctx.author.id)

                user['rep'][1].append(ctx.author.id)
                users.update_one({'userid':member.id},{'$set':{"rep": user['rep']}})
                embed = discord.Embed(title="-rep!", description=f"<@{member.id}> получает **-rep** от <@{ctx.author.id}>!",color=server['embed_color'])
                await ctx.send(embed=embed)
            else:
                await ctx.send("Такой функции как "+ str(arg) + " не существует, имеется только + или -")

    @commands.command(aliases = ["я", "профиль", "p"])
    @commands.cooldown(1, 2, commands.BucketType.guild)
    async def profile(self,ctx, member: discord.Member = None):
        if member == None:
            member = ctx.author

        user = funs.user_check(member, ctx.guild)
        print(user)
        main = users.find_one({"userid": member.id})
        server = servers.find_one({"server": ctx.guild.id})

        back = main['back']
        bc = backs.find_one({"bid": back})
        url = bc['url']
        progress_bar = bc["progress_bar"]
        al = bc['alpha_panel']
        pl = bc['panel_color']
        expn = 5 * user['lvl']*user['lvl'] + 50 * user['lvl'] + 100

        name = member.name
        tag = member.discriminator

        headline = ImageFont.truetype("fonts/NotoSans-Bold.ttf", size = 25)
        para = ImageFont.truetype("fonts/NotoSans-Bold.ttf", size = 30)


        if ctx.author == member:
            users.update_one({'userid': ctx.author.id}, {'$set': {'username':f"{name}#{tag}"}})

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

        def pixel_img(image, pixel_size=8):
            image = image.resize((image.size[0] // pixel_size, image.size[1] // pixel_size), Image.NEAREST)
            image = image.resize((image.size[0] * pixel_size, image.size[1] * pixel_size), Image.NEAREST)
            return image

        t = dict(sorted(server['users'].items(),key=lambda x: x[1]['money'], reverse=True))
        topmn = list(t.keys()).index(str(member.id)) +1

        t = dict(sorted(server['users'].items(),key=lambda x: x[1]['lvl'], reverse=True))
        toplvl = list(t.keys()).index(str(member.id)) +1

        alpha = Image.open('elements/alpha.png')

        if bc['format'] == "png":

            response = requests.get(url, stream = True)
            response = Image.open(io.BytesIO(response.content))
            response = response.convert("RGBA")
            img = response.resize((800, 400), Image.ANTIALIAS) # улучшение качества

        if bc['format'] == "gif":

            response = requests.get(url, stream=True)
            response.raw.decode_content = True
            img = Image.open(response.raw)


        mask = Image.new('L',(800, 400))
        bar = Image.new('RGB',(800, 400))

        #панель
        ImageDraw.Draw(mask).polygon(xy=[(0, 0),(402, 0),(285,400),(0,400)], fill = al[0])
        ImageDraw.Draw(bar).polygon(xy=[(0, 0),(402, 0),(285,400),(0,400)], fill = (pl[0][0],pl[0][1],pl[0][2]))
        bar = bar.filter(ImageFilter.BoxBlur(0.5))
        mask = mask.filter(ImageFilter.BoxBlur(1.5))
        alpha = Image.composite(bar, alpha, mask)

        #панель 2
        mask = Image.new('L',(800, 400))
        bar = Image.new('RGB',(800, 400))
        ImageDraw.Draw(mask).polygon(xy=[(319, 285),(800, 285),(800,400),(285,400)], fill = al[1] )
        ImageDraw.Draw(bar).polygon(xy=[(319, 285),(800, 285),(800,400),(285,400)], fill = (pl[1][0],pl[1][1],pl[1][2]))
        bar = bar.filter(ImageFilter.BoxBlur(0.5))
        mask = mask.filter(ImageFilter.BoxBlur(1.5))

        alpha = Image.composite(bar, alpha, mask)

        if ctx.author == member:
            users.update_one({'userid': ctx.author.id}, {'$set': {'username':f"{name}#{tag}"}})

        text_image = Image.open(f"elements/text.png")
        alpha = trans_paste(text_image, alpha, 1.0)

        # прогресс бар
        percent = round(user['xp'] / expn * 100)
        if percent > 100:
            percent = 100
        width, height = (800, 400)

        progress_width = 420 /100 * percent
        progress_height = 20  # Пусть будет 10% от высоты
        x0 = 330
        y0 = height * (80 / 100)  # 80% от высоты

        x1 = x0 + progress_width
        y1 = y0 + progress_height
        bar = Image.new('RGB',(800, 400))
        mask = Image.new('L',(800, 400))
        ImageDraw.Draw(mask).polygon(xy=[(x0,y0+10),(x0-9,y1+10),(750,y1+10),(750,y0+10)], fill = 255)
        mask = mask.filter(ImageFilter.BoxBlur(2))
        ImageDraw.Draw(bar).polygon(xy=[(x0,y0+10),(x0-9,y1+10),(750,y1+10),(750,y0+10)], fill = (255, 255, 255), outline = (0, 0, 0))
        alpha = Image.composite(bar, alpha, mask)

        if user['xp'] > 0:
            pbar = Image.new('RGB', (800, 400))
            mask = Image.new('L', (800, 400))
            ImageDraw.Draw(mask).polygon(xy=[(x0,y0+10),(x0-9,y1+10),(x1,y1+10),(x1,y0+10)], fill = 255)
            mask = mask.filter(ImageFilter.BoxBlur(2))
            ImageDraw.Draw(pbar).polygon(xy=[(x0, y0+10),(x0-9, y1+10),(x1, y1+10),(x1, y0+10)], fill=(progress_bar[0], progress_bar[1], progress_bar[2])) #основной прогресс бар
            alpha = Image.composite(pbar, alpha, mask)


        try:
            url = str(member.avatar.url)
            response1 = requests.get(url, stream = True)
            response1 = Image.open(io.BytesIO(response1.content))

        except Exception:
            byteImgIO = io.BytesIO()
            url = str(member.avatar.url)[:-9]
            response = requests.get(url, stream = True)
            response.raw.decode_content = True
            response1 = Image.open(response.raw)

        response1 = response1.convert("RGBA")
        response1 = response1.resize((150, 150), Image.ANTIALIAS)
        size = (150, 150)
        await ctx.trigger_typing()

        im = response1
        im = crop(im, size)
        im.putalpha(prepare_mask(size, 4))

        bg_img = alpha
        fg_img = im
        alpha = trans_paste(fg_img, bg_img, 1.0, (25, 25, 175, 175))

        fr = main['frame']
        if fr != None:
            fr = frames.find_one({"id": fr})

            fr_l = fr['link']

            if fr['style'] == 1:

                em = requests.get(fr_l, stream = True)
                em = Image.open(io.BytesIO(em.content))
                em = em.convert("RGBA")
                em = em.resize((210, 210), Image.ANTIALIAS)

                bg_img = alpha
                fg_img = em
                alpha = trans_paste(fg_img, bg_img, 1.0, (0, 0, 210, 210))

            if fr['style'] == 2:

                em = requests.get(fr_l, stream = True)
                em = Image.open(io.BytesIO(em.content))
                em = em.convert("RGBA")
                em = em.resize((160, 160), Image.ANTIALIAS)

                bg_img = alpha
                fg_img = em
                alpha = trans_paste(fg_img, bg_img, 1.0, (20, 20, 180, 180))

        idraw = ImageDraw.Draw(alpha)
        if main['guild'] != None:
            club = clubs.find_one({'name': main['guild']})
            idraw.text((315,360), f"{name}#{tag} [{club['tag']}]", font = headline) #первое значение это отступ с лева, второе сверху
        else:
            idraw.text((315,360), f"{name}#{tag}", font = headline)

        idraw.text((60,348), f"{user['money']} #{topmn}", font = para)
        idraw.text((260,50), f"{len(main['rep'][0])}", font = para)
        idraw.text((260,90), str(len(main['rep'][1])), font = para)
        idraw.text((505,282), f"{user['xp']}  |  {expn}" , font = para)
        idraw.text((60,298), f"{user['lvl']} #{toplvl}" , font = para)      #55,265


        if bc['format'] == "png":

            bg_img = img
            fg_img = alpha
            img = trans_paste(fg_img, bg_img, 1.0)

            image = img
            output = BytesIO()
            image.save(output, 'png')
            image_pix=BytesIO(output.getvalue())

            file = discord.File(fp = image_pix, filename="user_card.png")
            embed = discord.Embed(color=0xf03e65)
            embed.set_image(url="attachment://user_card.png")

            await ctx.send(file=file, embed=embed)


        else:
            await ctx.trigger_typing()
            fs = []
            for frame in ImageSequence.Iterator(img):
                frame = frame.convert("RGBA")
                frame = frame.resize((800, 400), Image.ANTIALIAS)

                bg_img = frame
                fg_img = alpha
                img = trans_paste(fg_img, bg_img, 1.0)


                b = io.BytesIO()
                frame.save(b, format="GIF",optimize=True, quality=75)
                frame = Image.open(b)
                fs.append(frame)


            fs[0].save('user_card.gif', save_all=True, append_images=fs[1:], loop = 0, optimize=True, quality=75)

            file = discord.File(fp = "user_card.gif", filename="user_card.gif")
            embed = discord.Embed(color=server['embed_color'])
            embed.set_image(url="attachment://user_card.gif")

            await ctx.send(file=file, embed=embed)
            try:
                os.remove('user_card.gif')
            except Exception:
                pass



def setup(bot):
    bot.add_cog(profile(bot))
