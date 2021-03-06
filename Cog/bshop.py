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
import os


sys.path.append("..")
from functions import functions as funs
import config

client = funs.mongo_c()
db = client.bot
backs = db.bs
servers = db.servers
settings = db.settings


class bs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['backshop','backgrounds','bs','bgshop','bg','бс'], usage = '[number]', description = 'Покупка фонов для профиля')
    async def bshop(self,ctx, number:int = 0):

        bs = list(backs.find())
        d = {}

        solutions = ['◀', '▶', '🛒', '❌']
        member = ctx.author
        reaction = 'a'

        ok =  self.bot.get_emoji(744137747639566346)
        no =  self.bot.get_emoji(744137801804546138)

        user = funs.user_check(ctx.author, ctx.guild)

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

            if str(number) in user['back_inv'] or number in user['back_inv']:
                status_b = f"{ok} | Приобретён"
            else:
                status_b = f"{no} | Не приобретён"


            if b['display'] == 0 and number not in user['back_inv'] or b['display'] == 0 and str(number) not in user['back_inv']:
                status_b = f'{no} Не доступен {no}'

            emb = discord.Embed(description = '**🖼 | Библиотека фонов**', color = b['color'])
            emb.add_field(name= f"📜 | Информация", value = f"Стоимость: {d[str(number)]['price']}\nАвтор: <@{d[str(number)]['creator_id']}>\nСтатус: {status_b}", inline = False)

            if status_b == f"{ok} | Приобретён":
                emb.add_field(name= f"🎋 | Для владельца", value = f"Так как фон приобретён, при нажатии 🛒 вы установите фон.", inline = False)

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
            nonlocal user
            if str(reaction.emoji) == '◀':
                await msg.remove_reaction('◀', member)
                number -= 1
                if number > -1:
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
                if b['display'] == 0 and str(number) not in user['back_inv']:
                    t = False
                if b['display'] == 0 and number not in user['back_inv']:
                    t = False

                if t == True:
                    if user['Nitro'] == True:
                        emb = discord.Embed(description = f'Фон успешно установлен на #{number}!',color=0xf03e65)

                        try:
                            emb.set_author(name = f'{ctx.author}', icon_url = f'{ctx.author.avatar.url}')
                        except:
                            emb.set_author(name = f'{ctx.author}')

                        await ctx.send(embed = emb)

                        funs.user_update(ctx.author.id, member.guild, 'back', number)

                    else:

                        if str(number) in user["back_inv"] or number in user["back_inv"]:
                            funs.user_update(ctx.author.id, member.guild, 'back', number)

                            emb = discord.Embed(description = f'Фон успешно установлен на #{number}!',color=0xf03e65)

                            try:
                                emb.set_author(name = f'{ctx.author}', icon_url = f'{ctx.author.avatar.url}')
                            except:
                                emb.set_author(name = f'{ctx.author}')

                            await ctx.send(embed = emb)
                        else:
                            bsk = backs.find_one({"bid": number})
                            if user['money'] >= bsk['price']:

                                emb = discord.Embed(description = f'Фон успешно приобретён #{number}!',color=0xf03e65)

                                try:
                                    emb.set_author(name = f'{ctx.author}', icon_url = f'{ctx.author.avatar.url}')
                                except:
                                    emb.set_author(name = f'{ctx.author}')

                                await ctx.send(embed = emb)

                                inv = user['back_inv']
                                inv.append(number)
                                funs.user_update(ctx.author.id, member.guild, 'back_inv', inv)
                                funs.user_update(ctx.author.id, member.guild, 'back', number)
                                funs.user_update(ctx.author.id, member.guild, 'money', user['money'] - bsk['price'])


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

    @commands.command(usage = '[@member]', description = 'Инвентарь фонов', aliases = ['bi'])
    async def back_inv(self,ctx, member: discord.Member = None):

        bs = list(backs.find())
        d = {}

        if member == None:
            member = ctx.author

        reaction = 'a'
        number = 1

        user = funs.user_check(member, ctx.guild)


        if user["Nitro"] == True:
            await ctx.send(f'У вас имеются все фоны, загляните в {ctx.prefix}bshop')
            return

        result = sorted([int(item) for item in user["back_inv"]])

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

        if ctx.author != member:
            text = f'\n🌮 | {ctx.author.mention}, вы просматриваете профиль {member.mention}'
            solutions = ['◀', '▶', '❌']
        else:
            solutions = ['◀', '▶', '🖼', '❌']
            text = ''


        def embed(number):
            emb = discord.Embed(title = "Инвентарь фонов", description =
            f"🎭 | Автор: <@{d[str(number)]['creator_id']}> | 🖼 Установлен: {user['back']}\n🥞 | В наличии: {len(d.keys())} шт." + text, color = int(d[str(number)]["emb_color"]))
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
            nonlocal user
            nonlocal ctx
            if str(reaction.emoji) == '◀':
                await msg.remove_reaction('◀', ctx.author)
                number -= 1
                if number > 0:
                    await msg.edit(embed = embed(number))
                    await reackt()
                else:
                    number = int(list(d)[-1])
                    await msg.edit(embed = embed(number))
                    await reackt()

            elif str(reaction.emoji) == '▶':
                await msg.remove_reaction('▶', ctx.author)
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
                if ctx.author.id == member.id:
                    user.update({"back": d[str(number)]["id"]})
                    emb = discord.Embed(description = f'Фон успешно установлен на #{d[str(number)]["id"]}!',color=0xf03e65)

                    try:
                        emb.set_author(name = f'{ctx.author}', icon_url = f'{ctx.author.avatar.url}')
                    except:
                        emb.set_author(name = f'{ctx.author}')

                    await ctx.send(embed = emb)

                funs.user_update(member.id, member.guild, 'back', d[str(number)]["id"])

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

    @commands.command(usage = '(url) [type]', description = 'Подача заявки на новый фон.')
    async def bs_app(self, ctx, link, type = 'png'):

        try:
            emb = discord.Embed(description = "-", color=0xf03e65)
            emb.set_image(url = link)
            mms = await ctx.send(embed = emb)
            try:
                await mms.delete()
            except:
                pass
        except:
            await ctx.send("Требовалось указать ссылку!")
            return

        if type not in ['png', 'gif']:
            await ctx.send("Требовалось указать png или gif!")
            return

        member = ctx.author

        server = servers.find_one({"server": ctx.guild.id})
        user = funs.user_check(ctx.author, ctx.guild)

        s = settings.find_one({"sid": 1})
        url = link
        progress_bar = [238, 74, 84]
        expn = 5 * user['lvl']*user['lvl'] + 50 * user['lvl'] + 100

        name = member.name
        tag = member.discriminator

        headline = ImageFont.truetype("fonts/NotoSans-Bold.ttf", size = 25)
        para = ImageFont.truetype("fonts/NotoSans-Bold.ttf", size = 30)


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

        def bl_f(im):
            mask = Image.new('L',(800, 400))
            ImageDraw.Draw(mask).polygon(xy=[(0, 0),(340, 0),(500,400),(0,400)], fill = 250)
            mask = mask.filter(ImageFilter.BoxBlur(1.5))
            im.paste(im.filter( ImageFilter.GaussianBlur(radius=2) ), mask=mask)
            return im

        t = '?'

        alpha = Image.open('elements/alpha.png')

        if type == "png":

            response = requests.get(url, stream = True)
            response = Image.open(io.BytesIO(response.content))
            img = response.convert("RGBA")

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
        ImageDraw.Draw(mask).polygon(xy=[(0, 0),(340, 0),(500,400),(0,400)], fill = 153)
        ImageDraw.Draw(bar).polygon(xy=[(0, 0),(340, 0),(500,400),(0,400)], fill = (0,0,0))
        bar = bar.filter(ImageFilter.BoxBlur(0.5))
        mask = mask.filter(ImageFilter.BoxBlur(1.5))
        alpha = Image.composite(bar, alpha, mask)

        text_image = Image.open(f"elements/text.png")
        alpha = trans_paste(text_image, alpha, 1.0)

        # прогресс бар
        percent = round(user['xp'] / expn * 100)
        if percent > 100:
            percent = 100
        width, height = (800, 400)

        progress_width = 420 /100 * percent
        progress_height = 20
        x0 = 30
        y0 = height * (82 / 100)

        x1 = x0 + progress_width
        y1 = y0 + progress_height
        bar = Image.new('RGB',(800, 400))
        mask = Image.new('L',(800, 400))
        ImageDraw.Draw(mask).polygon(xy=[(x0,y0+10),(x0-9,y1+10),(440,y1+10),(440,y0+10)], fill = 255)
        ImageDraw.Draw(bar).polygon(xy=[(x0,y0+10),(x0-9,y1+10),(440,y1+10),(440,y0+10)], fill = (255, 255, 255), outline = (0, 0, 0))
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
        if user['voice_time'] >= 86400:
            text = funs.time_end(user['voice_time'])[:-4]
        if user['voice_time'] >= 604800:
            text = funs.time_end(user['voice_time'])[:-8]
        else:
            text = funs.time_end(user['voice_time'])

        idraw.text((60,195), f"{text} #{t}" , font = para)
        idraw.text((15,360), f"{name}#{tag}", font = headline)

        idraw.text((60,242), f"{user['money']} #{t}", font = para)
        idraw.text((260,50), f"{len(user['rep'][0])}", font = para)
        idraw.text((260,90), str(len(user['rep'][1])), font = para)
        idraw.text((230,288), f"{user['xp']} / {expn}" , font = para)
        idraw.text((60,288), f"{user['lvl']} #{t}" , font = para)


        if type == "png":
            img = bl_f(img)
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
            if type == 'png': type = 'Статичная картинка'
            if type == 'gif': type = 'Анимированная картинка'

            if str(reaction.emoji) == '✅':

                await msg.remove_reaction('✅', member)
                channel = await self.bot.fetch_channel(config.bs_op)

                try:
                    bs_num = s['bs_num']
                except:
                    bs_num = 1
                    settings.update_one({"sid": 1},{'$set': {'bs_num': 1}})

                bs = s['bs']
                bs_id = bs_num + 1


                embed = discord.Embed(title = f'ID {bs_id}', description = f'Автор: <@{ctx.author.id}>\nУкзанный формат: {type}\nURL: {link}')
                embed.set_image(url=link)
                await msg.clear_reactions()
                m = await channel.send(embed=embed)

                for x in ['✅', '❌']:
                    await m.add_reaction(x)

                s['bs'].update( {str(bs_id): {'author': ctx.author.id, 'url': link, 'type': type, 'message': m.id, 'server':ctx.guild.id, "status": None} })
                settings.update_one({"sid": 1},{'$set': {'bs': s['bs']}})
                settings.update_one({"sid": 1},{'$set': {'bs_num': bs_id}})

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

        g = self.bot.get_guild(bs['server'])

        type = bs['type']

        channel = g.get_channel(config.bs_op)
        mid = await channel.fetch_message(bs['message'])
        await mid.clear_reactions()

        if reason == None:
            embed = discord.Embed(title = f'ID {id} Отклонён', description = f'Автор: <@{bs["author"]}>\nУкзанный формат: {type}\nURL: {bs["url"]}', color = 0xf03e65)
            embed.set_image(url=bs["url"])
        if reason != None:
            embed = discord.Embed(title = f'ID {id} Отклонён', description = f'Автор: <@{bs["author"]}>\nУкзанный формат: {type}\nURL: {bs["url"]}\n\n\nПричина: {"".join(reason)}', color = 0xf03e65)
            embed.set_image(url=bs["url"])

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


    @commands.command(hidden = True, usage = '(id) (price) [type] [display]')
    async def bs_approve(self, ctx, id:int, price:int, type = None, display = '1'):

        s = settings.find_one({"sid": 1})
        if ctx.author.id not in s['moderators']:
            await ctx.send("У вас нет прав модератора бота!")
            return

        try:
            bs = s['bs'][str(id)]
        except:
            await ctx.send("Запроса с таким id не найден!")
            return

        g = self.bot.get_guild(bs['server'])
        m = g.get_member(bs['author'])

        if bs['status'] != None:
            await ctx.send("Фон уже был принят\отклонён!")
            return

        if price < 0:
            await ctx.send("Цена не может быть меньше чем 0!")
            return

        if type != None:
            if type not in ['gif', 'png']:
                await ctx.send("Такого типа не существует!")
                return

        if display not in ['1', '0']:
            await ctx.send("Такого типа не существует! (1/0)")
            return

        if type == None:
            type = bs['type']

        channel = g.get_channel(config.bs_op)
        mid = await channel.fetch_message(bs['message'])
        await mid.clear_reactions()

        embed = discord.Embed(title = f'ID {id} Принят', description = f'Автор: <@{bs["author"]}>\nФормат: {type}\nURL: {bs["url"]}\nПринял: {ctx.author.mention}\nID в магазине: {len(list(backs.find()))}', color = 0x34cb2c)
        embed.set_image(url=bs["url"])

        await mid.edit(embed= embed)

        if g != None:
            if m != None:
                try:
                    await m.send(f'Ваш фон под id {id} был принят!\nТак же он был добавлен вам в коллекцию. Вы можете проверить и установить его, у себя в инвентаре (back_inv)!')
                except:
                    pass

        user = funs.user_check(m, g)
        inv = user['back_inv']
        inv.append(len(list(backs.find())))
        funs.user_update(m, g, 'back_inv', inv)

        s['bs'].update( {str(id): {'status': True} })
        settings.update_one({"sid": 1},{'$set': {'bs': s['bs']}})

        if type in ['Статичная картинка', 'png']:
            response = requests.get(bs["url"], stream = True)
            response = Image.open(io.BytesIO(response.content))

            image = response
            output = BytesIO()
            image.save(output, 'png')
            image_pix=BytesIO(output.getvalue())

            file = discord.File(fp = image_pix, filename=f"back.png")

        else:
            fs = []
            response = requests.get(bs["url"], stream=True)
            response.raw.decode_content = True
            img = Image.open(response.raw)

            for frame in ImageSequence.Iterator(img):

                b = io.BytesIO()
                frame.save(b, format="GIF",optimize=True, quality=100)
                frame = Image.open(b)
                fs.append(frame)

            fs[0].save('back.gif', save_all=True, append_images=fs[1:], loop = 0, optimize=True, quality=100)
            file = discord.File(fp = "back.gif", filename="back.gif")

        ss_channel = await self.bot.fetch_channel(config.cloud_channel)
        msg = await ss_channel.send(content = f'🖼 | Фон {len(list(backs.find()))}', file = file)

        b = { 'bid': len(list(backs.find())),
              'url': msg.attachments[0].url,
              'price': price,
              'creator_id': bs['author'],
              'display': display,
              'color': 15744613,
              'format': type,
              'progress_bar': [238, 74, 84],
              'alpha_panel': [153],
              'panel_color': [ [0,0,0], [0,0,0] ],

        }
        backs.insert_one(b)

        await ctx.send(f"Фон {id} принят пользователем {ctx.author}")



def setup(bot):
    bot.add_cog(bs(bot))
