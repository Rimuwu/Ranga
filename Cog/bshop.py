import nextcord as discord
from nextcord.ext import tasks, commands
from PIL import Image, ImageFont, ImageDraw, ImageOps, ImageSequence, ImageFilter
import io
from io import BytesIO
import requests
import sys
import random
from random import choice
import asyncio
import time
import pymongo
import pprint


sys.path.append("..")
from AI2 import functions as funs
import config

client = funs.mongo_c()
db = client.bot
users = db.users
backs = db.bs
servers = db.servers
settings = db.settings


class bs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['backshop','backgrounds','bs','bgshop','bg','бс'], usage = '(number)', description = 'Покупка фонов для профиля')
    async def bshop(self,ctx, number:int = 0):
        bs = list(backs.find())
        d = {}


        solutions = ['◀', '▶', '🛒', '❌']
        member = ctx.author
        reaction = 'a'

        ok =  self.bot.get_emoji(744137747639566346)
        no =  self.bot.get_emoji(744137801804546138)

        us = users.find_one({"userid": ctx.author.id})

        if number < 0 or number > backs.count():
            number = 0

        for i in bs:
            d.update({str(i['bid']) : {
             'url': i['url'],
             'display': i['display'],
             'creator_id': i['creator_id'],
             'emb_color': i['color'],
             'price': i['price']
            }})



        def embed(number):

            b = backs.find_one({"bid": number})

            if str(number) in us['back_inv']:
                status_b = ok
            else:
                status_b = no

            if us['Nitro'] == True:
                status_b = ok

            if b['display'] == 0 and number not in us['back_inv'] or b['display'] == 0 and str(number) not in us['back_inv']:
                status_b = f'{no} Не доступен {no}'

            emb = discord.Embed(title = "Покупка фонов", description =
            f"Стоимость: {d[str(number)]['price']}\n Автор: <@{d[str(number)]['creator_id']}>\n Статус: {status_b}", color = int(d[str(number)]["emb_color"]))
            emb.set_image(url =f'{d[str(number)]["url"]}')
            emb.set_footer(text = f'ID {number} | {len(bs)-1}')
            return emb

        msg = await ctx.send(embed = embed(number))

        def check( reaction, user):
            nonlocal msg
            return user == ctx.author and str(reaction.emoji) in solutions and str(reaction.message) == str(msg)

        async def rr():
            nonlocal reaction
            nonlocal number
            nonlocal bs
            nonlocal us
            if str(reaction.emoji) == '◀':
                await msg.remove_reaction('◀', member)
                number -= 1
                if number > 0:
                    await msg.edit(embed = embed(number))
                    await reackt()
                else:
                    number = len(bs)-1
                    await msg.edit(embed = embed(number))
                    await reackt()

            elif str(reaction.emoji) == '▶':
                await msg.remove_reaction('▶', member)
                number += 1
                if number == len(bs):
                    number = 0
                    await msg.edit(embed = embed(number))
                    await reackt()
                else:
                    await msg.edit(embed = embed(number))
                    await reackt()

            elif str(reaction.emoji) == '❌':
                await msg.clear_reactions()
                return

            elif str(reaction.emoji) == '🛒':
                await msg.remove_reaction('🛒', member)
                b = backs.find_one({"bid": number})

                t = True
                if b['display'] == 0 and str(number) not in us['back_inv']:
                    t = False
                if b['display'] == 0 and number not in us['back_inv']:
                    t = False

                if t == True:
                    if us['Nitro'] == True:
                        emb = discord.Embed(description = f'Фон успешно установлен на #{number}!',color=0xf03e65)
                        emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar_url))
                        await ctx.send(embed = emb)

                        users.update_one({'userid':ctx.author.id},{'$set':{"back": number}})
                    else:

                        if str(number) in us["back_inv"] or number in us["back_inv"]:
                            users.update_one({'userid':ctx.author.id},{'$set':{"back": number}})

                            emb = discord.Embed(description = f'Фон успешно установлен на #{number}!',color=0xf03e65)
                            emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar_url))
                            await ctx.send(embed = emb)
                        else:
                            bsk = backs.find_one({"bid": number})
                            if us['money'] >= bsk['price']:

                                emb = discord.Embed(description = f'Фон успешно приобретён #{number}!',color=0xf03e65)
                                emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar_url))
                                await ctx.send(embed = emb)

                                inv = us['back_inv']
                                inv.append(number)
                                users.update_one({'userid':ctx.author.id},{'$set':{"back_inv": inv}})
                                users.update_one({'userid':ctx.author.id},{'$set':{"back": number}})
                                users.update_one({'userid':ctx.author.id},{'$inc':{"money": -bsk['price']}})
                await reackt()

        async def reackt():
            nonlocal reaction
            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=30.0, check = check)
            except asyncio.TimeoutError:
                await msg.clear_reactions()
            else:
                await rr()

        for x in solutions:
            await msg.add_reaction(x)
        await reackt()

    @commands.command(usage = '-', description = 'Инвентарь фонов')
    async def back_inv(self,ctx):

        bs = list(backs.find())
        d = {}


        solutions = ['◀', '▶', '🖼', '❌']
        member = ctx.author
        reaction = 'a'
        number = 1

        ok =  self.bot.get_emoji(744137747639566346)
        no =  self.bot.get_emoji(744137801804546138)

        us = users.find_one({"userid": ctx.author.id})


        if us["Nitro"] == True:
            await ctx.send(f'У вас имеются все фоны, загляните в {ctx.prefix}bshop')
            return

        result = sorted([int(item) for item in us["back_inv"]])

        nl = 1
        for i in result:
            i = int(i)
            b = backs.find_one({"bid": i})
            d.update({str(nl) : {
             'url': b['url'],
             'display': b['display'],
             'creator_id': b['creator_id'],
             'emb_color': b['color'],
             'price': b['price'],
             'id': b['bid']
            }})
            nl += 1


        def embed(number):
            emb = discord.Embed(title = "Инвентарь фонов", description =
            f"🎭Автор: <@{d[str(number)]['creator_id']}> | 🖼Установлен: {us['back']}", color = int(d[str(number)]["emb_color"]))
            emb.set_image(url =f'{d[str(number)]["url"]}')
            emb.set_footer(text = f'ID {d[str(number)]["id"]}')
            return emb

        msg = await ctx.send(embed = embed(number))

        def check( reaction, user):
            nonlocal msg
            return user == ctx.author and str(reaction.emoji) in solutions and str(reaction.message) == str(msg)

        async def rr():
            nonlocal reaction
            nonlocal number
            nonlocal bs
            nonlocal us
            if str(reaction.emoji) == '◀':
                await msg.remove_reaction('◀', member)
                number -= 1
                if number > 0:
                    await msg.edit(embed = embed(number))
                    await reackt()
                else:
                    number = int(list(d)[-1])
                    await msg.edit(embed = embed(number))
                    await reackt()

            elif str(reaction.emoji) == '▶':
                await msg.remove_reaction('▶', member)
                number += 1
                if number > int(list(d)[-1]):
                    number = 1
                    await msg.edit(embed = embed(number))
                    await reackt()
                else:
                    await msg.edit(embed = embed(number))
                    await reackt()

            elif str(reaction.emoji) == '❌':
                await msg.clear_reactions()

            elif str(reaction.emoji) == '🖼':
                await msg.remove_reaction('🖼', member)
                us.update({"back": d[str(number)]["id"]})
                emb = discord.Embed(description = f'Фон успешно установлен на #{d[str(number)]["id"]}!',color=0xf03e65)
                emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar_url))
                await ctx.send(embed = emb)

                users.update_one({'userid':ctx.author.id},{'$set':{"back": d[str(number)]["id"]}})

                await reackt()



        async def reackt():
            nonlocal reaction
            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=30.0, check = check)
            except asyncio.TimeoutError:
                await msg.clear_reactions()
            else:
                await rr()

        for x in solutions:
            await msg.add_reaction(x)
        await reackt()

    @commands.command(usage = '(url) [type]', description = 'Подача заявки на новый фон.', help = 'Грустные')
    async def bs_app(self, ctx, link, type = 'png'):


        try:
            emb = discord.Embed(description = "-", color=0xf03e65)
            emb.set_image(url = link)
        except:
            await ctx.send("Требовалось указать ссылку!")
            return

        if type not in ['png', 'gif']:
            await ctx.send("Требовалось указать png или gif!")
            return

        member = ctx.author

        user = funs.user_check(member, ctx.guild)
        main = users.find_one({"userid": member.id})
        server = servers.find_one({"server": ctx.guild.id})

        back = 1
        s = settings.find_one({"sid": 1})
        bc = backs.find_one({"bid": back})
        url = link
        progress_bar = bc["progress_bar"]
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

        if type == "png":

            response = requests.get(url, stream = True)
            response = Image.open(io.BytesIO(response.content))
            response = response.convert("RGBA")
            img = response.resize((800, 400), Image.ANTIALIAS) # улучшение качества

        if type == "gif":

            response = requests.get(url, stream=True)
            response.raw.decode_content = True
            img = Image.open(response.raw)

        sze = f"{img.size[0]}x{img.size[1]}"

        if sze != '800x400':
            await ctx.send("Требуется указать изображение размером 800 на 400 пикселей!")
            return

        mask = Image.new('L',(800, 400))
        bar = Image.new('RGB',(800, 400))

        #панель
        ImageDraw.Draw(mask).polygon(xy=[(0, 0),(402, 0),(285,400),(0,400)], fill = 153)
        ImageDraw.Draw(bar).polygon(xy=[(0, 0),(402, 0),(285,400),(0,400)], fill = (0,0,0))
        bar = bar.filter(ImageFilter.BoxBlur(0.5))
        mask = mask.filter(ImageFilter.BoxBlur(1.5))
        alpha = Image.composite(bar, alpha, mask)

        #панель 2
        mask = Image.new('L',(800, 400))
        bar = Image.new('RGB',(800, 400))
        ImageDraw.Draw(mask).polygon(xy=[(319, 285),(800, 285),(800,400),(285,400)], fill = 153 )
        ImageDraw.Draw(bar).polygon(xy=[(319, 285),(800, 285),(800,400),(285,400)], fill = (0,0,0))
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


        idraw = ImageDraw.Draw(alpha)

        idraw.text((315,360), f"{name}#{tag}", font = headline)

        idraw.text((60,348), f"{user['money']} #{topmn}", font = para)
        idraw.text((260,50), f"{len(main['rep'][0])}", font = para)
        idraw.text((260,90), str(len(main['rep'][1])), font = para)
        idraw.text((505,282), f"{user['xp']}  |  {expn}" , font = para)
        idraw.text((60,298), f"{user['lvl']} #{toplvl}" , font = para)      #55,265


        if type == "png":

            bg_img = img
            fg_img = alpha
            img = trans_paste(fg_img, bg_img, 1.0)

            image = img
            output = BytesIO()
            image.save(output, 'png')
            image_pix=BytesIO(output.getvalue())

            file = discord.File(fp = image_pix, filename="user_card.png")
            embed = discord.Embed(description = 'Примерный вид нового фона\nОтправить фон на рассмотрение?\nНажмите ✅ или ❌', color=server['embed_color'])
            embed.set_image(url="attachment://user_card.png")


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
            embed = discord.Embed(description = 'Примерный вид нового фона\nОтправить фон на рассмотрение?\nНажмите ✅ или ❌', color=server['embed_color'])
            embed.set_image(url="attachment://user_card.gif")

            try:
                os.remove('user_card.gif')
            except Exception:
                pass

        msg = await ctx.send(file=file, embed=embed)

        solutions = ['✅', '❌']
        reaction = 'a'

        def check( reaction, user):
            nonlocal msg
            return user == ctx.author and str(reaction.emoji) in solutions and str(reaction.message) == str(msg)

        async def rr():
            nonlocal reaction
            nonlocal server
            nonlocal s
            nonlocal ctx
            nonlocal type
            nonlocal link
            nonlocal msg
            nonlocal sze
            if str(reaction.emoji) == '✅':

                await msg.remove_reaction('✅', member)
                channel = await self.bot.fetch_channel(880148384416153682)

                bs = s['bs']
                try:
                    bs_id = max(bs.keyd()) + 1
                except:
                    bs_id = 1

                embed = discord.Embed(title = f'ID {bs_id}', description = f'Автор: {ctx.author.id}\nУкзанный формат: {type}\nURL: {link}\n{sze}')
                embed.set_image(url=link)
                await msg.clear_reactions()
                m = await channel.send(embed=embed)

                for x in ['✅', '❌']:
                    await m.add_reaction(x)

                s['bs'].update( {str(bs_id): {'author': ctx.author.id, 'url': link, 'type': type, 'message': m.id, 'server':ctx.guild.id, "status": None} })
                settings.update_one({"sid": 1},{'$set': {'bs': s['bs']}})

                await ctx.send("Фон отправлен на рассмотрение!")
                return

            elif str(reaction.emoji) == '❌':
                await msg.clear_reactions()
                return

        async def reackt():
            nonlocal reaction
            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=30.0, check = check)
            except asyncio.TimeoutError:
                await msg.clear_reactions()
                return
            else:
                await rr()
        try:
            for x in solutions:
                await msg.add_reaction(x)
            await reackt()
        except:
            return


    @commands.command(hidden = True, usage = '(id) [reason]')
    async def bs_deny(self, ctx, id:int, *, reason = None):
        s = settings.find_one({"sid": 1})
        if ctx.author.id not in s['moderators']:
            await ctx.send("У вас нет прав модератора бота!")
            return

        try:
            bs = s['bs'][str(id)]
        except:
            await ctx.send("Запроса с таким id не найден!")
            return

        if bs['status'] != None:
            await ctx.send("Фон уже был принят\отклонён!")
            return

        channel = self.bot.get_channel(880148384416153682)
        mid = await channel.fetch_message(bs['message'])
        await mid.clear_reactions()

        if reason == None:
            embed = discord.Embed(title = f'ID {id} Отклонён', description = f'Автор: {bs["author"]}\nУкзанный формат: {bs["type"]}\nURL: {bs["url"]}\n{bs["size"]}', color = 0xf03e65)
            embed.set_image(url=bs["url"])
        if reason != None:
            embed = discord.Embed(title = f'ID {id} Отклонён', description = f'Автор: {bs["author"]}\nУкзанный формат: {bs["type"]}\nURL: {bs["url"]}\n\n\nПричина: {"".join(reason)}', color = 0xf03e65)
            embed.set_image(url=bs["url"])

            g = self.bot.get_guild(bs['server'])
            if g != None:
                m = g.get_member(bs['author'])
                if m != None:
                    try:
                        await m.send(f'Ваш фон под id {id} был отклонён по причине: {reason}')
                    except:
                        pass

        await mid.edit(embed= embed)

        s['bs'].update( {str(id): {'status': False} })
        settings.update_one({"sid": 1},{'$set': {'bs': s['bs']}})

        await ctx.send(f"Фон {id} отклонён пользователем {ctx.author}")


    @commands.command(hidden = True, usage = '(id) (price) [type]')
    async def bs_approve(self, ctx, id:int, price:int, type = None):
        s = settings.find_one({"sid": 1})
        if ctx.author.id not in s['moderators']:
            await ctx.send("У вас нет прав модератора бота!")
            return

        try:
            bs = s['bs'][str(id)]
        except:
            await ctx.send("Запроса с таким id не найден!")
            return

        if bs['status'] != None:
            await ctx.send("Фон уже был принят\отклонён!")
            return

        if price < 0:
            if type not in ['gif', 'png']:
                await ctx.send("Цена не может быть меньше чем 0!")
                return

        if type != None:
            if type not in ['gif', 'png']:
                await ctx.send("Такого типа не существует!")
                return
        if type == None:
            type = bs['type']

        channel = self.bot.get_channel(880148384416153682)
        mid = await channel.fetch_message(bs['message'])
        await mid.clear_reactions()

        embed = discord.Embed(title = f'ID {id} Принят', description = f'Автор: {bs["author"]}\nФормат: {type}\nURL: {bs["url"]}\nПринял: {ctx.author.mention}\nID в магазине: {len(list(backs.find()))}', color = 0x34cb2c)
        embed.set_image(url=bs["url"])

        await mid.edit(embed= embed)

        g = self.bot.get_guild(bs['server'])
        if g != None:
            m = g.get_member(bs['author'])
            if m != None:
                try:
                    await m.send(f'Ваш фон под id {id} был отклонён по причине: {reason}')
                except:
                    pass


        s['bs'].update( {str(id): {'status': True} })
        settings.update_one({"sid": 1},{'$set': {'bs': s['bs']}})


        b = { 'bid': len(list(backs.find())),
              'url': bs["url"],
              'price': price,
              'url': bs["url"],
              'creator_id': bs['author'],
              'display': 1,
              'color': 15744613,
              'format': type,
              'progress_bar': [238, 74, 84],
              'alpha_panel': [153, 153],
              'panel_color': [ [0,0,0], [0,0,0] ],

        }
        backs.insert_one(b)

        await ctx.send(f"Фон {id} принят пользователем {ctx.author}")



def setup(bot):
    bot.add_cog(bs(bot))
