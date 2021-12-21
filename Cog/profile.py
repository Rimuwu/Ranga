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
import pprint

sys.path.append("..")
from ai3 import functions as funs
import config

client = funs.mongo_c()
db = client.bot
backs = db.bs
servers = db.servers
frames = db.frames

class profile(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.command(usage = '(@member) [+\-]', description = 'Повысить\понизить репутацию пользователя.')
    async def rep(self,ctx, member: discord.Member, arg=None):

        user = funs.user_check(member, member.guild)
        if user == False:
            await ctx.send(f"С ботом взаимодействовать нельзя!")
            return
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

                funs.user_update(member.id, member.guild, 'rep', user['rep'])

                embed = discord.Embed(title="+rep!", description=f"<@{member.id}> получает **+rep** от <@{ctx.author.id}>!",color=0x63d955)

                await ctx.send(embed=embed)

            elif arg == "-":
                if ctx.author.id in user['rep'][1]:
                    await ctx.send("Повторно нельзя понизить репутацию пользователю")
                    return
                if ctx.author.id in user['rep'][0]:
                    user['rep'][0].remove(ctx.author.id)

                user['rep'][1].append(ctx.author.id)
                funs.user_update(member.id, member.guild, 'rep', user['rep'])
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
        server = servers.find_one({"server": ctx.guild.id})

        back = user['back']
        bc = backs.find_one({"bid": back})
        url = bc['url']
        progress_bar = bc["progress_bar"]
        pl = bc['panel_color']
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
            ImageDraw.Draw(mask).polygon(xy=[(0, 0),(340, 0),(500,400),(0,400)], fill = 200)
            mask = mask.filter(ImageFilter.BoxBlur(1.5))
            im.paste(im.filter( ImageFilter.GaussianBlur(radius=8) ), mask=mask)
            return im

        t = dict(sorted(server['users'].items(),key=lambda x: x[1]['money'], reverse=True))
        topmn = list(t.keys()).index(str(member.id)) +1

        t = dict(sorted(server['users'].items(),key=lambda x: x[1]['lvl'], reverse=True))
        toplvl = list(t.keys()).index(str(member.id)) +1

        t = dict(sorted(server['users'].items(),key=lambda x: x[1]['voice_time'], reverse=True))
        topvoice = list(t.keys()).index(str(member.id)) +1

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
        ImageDraw.Draw(mask).polygon(xy=[(0, 0),(340, 0),(500,400),(0,400)], fill = al[0])
        ImageDraw.Draw(bar).polygon(xy=[(0, 0),(340, 0),(500,400),(0,400)], fill = (pl[0][0],pl[0][1],pl[0][2]))
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

        progress_width = 445 /100 * percent
        progress_height = 20
        x0 = 15
        y0 = height * (82 / 100)

        x1 = x0 + progress_width
        y1 = y0 + progress_height
        bar = Image.new('RGB',(800, 400))
        mask = Image.new('L',(800, 400))
        ImageDraw.Draw(mask).polygon(xy=[(x0,y0+10),(x0,y1+10),(469,y1+10),(460,y0+10)], fill = 255)
        ImageDraw.Draw(bar).polygon(xy=[(x0,y0+10),(x0,y1+10),(469,y1+10),(460,y0+10)], fill = (255, 255, 255), outline = (0, 0, 0))
        alpha = Image.composite(bar, alpha, mask)

        if user['xp'] > 0:
            pbar = Image.new('RGB', (800, 400))
            mask = Image.new('L', (800, 400))
            ImageDraw.Draw(mask).polygon(xy=[(x0,y0+10),(x0,y1+9),(x1+10,y1+10),(x1,y0+10)], fill = 255)
            mask = mask.filter(ImageFilter.BoxBlur(2))
            ImageDraw.Draw(pbar).polygon(xy=[(x0, y0+10),(x0, y1+9),(x1+10, y1+10),(x1, y0+10)], fill=(progress_bar[0], progress_bar[1], progress_bar[2])) #основной прогресс бар
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

        idraw.text((60,195), f"{text} #{topvoice}" , font = para)

        if user['guild'] != None:
            club = server['rpg']['guild'][f'{user["guild"]}']
            idraw.text((15,360), f"{name}#{tag} [{club['tag']}]", font = headline) #первое значение это отступ с лева, второе сверху
        else:
            idraw.text((15,360), f"{name}#{tag}", font = headline)

        idraw.text((60,242), f"{user['money']} #{topmn}", font = para)
        idraw.text((260,50), f"{len(user['rep'][0])}", font = para)
        idraw.text((260,90), str(len(user['rep'][1])), font = para)
        idraw.text((230,288), f"{user['xp']} / {expn}" , font = para)
        idraw.text((60,288), f"{user['lvl']} #{toplvl}" , font = para)


        embed = discord.Embed(color=0xf03e65)
        embed.set_author(name = ctx.author, url = ctx.author.avatar.url)

        reaction = 'a'

        inv = {}

        items = []
        for i in server['items'].keys():
            items.append(server['items'][i])

        for i in user['inv']:
            u = i.copy()
            del i['iid']

            if i in items:
                if i['name'] in list(inv.keys()):
                    inv.update({ i['name']: { 'it':i, 'count': inv[i['name']]['count']+1 } })
                else:
                    inv.update({ i['name']: { 'it':i, 'count': 1 } })

            if i not in items:
                if f'{i["name"]} (#{u["iid"]})' in list(inv.keys()):
                    inv.update({ f'{i["name"]} (#{u["iid"]})': { 'it':i, 'count': inv[i['name']]['count']+1 } })
                else:
                    inv.update({ f'{i["name"]} (#{u["iid"]})': { 'it':i, 'count': 1 } })


        if inv == {}:
            emb_i = discord.Embed(title = '<:inventory_b:886909340550823936> | Инвентарь', description = 'Тут пусто 🔎',color=0xf03e65)

        if inv != {}:

            emb_i = discord.Embed(title = '<:inventory_b:886909340550823936> | Инвентарь',color=0xf03e65)


            text, text2, text3, text4, text5, text6 = '', '', '', '', '', ''
            num, num2, num3, num4, num5, num6 = 0, 0, 0, 0, 0, 0

            for i in inv.keys():
                item = inv[i]['it']
                if item['quality'] == 'n':
                    qul = '<:normal_q:781531816993620001>'
                elif item['quality'] == 'u':
                    qul = '<:unusual_q:781531868780691476>'
                elif item['quality'] == 'r':
                    qul = '<:rare_q:781531919140651048>'
                elif item['quality'] == 'o':
                    qul = '<:orate_q:781531996866084874>'
                elif item['quality'] == 'l':
                    qul = '<:legendary_q:781532085130100737>'
                else:
                    qul = '???'

                if item['type'] == 'weapon':

                    text += f"{qul} | {item['emoji']} | {i}: {inv[i]['count']}\n"
                    num += inv[i]['count']

                elif item['type'] == 'point':

                    text2 += f"{qul} | {item['emoji']} | {i}: {inv[i]['count']}\n"
                    num2 += inv[i]['count']

                elif item['type'] == 'eat':

                    text3 += f"{qul} | {item['emoji']} | {i}: {inv[i]['count']}\n"
                    num3 += inv[i]['count']

                elif item['type'] == 'pet':

                    text4 += f"{qul} | {item['emoji']} | {i}: {inv[i]['count']}\n"
                    num4 += inv[i]['count']

                elif item['type'] == 'role':

                    text6 += f"{qul} | {item['emoji']} | {i}: {inv[i]['count']}\n"
                    num6 += inv[i]['count']

                else:
                    text5 += f"{qul} | {item['emoji']} | {i}: {inv[i]['count']}\n"
                    num5 += inv[i]['count']


            if num > 0:
                emb_i.add_field(name= f"Предметы | Оружия: {num}", value= text)
            if num2 > 0:
                emb_i.add_field(name= f"Предметы | Зелья: {num2}", value= text2)
            if num3 > 0:
                emb_i.add_field(name= f"Предметы | Еда: {num3}", value= text3)
            if num4 > 0:
                emb_i.add_field(name= f"Предметы | Питомцы: {num4}", value= text4)
            if num6 > 0:
                emb_i.add_field(name= f"Предметы | Роли: {num5}", value= text6)
            if num5 > 0:
                emb_i.add_field(name= f"Предметы | Остальное: {num5}", value= text5)


        emb_s = discord.Embed(title = ':bust_in_silhouette:  | Профиль',
        color=0xf03e65)

        if user['gm_status'] != False:
            if user['bio'] == None:
                emb_s.add_field(name="<:info:886888485796065311> | Информация", value=f'Тут пусто 🔎', inline = False)
            if user['bio'] != None:
                emb_s.add_field(name="<:info:886888485796065311> | Информация", value=user['bio'], inline = False)
            if user['people_avatar'] != None:
                emb_s.set_thumbnail(url = user['people_avatar'])

            emb_s.add_field(name="<:hunt:886890612341739550> | Уровень наёмника", value=f'<:lvl:886876034149011486> {user["rpg_lvl"]} уровень\n<:lvl:886876034149011486> {user["rpg_xp"]} | {5 * user["rpg_lvl"]*user["rpg_lvl"] + 50 * user["rpg_lvl"] + 100}')

            emb_s.add_field(name="<:characteristic:886892962888421376> | Статистика персонажа", value=f'<:heart:886874654072008705> {user["hp"]} | {user["hpmax"]}\n<:c_mana:886893705594818610> {user["mana"]} | {user["manamax"]} ')

            if user['weapon'] == None:
                weapon = "Руки"
            else:
                weapon = user['weapon']['name']

            if user['armor'] == None:
                armor = "Майка"
            else:
                armor = user['armor']['name']

            if user['pet'] == None:
                pet = "Отсутсвует"
            else:
                pet = user['pet']['name']

            emb_s.add_field(name="<:p_backpack:886909262712930325> | Снаряжение", value=f'Оружие: {weapon}\n<:armor:827220888130682880> | {armor}\n<:pet1:886919865544368158> | {pet}')


        if bc['format'] == "png":
            img = bl_f(img)
            bg_img = img
            fg_img = alpha
            img = trans_paste(fg_img, bg_img, 1.0)

            image = img
            output = BytesIO()
            image.save(output, 'png')
            image_pix=BytesIO(output.getvalue())

            file = discord.File(fp = image_pix, filename="user_card.png")
            emb_i.set_image(url="attachment://user_card.png")
            emb_s.set_image(url="attachment://user_card.png")

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
            emb_i.set_image(url="attachment://user_card.gif")
            emb_s.set_image(url="attachment://user_card.gif")


        msg = await ctx.send(file=file, embed=emb_s)

        try:
            os.remove('user_card.gif')
        except Exception:
            pass

        page_s = 'stat'

        def check(reaction, user):
            nonlocal msg
            return user == ctx.author and str(reaction.emoji) == '<:ch_page:886895064331202590>' and str(reaction.message) == str(msg)

        async def rr():
            nonlocal reaction
            nonlocal page_s

            if str(reaction.emoji) == '<:ch_page:886895064331202590>':
                await msg.remove_reaction('<:ch_page:886895064331202590>', ctx.author)
                if page_s == 'inv':
                    page_s = 'stat'
                    await msg.edit(embed = emb_s)
                else:
                    page_s = 'inv'
                    await msg.edit(embed = emb_i)


        async def reackt():
            nonlocal reaction
            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=30.0, check = check)
            except asyncio.TimeoutError:
                await msg.clear_reactions()
                return
            else:
                await rr(), await reackt()

        await msg.add_reaction('<:ch_page:886895064331202590>')

        await reackt()


    @commands.command(usage = '(avatar character\none) (bio) ', description = 'Установить информацию о своём аватаре.')
    async def bio(self,ctx, avatar:str, *, bio:str):

        user = funs.user_check(ctx.author, ctx.author.guild)
        server = servers.find_one({"server": ctx.guild.id})

        if user['gm_status'] == False:
            await ctx.send("Требуется быть зарегестрированным пользователем в рпг системе!")
            return

        if user['gm_status'] == True:

            if avatar != 'none':
                try:
                    emb1 = discord.Embed(title = "Изображение", color=server['embed_color'])
                    emb1.set_thumbnail(url = avatar)
                    msg2 = await ctx.send(embed = emb1)
                except Exception:
                    await ctx.send("Требовалось указать __ссылку__, повторите настройку ещё раз.")
                    return

                try:
                    await msg2.delete()
                except Exception:
                    pass

                funs.user_update(ctx.author.id, ctx.author.guild, 'people_avatar', avatar)
            else:
                pass

            desc = ' '.join(bio)

            if len(desc) > 1024:
                await ctx.send("Тебовалось указать описание персонажа <= 1024 символа")
                return

            funs.user_update(ctx.author.id, ctx.author.guild, 'bio', bio)

            await ctx.send("Информация и картинка персонажа настроенны!")




def setup(bot):
    bot.add_cog(profile(bot))
