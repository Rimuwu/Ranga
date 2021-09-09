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
import os
import pymongo
import math
from datetime import datetime, timedelta, timezone
import aiohttp
import pprint

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
settings = db.settings

voice_dict = {}
start_time = time.time()

stat_list = [
               "Играю с твоей душой...",
               'Я волк, но в душе я дракон, рррррр!',
               "Пинг 52к + баги == Ранга",
               "Моя любимая рыбка - карась",
               'Мошенница - Акудама SSS ранга, Награда: 100.000.000$',
               'Чем сильнее я становлюсь, тем сильнее мои враги...',
               'IT | Демон | 1.?.9',
            ]

async def voice_check(guild):
    server = servers.find_one({"server": guild.id})
    v = server['voice']
    if v == {}: return
    for i in list(v):
        try:
            try:
                chan = guild.get_channel(int(i))
            except Exception:
                v['private_voices'].pop(i)
                servers.update_one({'server': guild.id},{'$set': {'voice': v}})

            if chan == None:
                v['private_voices'].pop(i)
                servers.update_one({'server': guild.id},{'$set': {'voice': v}})

            elif len(chan.members) < 1:
                try:
                    await chan.delete()
                except Exception:
                    pass
                v['private_voices'].pop(i)
                servers.update_one({'server': guild.id},{'$set': {'voice': v}})
        except Exception:
            pass

def voice_time(guild, member, time, met):
    global voice_dict
    global servers
    server = servers.find_one({"server": guild.id})

    if met == 'add':
        try:
            voice_dict[str(guild.id)].update({ str(member.id) : time })
        except Exception:
            voice_dict.update({ str(guild.id) : { str(member.id) : time }})

    if met == 'delete':

        try:
            tt = time - voice_dict[str(guild.id)][str(member.id)]
            del voice_dict[str(guild.id)][str(member.id)]
            uss = funs.user_check(member, guild)
            funs.user_update(member.id, guild, 'voice_time', int(uss['voice_time'] + tt))


            expn = 5 * uss['voice_lvl'] * uss['voice_lvl'] + 50 * uss['voice_lvl'] + 100
            expi = int(tt)
            expi = uss['voice_xp'] + expi

            funs.user_update(member.id, guild, 'voice_xp', expi )

            if expn <= expi:
                funs.user_update(member.id, guild, 'voice_xp', 0 )
                funs.user_update(member.id, guild, 'voice_lvl', uss['voice_lvl'] + 1 )

                if server['voice_reward'] != {}:
                    if str(uss['voice_lvl'] + 1) in list(server['voice_reward'].keys()):

                        r = str(uss['voice_lvl'] + 1)
                        uss['money'] += server['voice_reward'][str(r)]['money']
                        for i in server['voice_reward'][str(r)]['items']:
                             uss['inv'].append(server['items'][str(i)])

                        funs.user_update(member.id, guild, 'money', uss['money'] )
                        funs.user_update(member.id, guild, 'inv', uss['inv'] )


        except Exception:
            pass



class MainCog(commands.Cog):
    def __init__(self, bot):
        global users
        global servers
        global clubs
        self.bot = bot


    @commands.Cog.listener()
    async def on_ready(self):
        global start_time

        channel = self.bot.get_channel(884486606399094876)
        ping = self.bot.latency
        ping_emoji = "🟩🔳🔳🔳🔳"

        ping_list = [
            {"ping": 0.100000000000000, "emoji": "🟧🟩🔳🔳🔳"},
            {"ping": 0.150000000000000, "emoji": "🟥🟧🟩🔳🔳"},
            {"ping": 0.200000000000000, "emoji": "🟥🟥🟧🟩🔳"},
            {"ping": 0.250000000000000, "emoji": "🟥🟥🟥🟧🟩"},
            {"ping": 0.300000000000000, "emoji": "🟥🟥🟥🟥🟧"},
            {"ping": 0.350000000000000, "emoji": "🟥🟥🟥🟥🟥"}]

        for ping_one in ping_list:
            if ping > ping_one["ping"]:
                ping_emoji = ping_one["emoji"]

        time2 = time.time()

        await channel.send(f"Бот {self.bot.user} онлайн - Команд: {len(self.bot.commands)}\n{ping_emoji} `{ping * 1000:.0f}ms`\nВремя на запуск: {funs.time_end(time2 - start_time)}")
        print(f"Бот {self.bot.user} онлайн - Команд: {len(self.bot.commands)}\n{ping_emoji} {ping * 1000:.0f}ms\nВремя на запуск: {funs.time_end(time2 - start_time)}")


        self.change_stats.start()
        self.manage_check.start()

    @tasks.loop(seconds = 3600)
    async def premium_check(self):
        global users
        uss = users.find({ "Nitro": True })
        for user in uss:
            try:
                uiv = user['global']['nitro']
                if uiv['time'] != 'infinity':
                    if uiv['time'] <= time.time():
                        users.update_one({"userid": idd}, {"$set":{"Nitro": False}})
                        if uiv['server'] != None:
                            servers.update_one({'server': guild.id},{'$set': {'premium': False}})
            except Exception:
                pass



    @tasks.loop(seconds = 15)
    async def change_stats(self):
        global stats
        await self.bot.change_presence( status = discord.Status.online, activity = discord.Game(name = random.choice(stat_list)))

    @tasks.loop(seconds=1)
    async def manage_check(self):
        if time.strftime('%S') == '00':

            m_t = time.time()
            guilds = servers.find({ "mute_members": { '$ne':{} } })
            for server in guilds:
                for member in server['mute_members']:
                    if int(time.time()) >= server['mute_members'][member]:
                        a = server['mute_members'].copy()
                        a.pop(member)
                        servers.update_one({'server':server['server']},{'$set': {'mute_members':a}})
                        try:
                            await self.bot.get_guild(server['server']).get_member(int(member)).remove_roles(self.bot.get_guild(server['server']).get_role(int(server['mod']['muterole'])))
                        except Exception:
                            pass

            m_t = int(time.time() - m_t)

            i_t = time.time()
            guilds = servers.find({ "roles_income": {"$exists": True} })
            for server in guilds:
                guild = self.bot.get_guild(server['server'])
                if guild != None:
                    for r_i in server['roles_income']:
                        r = server['roles_income'][r_i]
                        if int(time.time()) >= int(r['time']):
                            role = guild.get_role(int(r_i))
                            for member in role.members:
                                user = funs.user_check(member, guild)
                                if user != False:
                                    funs.user_update(member.id, guild, 'money', int(user['money'] + r['money']))

                            server['roles_income'][r_i].update({'time': time.time() + r['cooldown'] })
                            servers.update_one({'server':server['server']},{'$set': {'roles_income': server['roles_income'] }})

            i_t = int(time.time() - i_t)

            b_t = time.time()
            guilds = servers.find({ "banner_status": True })

            def trans_paste(fg_img,bg_img,alpha=10,box=(0,0)):
                fg_img_trans = Image.new("RGBA",fg_img.size)
                fg_img_trans = Image.blend(fg_img_trans,fg_img,alpha)
                bg_img.paste(fg_img_trans,box,fg_img_trans)
                return bg_img

            for g in guilds:
                serv = self.bot.get_guild(g['server'])
                if serv != None:
                    # await otl.send(f'Сервер {serv} найден')
                    try:
                        if serv.premium_subscription_count < 15:
                            servers.update_one({'server':g['server']},{'$set':{'banner_status': False}})
                        if serv.premium_subscription_count >= 15:
                            try:
                                offset = timezone(timedelta(hours=g['banner']['time']))
                                hour = int(str(datetime.now(offset)).split()[1][:-19])
                                ttime = str(datetime.now(offset)).split()[1][:-16]
                            except Exception:
                                offset = datetime.timezone(datetime.timedelta(hours=g['banner']['time']))
                                hour = int(str(datetime.datetime.now(offset)).split()[1][:-19])
                                ttime = str(datetime.datetime.now(offset)).split()[1][:-16]
                            # await otl.send(f'Сервер {serv} - достаточно бустов')


                            if g['banner']['met'] == 'time':
                                # await otl.send(f'Сервер {serv} - time')

                                #gps

                                if g['banner']['gps'] == 'center':
                                    xgps = -300
                                    ygps = -200

                                if g['banner']['gps'] == 'center-top':
                                    xgps = -300
                                    ygps = -400

                                if g['banner']['gps'] == 'center-bottom':
                                    xgps = -300
                                    ygps = 0

                                if g['banner']['gps'] == 'lower-left-corner':
                                    xgps = -600
                                    ygps = 0

                                if g['banner']['gps'] == 'upper-left-corner':
                                    xgps = -600
                                    ygps = -400

                                if g['banner']['gps'] == 'bottom-right-corner':
                                    xgps = 0
                                    ygps = 0

                                if g['banner']['gps'] == 'upper-right-corner':
                                    xgps = 0
                                    ygps = -400

                                # await otl.send(f'Сервер {serv} - gps установлен')

                                pl = Image.new('RGBA', (960, 540), (38, 32, 48))
                                response = requests.get(g['banner']['url'], stream = True)
                                response = Image.open(io.BytesIO(response.content))
                                response = response.convert("RGBA")
                                img = response.resize((960, 540), Image.ANTIALIAS) # улучшение качества
                                img.save(f'{serv.id}.png', format = "PNG")
                                img = Image.open(f'{serv.id}.png')
                                img = response.convert("RGBA")
                                try:
                                    os.remove(f'{serv.id}.png')
                                except Exception:
                                    pass
                                # await otl.send(f'Сервер {serv} - манипуляция с изображением')

                                idraw = ImageDraw.Draw(img)
                                headline = ImageFont.truetype("fonts/ChangaOne-Regular.ttf", size = 70)
                                idraw.text((690 + xgps, 430 + ygps), f"{ttime}", font = headline)
                                img = Image.composite(img, pl, img)
                                # await otl.send(f'Сервер {serv} - шрифт установлен')


                                if hour >= 0 and hour < 3 or hour >= 12 and hour < 15:
                                    text_image = Image.open(f"elements/time 12 {g['banner']['color']}.png")

                                if hour >= 3 and hour < 6 or hour >= 15 and hour < 18:
                                    text_image = Image.open(f"elements/time 3 {g['banner']['color']}.png")

                                if hour >= 6 and hour < 9 or hour >= 18 and hour < 21:
                                    text_image = Image.open(f"elements/time 6 {g['banner']['color']}.png")

                                if hour >= 9 and hour < 12 or hour >= 21 and hour < 23:
                                    text_image = Image.open(f"elements/time 9 {g['banner']['color']}.png")

                                img = trans_paste(text_image, img, 1.0, (xgps, ygps))

                                # await otl.send(f'Сервер {serv} - элемент найден')

                                try:
                                    img.save(f'banner {serv.id} id.png')
                                    with open(f'banner {serv.id} id.png', 'rb') as f:
                                        icon = f.read()
                                    await serv.edit(banner = icon)
                                    os.remove(f'banner {serv.id} id.png')
                                except Exception:
                                    pass

                                # await otl.send(f'Сервер {serv} - установлен')

                            if g['banner']['met'] == 'top-lvl':

                                #gps
                                if g['banner']['gps'] == 'center':
                                    xgps = -80
                                    ygps = -100

                                if g['banner']['gps'] == 'center-top':
                                    xgps = -80
                                    ygps = -230

                                if g['banner']['gps'] == 'center-bottom':
                                    xgps = -80
                                    ygps = 0

                                if g['banner']['gps'] == 'lower-left-corner':
                                    xgps = 100
                                    ygps = 0

                                if g['banner']['gps'] == 'upper-left-corner':
                                    xgps = -250
                                    ygps = 0

                                if g['banner']['gps'] == 'bottom-right-corner':
                                    xgps = 80
                                    ygps = 0

                                if g['banner']['gps'] == 'upper-right-corner':
                                    xgps = 80
                                    ygps = -230

                                top = list(sorted(g['users'].items(),key=lambda x: x[1]['lvl'],reverse=True))
                                top_user = list(top[0])
                                us = serv.get_member(int(top_user[0]))

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

                                pl = Image.new('RGBA', (960, 540), (38, 32, 48))
                                response = requests.get(g['banner']['url'], stream = True)
                                response = Image.open(io.BytesIO(response.content))
                                img = response.convert("RGBA")
                                img = response.resize((960, 540), Image.ANTIALIAS) # улучшение качества

                                img.save(f'{serv.id}.png', format = "PNG")
                                img = Image.open(f'{serv.id}.png')
                                img = response.convert("RGBA")
                                try:
                                    os.remove(f'{serv.id}.png')
                                except Exception:
                                    pass

                                text_image = Image.open(f"elements/top-lvl-element-{g['banner']['color']}.png")
                                img = trans_paste(text_image, img, 1.0, (xgps, ygps))

                                idraw = ImageDraw.Draw(img)
                                f2 = ImageFont.truetype("fonts/20421.ttf", size = 42)
                                f1 = ImageFont.truetype("fonts/BBCT.ttf", size = 32)

                                name = us.name
                                if len(name) <= 14:
                                    pass
                                else:
                                    n = len(name) - 14
                                    name = name[:-n] + "..."

                                idraw.text((420 + xgps, 380 + ygps), f"{name}", font = f2)
                                idraw.text((720 + xgps, 285 + ygps), f"{ttime}", font = f1)

                                im = img
                                try:
                                    url = str(us.avatar.url)
                                    response1 = requests.get(url, stream = True)
                                    response1 = Image.open(io.BytesIO(response1.content))

                                except Exception:
                                    byteImgIO = io.BytesIO()
                                    url = str(us.avatar.url)[:-9]
                                    response = requests.get(url, stream = True)
                                    response.raw.decode_content = True
                                    response1 = Image.open(response.raw)

                                response1 = response1.convert("RGBA")
                                response1 = response1.resize((50, 50), Image.ANTIALIAS)
                                size = (100, 100)

                                im = response1
                                im = crop(im, size)
                                im.putalpha(prepare_mask(size, 4))

                                bg_img = img
                                fg_img = im
                                img = trans_paste(fg_img, bg_img, 1.0, (300 + xgps, 350+ ygps, 400 + xgps, 450+ ygps))

                                try:
                                    img.save(f'banner {serv.id} id.png')
                                    with open(f'banner {serv.id} id.png', 'rb') as f:
                                        icon = f.read()
                                    await serv.edit(banner = icon)
                                    os.remove(f'banner {serv.id} id.png')
                                except Exception:
                                    pass

                            if g['banner']['met'] == 'stat' or g['banner']['met'] == 'stat-nb':

                                #gps
                                if g['banner']['gps'] == 'center':
                                    xgps = 0
                                    ygps = -100

                                if g['banner']['gps'] == 'center-top':
                                    xgps = 0
                                    ygps = -230

                                if g['banner']['gps'] == 'center-bottom':
                                    xgps = 0
                                    ygps = 0

                                if g['banner']['gps'] == 'lower-left-corner':
                                    xgps = -250
                                    ygps = 0

                                if g['banner']['gps'] == 'upper-left-corner':
                                    xgps = -250
                                    ygps = -230

                                if g['banner']['gps'] == 'bottom-right-corner':
                                    xgps = 250
                                    ygps = 0

                                if g['banner']['gps'] == 'upper-right-corner':
                                    xgps = 250
                                    ygps = -230

                                ms = 0
                                for i in serv.voice_channels:
                                    ms += len(i.members)

                                mm = serv.member_count

                                pl = Image.new('RGBA', (960, 540), (38, 32, 48))
                                response = requests.get(g['banner']['url'], stream = True)
                                response = Image.open(io.BytesIO(response.content))
                                img = response.convert("RGBA")
                                img = response.resize((960, 540), Image.ANTIALIAS) # улучшение качества

                                img.save(f'{serv.id}.png', format = "PNG")
                                img = Image.open(f'{serv.id}.png')
                                img = response.convert("RGBA")
                                try:
                                    os.remove(f'{serv.id}.png')
                                except Exception:
                                    pass
                                if g['banner']['met'] == 'stat':
                                    text_image = Image.open(f"elements/stat-element-{g['banner']['color']}.png")
                                else:
                                    text_image = Image.open(f"elements/stat-element-{g['banner']['color']}-no_b.png")
                                img = trans_paste(text_image, img, 1.0, (xgps, ygps))

                                idraw = ImageDraw.Draw(img)
                                f1 = ImageFont.truetype("fonts/BBCT.ttf", size = 40)


                                idraw.text((530 + xgps,285+ ygps), f"{mm}", font = f1)
                                idraw.text((480 + xgps,360+ ygps), f"{ttime}", font = f1)
                                idraw.text((500 + xgps,440+ ygps), f"{serv.premium_subscription_count}", font = f1)


                                try:
                                    img.save(f'banner {serv.id} id.png')
                                    with open(f'banner {serv.id} id.png', 'rb') as f:
                                        icon = f.read()
                                    await serv.edit(banner = icon)
                                    os.remove(f'banner {serv.id} id.png')
                                except Exception:
                                    pass

                            if g['banner']['met'] == 'voice-stat' or g['banner']['met'] == 'voice-stat-nb':

                                #gps
                                if g['banner']['gps'] == 'center':
                                    xgps = 20
                                    ygps = -100

                                if g['banner']['gps'] == 'center-top':
                                    xgps = 20
                                    ygps = -230

                                if g['banner']['gps'] == 'center-bottom':
                                    xgps = 20
                                    ygps = 0

                                if g['banner']['gps'] == 'lower-left-corner':
                                    xgps = -250
                                    ygps = 0

                                if g['banner']['gps'] == 'upper-left-corner':
                                    xgps = -250
                                    ygps = -230

                                if g['banner']['gps'] == 'bottom-right-corner':
                                    xgps = 270
                                    ygps = 0

                                if g['banner']['gps'] == 'upper-right-corner':
                                    xgps = 270
                                    ygps = -230

                                ms = 0
                                for i in serv.voice_channels:
                                    ms += len(i.members)

                                mm = serv.member_count

                                pl = Image.new('RGBA', (960, 540), (38, 32, 48))
                                response = requests.get(g['banner']['url'], stream = True)
                                response = Image.open(io.BytesIO(response.content))
                                img = response.convert("RGBA")
                                img = response.resize((960, 540), Image.ANTIALIAS) # улучшение качества

                                img.save(f'{serv.id}.png', format = "PNG")
                                img = Image.open(f'{serv.id}.png')
                                img = response.convert("RGBA")
                                try:
                                    os.remove(f'{serv.id}.png')
                                except Exception:
                                    pass

                                if g['banner']['met'] == 'voice-stat':
                                    text_image = Image.open(f"elements/voice-stat-element-{g['banner']['color']}.png")
                                else:
                                    text_image = Image.open(f"elements/voice-stat-element-{g['banner']['color']}-no_b.png")
                                img = trans_paste(text_image, img, 1.0, (xgps, ygps))

                                idraw = ImageDraw.Draw(img)
                                f1 = ImageFont.truetype("fonts/BBCT.ttf", size = 50)


                                idraw.text((400 + xgps,310+ ygps), f"{mm}", font = f1)
                                idraw.text((400 + xgps,410+ ygps), f"{ms}", font = f1)


                                try:
                                    img.save(f'banner {serv.id} id.png')
                                    with open(f'banner {serv.id} id.png', 'rb') as f:
                                        icon = f.read()
                                    await serv.edit(banner = icon)
                                    os.remove(f'banner {serv.id} id.png')
                                except Exception:
                                    pass

                            if g['banner']['met'] == 'common':

                                #gps
                                if g['banner']['gps'] == 'center':
                                    xgps = 0
                                    ygps = -200

                                if g['banner']['gps'] == 'center-top':
                                    xgps = 0
                                    ygps = -350

                                if g['banner']['gps'] == 'center-bottom':
                                    xgps = 0
                                    ygps = 0

                                if g['banner']['gps'] not in ['center', 'center-top', 'center-bottom']:
                                    xgps = 0
                                    ygps = 0

                                ms = 0
                                for i in serv.voice_channels:
                                    ms += len(i.members)

                                mm = serv.member_count

                                pl = Image.new('RGBA', (960, 540), (38, 32, 48))
                                response = requests.get(g['banner']['url'], stream = True)
                                response = Image.open(io.BytesIO(response.content))
                                img = response.convert("RGBA")
                                img = response.resize((960, 540), Image.ANTIALIAS) # улучшение качества

                                img.save(f'{serv.id}.png', format = "PNG")
                                img = Image.open(f'{serv.id}.png')
                                img = response.convert("RGBA")
                                try:
                                    os.remove(f'{serv.id}.png')
                                except Exception:
                                    pass

                                text_image = Image.open(f"elements/common-{g['banner']['color']}.png")
                                img = trans_paste(text_image, img, 1.0, (xgps, ygps))

                                idraw = ImageDraw.Draw(img)
                                f1 = ImageFont.truetype("fonts/BBCT.ttf", size = 60)

                                idraw.text((818 + xgps,450+ ygps), f"{ms}", font = f1)
                                idraw.text((430 + xgps,450+ ygps), f"{mm}", font = f1)
                                idraw.text((40 + xgps,450+ ygps), f"{ttime}", font = f1)


                                try:
                                    img.save(f'banner {serv.id} id.png')
                                    with open(f'banner {serv.id} id.png', 'rb') as f:
                                        icon = f.read()
                                    await serv.edit(banner = icon)
                                    os.remove(f'banner {serv.id} id.png')
                                except Exception:
                                    pass

                    except Exception:
                        pass

            b_t = int(time.time() - b_t)

            channel = await self.bot.fetch_channel(884499936476024913)
            emb = discord.Embed(description=f"Проверка мьютов: {funs.time_end(m_t)}\nПроверка ролей дохода: {funs.time_end(i_t)}\nУстановка баннера: {funs.time_end(b_t)}", color=0xE52B50)
            await channel.send(embed = emb)


    @commands.Cog.listener()
    async def on_member_join(self, member):

        server = servers.find_one({"server": member.guild.id})

        if server['send']['joinsend'] != 777777777777777777 or server['send']['joinsend'] != None:

            if server['send']['joinsend'] == 'dm':
                channel = member
            else:
                channel = self.bot.get_channel(server['send']['joinsend'])

            if channel != None:
                if server['send']['avatar_join_url'] != "avatar_url_none":

                    ust = server['send']

                    try:
                        ust['join_type']
                    except:
                        ust.update({'join_type': "png"})

                    url = server['send']['avatar_join_url']
                    user = users.find_one({"userid": member.id})

                    if ust['join_type'] == "png":

                        response = requests.get(url, stream = True)
                        response = Image.open(io.BytesIO(response.content))
                        response = response.convert("RGBA")
                        alpha = response.resize((960, 470), Image.ANTIALIAS) # улучшение качества

                    if ust['join_type'] == "gif":

                        response = requests.get(url, stream=True)
                        response.raw.decode_content = True
                        img = Image.open(response.raw)

                        alpha = Image.open('elements/alpha.png')
                        alpha = alpha.resize((960, 470), Image.ANTIALIAS) # улучшение качества


                    idraw = ImageDraw.Draw(alpha)
                    name = member.name
                    tag = member.discriminator


                    headline = ImageFont.truetype("fonts/20421.ttf", size = 50)
                    big = ImageFont.truetype("fonts/NotoSans-Bold.ttf", size = 100)

                    l = len(name)
                    if l < 11:
                        number = 11
                    if l >= 11:
                        number = 9

                    if server['send']['join_position_avatar'] == 0:

                        wp1 = 245          #x
                        wp2 = 275          #y

                        tp2 = 400
                        tp1 = int(400 - l * number) #текст

                        size = (250,250)        #y
                        ap1 = int(960 / 2 - size[0] / 2)         #x
                        ap2 = 30          #y

                    if server['send']['join_position_avatar'] == 1:

                        wp1 = 300          #x
                        wp2 = 170          #y

                        tp2 = 280 #y
                        tp1 = 305 #текст имени  x

                        size = (250,250)
                        ap1 = 20         #x
                        ap2 = 115          #y

                    if server['welcome']['wel_fill'] == None:
                        idraw.text((wp1, wp2), f"WELCOME", font = big)
                    else:
                        idraw.text((wp1, wp2), f"WELCOME", font = big, fill = f"{server['welcome']['wel_fill']}")

                    if server['welcome']['nam_fill'] == None:
                        idraw.text((tp1, tp2), f"{name}#{tag}", font = headline)
                    else:
                        idraw.text((tp1, tp2), f"{name}#{tag}", font = headline,fill = f"{server['welcome']['nam_fill']}")

                    url = str(member.avatar.url)

                    try:
                        response1 = requests.get(url, stream = True)
                        response1 = Image.open(io.BytesIO(response1.content))

                    except Exception:
                        byteImgIO = io.BytesIO()
                        response = requests.get(url, stream = True)
                        response.raw.decode_content = True
                        response1 = Image.open(response.raw)

                    response1 = response1.convert("RGB")
                    response1 = response1.resize((200, 200), Image.ANTIALIAS)

                    def trans_paste(fg_img,bg_img,alpha=10,box=(0,0)):
                        fg_img_trans = Image.new("RGBA",fg_img.size)
                        fg_img_trans = Image.blend(fg_img_trans,fg_img,alpha)
                        bg_img.paste(fg_img_trans,box,fg_img_trans)
                        return bg_img

                    def prepare_mask(size, antialias = 2):
                        mask = Image.new('L', (size[0] * antialias, size[1] * antialias), 0)
                        ImageDraw.Draw(mask).ellipse((0, 0) + mask.size, fill=255)
                        return mask.resize(size, Image.ANTIALIAS)

                    def crop(im, s):
                        w, h = im.size
                        k = w / s[0] - h / s[1]

                        if k > 0:
                            im = im.crop(((w - h) / 2, 0, (w + h) / 2, h))
                        elif k < 0:
                            im = im.crop((0, (h - w) / 2, w, (h + w) / 2))

                        return im.resize(s, Image.ANTIALIAS)

                    im = response1
                    im = crop(im, size)
                    im.putalpha(prepare_mask(size, 4))

                    def make_ellipse_mask(size, x0, y0, x1, y1, blur_radius):
                        img = Image.new("L", size, color=0)
                        draw = ImageDraw.Draw(img)
                        draw.ellipse((x0, y0, x1, y1), fill=255)
                        return img.filter(ImageFilter.GaussianBlur(radius=blur_radius))

                    overlay_image = alpha.filter(ImageFilter.GaussianBlur(radius=15))
                    if server['welcome']['el_fill'] == None:
                        mask_image = make_ellipse_mask((960, 470), ap1 - 10, ap2 - 10, ap1 + size[0] + 10, ap2 + size[1] + 10, 1)
                        alpha = Image.composite(overlay_image, alpha, mask_image)
                    else:
                        idraw.ellipse((ap1 - 10, ap2 - 10, ap1 + size[0] + 10, ap2 + size[1] + 10), fill = f"{server['welcome']['el_fill']}")

                    #аватарка
                    bg_img = alpha
                    fg_img = im
                    p = trans_paste(fg_img, bg_img, 1.0, (ap1, ap2, ap1 + size[0], ap2 + size[0]))

                    if server['welcome']['wel_text'] == None:
                        text = f"Welcome {name}#{tag} to {member.guild.name}"
                    else:
                        text = server['welcome']['wel_text']
                        text = funs.text_replase(text, member)

                    if ust['join_type'] == "png":


                        image = alpha
                        output = BytesIO()
                        image.save(output, 'png')
                        image_pix=BytesIO(output.getvalue())

                        file = discord.File(fp = image_pix, filename="welcome_card.png")
                        ul = 'png'

                    if ust['join_type'] == "gif":
                        fs = []
                        for frame in ImageSequence.Iterator(img):
                            frame = frame.convert("RGBA")

                            frame = frame.resize((960, 470), Image.ANTIALIAS)

                            bg_img = frame
                            fg_img = alpha
                            img = trans_paste(fg_img, bg_img, 1.0)

                            b = io.BytesIO()
                            frame.save(b, format="GIF",optimize=True, quality=75)
                            frame = Image.open(b)
                            fs.append(frame)


                        fs[0].save('welcome_card.gif', save_all=True, append_images=fs[1:], loop = 0, optimize=True, quality=75)

                        file = discord.File(fp = "welcome_card.gif", filename="welcome_card.gif")
                        ul = 'gif'


                    try:
                        if server['welcome']['emb'] == False:
                            await channel.send(f"{text}", file = file)

                        if server['welcome']['emb'] == True:
                            emb = discord.Embed(description = text, color= server['embed_color'])
                            emb.set_image(url=f"attachment://welcome_card.{ul}")
                            await channel.send(file=file, embed = emb)

                    except Exception:
                        pass

                    try:
                        os.remove(f'welcome_card.{ul}')
                    except Exception:
                        pass

        try:
            if server['nick_change'] != None:

                if funs.user_check(member, member.guild, 'dcheck', 'save_users') == False:
                    ret = False

                if funs.user_check(member, member.guild, 'dcheck', 'save_users') == True:
                    l_user = funs.user_check(member, member.guild)

                    try:
                        l_user['name']
                        ret = True
                    except Exception:
                        ret = False

                if ret == False:
                    name = funs.text_replase(server['nick_change'], member)
                    try:
                        await member.edit(nick = name)# изменение никнейма при насройке изменения
                    except Exception:
                        pass
        except Exception:
            pass

        if funs.user_check(member, member.guild, 'dcheck', 'save_users') == True:
            l_user = funs.user_check(member, member.guild)
            s_user = funs.user_check(member, member.guild, None, 'save_users')

            if server['save']['name_save'] == True:
                try:
                    await member.edit(nick = s_user['name'])# изменение никнейма при сохранении
                    funs.user_update(member.id, member.guild, 'name', '-', 'pop', 'save_users')
                except Exception:
                    pass

            if server['save']['roles_save'] == True:
                try:
                    if s_user['roles'] != []:
                        for id in s_user['roles']:
                            try:
                                role = member.guild.get_role(int(id))
                                await member.add_roles(role)
                            except Exception:
                                pass
                        funs.user_update(member.id, member.guild, 'roles', '-', 'pop', 'save_users')
                except Exception:
                    pass

        try:
            if server['join_roles'] != []:
                for id in server['join_roles']:
                    try:
                        role = member.guild.get_role(int(id))
                        await member.add_roles(role)
                    except Exception:
                        pass
        except Exception:
            pass

        #лог
        if server['mod']['log_channel'] != {}:
            if 'member_join' in server['mod']['log_channel']['logging'] or 'all' in server['mod']['log_channel']['logging'] or 'member' in server['mod']['log_channel']['logging']:

                channel = await self.bot.fetch_channel(server['mod']['log_channel']['channel'])

                one_day_ago = datetime.now() - timedelta(days=1)
                if member.created_at > one_day_ago: #меньше одного дня
                    emb = discord.Embed(description="Пользователь присоединился к серверу", color=0xE52B50)
                    emb.add_field(name="Оповещение",value=f"Аккаунт создан меньше одного дня назад!", inline=False)
                else: #больше одного дня
                    emb = discord.Embed(description="Пользователь присоединился к серверу", color=0x76E212)

                if member.nick == None:
                    nick = f"Имя: {member.name}#{member.discriminator}\nУпоминание: {member.mention}"
                else:
                    nick = f"Имя: {member.name}#{member.discriminator}\nНикнейм: {member.nick}\nУпоминание: {member.mention}"

                emb.add_field(name="Информация",value=f"Аккаунт создан: {member.created_at.strftime('%X, %d %B, %Y')}\n{nick}", inline=False)
                emb.set_thumbnail(url= member.avatar.url)
                emb.set_footer(text=f"ID: {member.id}")
                await channel.send(embed=emb)


    @commands.Cog.listener()
    async def on_member_remove(self, member):
        server = servers.find_one({"server": member.guild.id})

        if server['send']['leavensend'] != 777777777777777777 or server['send']['leavensend'] != None:

            channel = self.bot.get_channel(server['send']['leavensend'])

            if channel != None:
                if server['send']['avatar_leave_url'] != "avatar_url_none":

                    ust = server['send']
                    try:
                        ust['leave_type']
                    except:
                        ust.update({'leave_type': "png"})

                    url = server['send']['avatar_leave_url']
                    user = users.find_one({"userid": member.id})

                    if ust['leave_type'] == "png":

                        response = requests.get(url, stream = True)
                        response = Image.open(io.BytesIO(response.content))
                        response = response.convert("RGBA")
                        alpha = response.resize((960, 470), Image.ANTIALIAS) # улучшение качества

                    if ust['leave_type'] == "gif":

                        response = requests.get(url, stream=True)
                        response.raw.decode_content = True
                        img = Image.open(response.raw)

                        alpha = Image.open('elements/alpha.png')
                        alpha = alpha.resize((960, 470), Image.ANTIALIAS) # улучшение качества


                    idraw = ImageDraw.Draw(alpha)
                    name = member.name
                    tag = member.discriminator


                    headline = ImageFont.truetype("fonts/20421.ttf", size = 50)
                    big = ImageFont.truetype("fonts/NotoSans-Bold.ttf", size = 100)

                    l = len(name)
                    if l < 11:
                        number = 11
                    if l >= 11:
                        number = 9

                    if server['send']['leave_position_avatar'] == 0:

                        wp1 = 245          #x
                        wp2 = 275          #y

                        tp2 = 400
                        tp1 = int(400 - l * number) #текст

                        size = (250,250)        #y
                        ap1 = int(960 / 2 - size[0] / 2)         #x
                        ap2 = 30          #y

                    if server['send']['leave_position_avatar'] == 1:

                        wp1 = 300          #x
                        wp2 = 170          #y

                        tp2 = 280 #y
                        tp1 = 305 #текст имени  x

                        size = (250,250)
                        ap1 = 20         #x
                        ap2 = 115          #y

                    if server['goodbye']['wel_fill_l'] == None:
                        idraw.text((wp1, wp2), f"GOODBYE", font = big)
                    else:
                        idraw.text((wp1, wp2), f"GOODBYE", font = big, fill = f"{server['goodbye']['wel_fill_l']}")

                    if server['goodbye']['nam_fill_l'] == None:
                        idraw.text((tp1, tp2), f"{name}#{tag}", font = headline)
                    else:
                        idraw.text((tp1, tp2), f"{name}#{tag}", font = headline,fill = f"{server['goodbye']['nam_fill_l']}")

                    url = str(member.avatar.url)

                    try:
                        response1 = requests.get(url, stream = True)
                        response1 = Image.open(io.BytesIO(response1.content))

                    except Exception:
                        byteImgIO = io.BytesIO()
                        response = requests.get(url, stream = True)
                        response.raw.decode_content = True
                        response1 = Image.open(response.raw)

                    response1 = response1.convert("RGB")
                    response1 = response1.resize((200, 200), Image.ANTIALIAS)

                    def trans_paste(fg_img,bg_img,alpha=10,box=(0,0)):
                        fg_img_trans = Image.new("RGBA",fg_img.size)
                        fg_img_trans = Image.blend(fg_img_trans,fg_img,alpha)
                        bg_img.paste(fg_img_trans,box,fg_img_trans)
                        return bg_img

                    def prepare_mask(size, antialias = 2):
                        mask = Image.new('L', (size[0] * antialias, size[1] * antialias), 0)
                        ImageDraw.Draw(mask).ellipse((0, 0) + mask.size, fill=255)
                        return mask.resize(size, Image.ANTIALIAS)

                    def crop(im, s):
                        w, h = im.size
                        k = w / s[0] - h / s[1]

                        if k > 0:
                            im = im.crop(((w - h) / 2, 0, (w + h) / 2, h))
                        elif k < 0:
                            im = im.crop((0, (h - w) / 2, w, (h + w) / 2))

                        return im.resize(s, Image.ANTIALIAS)

                    im = response1
                    im = crop(im, size)
                    im.putalpha(prepare_mask(size, 4))

                    def make_ellipse_mask(size, x0, y0, x1, y1, blur_radius):
                        img = Image.new("L", size, color=0)
                        draw = ImageDraw.Draw(img)
                        draw.ellipse((x0, y0, x1, y1), fill=255)
                        return img.filter(ImageFilter.GaussianBlur(radius=blur_radius))

                    overlay_image = alpha.filter(ImageFilter.GaussianBlur(radius=15))
                    if server['goodbye']['el_fill_l'] == None:
                        mask_image = make_ellipse_mask((960, 470), ap1 - 10, ap2 - 10, ap1 + size[0] + 10, ap2 + size[1] + 10, 1)
                        alpha = Image.composite(overlay_image, alpha, mask_image)
                    else:
                        idraw.ellipse((ap1 - 10, ap2 - 10, ap1 + size[0] + 10, ap2 + size[1] + 10), fill = f"{server['goodbye']['el_fill_l']}")

                    #аватарка
                    bg_img = alpha
                    fg_img = im
                    p = trans_paste(fg_img, bg_img, 1.0, (ap1, ap2, ap1 + size[0], ap2 + size[0]))

                    if server['goodbye']['lea_text'] == None:
                        text = f"Goodbye {name}#{tag} to {member.guild.name}"
                    else:
                        text = server['goodbye']['lea_text']
                        text = funs.text_replase(text, member)

                    if ust['leave_type'] == "png":

                        image = alpha
                        output = BytesIO()
                        image.save(output, 'png')
                        image_pix=BytesIO(output.getvalue())

                        file = discord.File(fp = image_pix, filename="goodbye_card.png")
                        ul = 'png'

                    if ust['leave_type'] == "gif":
                        fs = []
                        for frame in ImageSequence.Iterator(img):
                            frame = frame.convert("RGBA")

                            frame = frame.resize((960, 470), Image.ANTIALIAS)

                            bg_img = frame
                            fg_img = alpha
                            img = trans_paste(fg_img, bg_img, 1.0)

                            b = io.BytesIO()
                            frame.save(b, format="GIF",optimize=True, quality=75)
                            frame = Image.open(b)
                            fs.append(frame)


                        fs[0].save('goodbye_card.gif', save_all=True, append_images=fs[1:], loop = 0, optimize=True, quality=75)

                        file = discord.File(fp = "goodbye_card.gif", filename="goodbye_card.gif")
                        ul = 'gif'


                    try:
                        if server['goodbye']['emb'] == False:
                            await channel.send(f"{text}", file = file)

                        if server['goodbye']['emb'] == True:
                            emb = discord.Embed(description = text, color= server['embed_color'])
                            emb.set_image(url=f"attachment://goodbye_card.{ul}")
                            await channel.send(file=file, embed = emb)

                    except Exception:
                        pass

                    try:
                        os.remove(f'goodbye_card.{ul}')
                    except Exception:
                        pass

        if server['save']['roles_save'] == True or server['save']['name_save'] == True:
            server['save_users'].update({ str(member.id): {} })
            servers.update_one({'server':member.guild.id},{'$set':{'save_users': server['save_users'] }})

        if funs.user_check(member, member.guild, 'dcheck') == True:
            if server['save']['date_save'] == False:

                server['users'].pop(str(member.id))
                servers.update_one({'server':member.guild.id},{'$set':{'users': server['users'] }})

        if server['save']['name_save'] == True:
            if member.nick == None:
                funs.user_update(member.id, member.guild, 'name', member.name, 'update', 'save_users')
            else:
                funs.user_update(member.id, member.guild, 'name', member.nick, 'update', 'save_users')

        if server['save']['roles_save'] == True:
            roles_list_ids = []

            for i in member.roles:
                if i != member.guild.default_role:
                    roles_list_ids.append(i.id)

            if roles_list_ids != []:
                funs.user_update(member.id, member.guild, 'roles', roles_list_ids, 'update', 'save_users')

        #лог
        if server['mod']['log_channel'] != {}:
            if 'member_remove' in server['mod']['log_channel']['logging'] or 'all' in server['mod']['log_channel']['logging'] or 'member' in server['mod']['log_channel']['logging']:

                channel = await self.bot.fetch_channel(server['mod']['log_channel']['channel'])
                emb = discord.Embed(description= f"Пользователь {member.name}#{member.discriminator} покинул сервер", color=0xFFDB8B)
                emb.set_thumbnail(url= member.avatar.url)
                emb.set_footer(text=f"ID: {member.id}")
                await channel.send(embed=emb)



    @commands.Cog.listener()
    async def on_guild_join(self,guild):
        funs.insert_server(guild)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        servers.delete_one({"server": guild.id})

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        normal = False
        channel = self.bot.get_channel(884486925933764649)

        if isinstance(error, commands.CommandNotFound):
            pass

        if isinstance(error, commands.CommandOnCooldown):
            seconds = error.retry_after
            time_end = funs.time_end(seconds)
            e = discord.Embed(color=0xf03e65)
            e.add_field(name = 'Перезарядка:', value = f'Попробуйте через {time_end}')
            e.set_thumbnail(url = "https://cdn.discordapp.com/attachments/707663547928412250/735467950563393617/632693649767137280.gif" )
            await ctx.send(embed = e)
            normal = True

        if isinstance(error, commands.MissingRequiredArgument):
            com = ctx.command
            emb = discord.Embed(description = f"Правильное использование: **{ctx.prefix}{com.name}** `{com.usage}`\n Аргумент `{error.param.name}` не указан!" ,color= 15744613 ).set_footer(text = '() - обязательный аргумент, [] - необязательный аргумент')
            await ctx.send(embed = emb)
            normal = True

        elif str(error)=="Command raised an exception: TypeError: 'NoneType' object is not subscriptable":
            await ctx.send(f"Объект не найден!")
            normal = True

        elif str(error)=="Command raised an exception: NotFound: 404 Not Found (error code: 10008): Unknown Message":
            await ctx.send("Сообщение не найдено!")
            normal = True


        elif str(error)=="Command raised an exception: Forbidden: 403 Forbidden (error code: 50013): Missing Permissions":
            try:
                await ctx.send("У бота не достаточно прав!")
            except Exception:
                pass
            normal = True


        elif str(error)=="Command raised an exception: AttributeError: 'NoneType' object has no attribute 'id'":
            await ctx.send("'Ничего' не может иметь 'id'")
            normal = False


        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("У вас недостаточно прав!")
            normal = True


        elif isinstance(error, commands.BadArgument):
            com = ctx.command
            emb = discord.Embed(description = f"Правильное использование: **{ctx.prefix}{com.name}** `{com.usage}`" ,color= 15744613 ).set_footer(text = '() - обязательный аргумент, [] - необязательный аргумент')
            await ctx.send(embed = emb)
            normal = True

        else:
            print(error)
            await channel.send(f"Ошибка: `{error}`")

        try:
            ctx.command = self.bot.get_command(ctx.invoked_with.lower())
            await channel.send(f"Команда: {ctx.command.name}\nСервер: {ctx.guild.id}\nПользователь: {ctx.author.id}\n Ошибка: `{error}` ")

        except Exception:
            await channel.send(f"Ошибка: `{error}`")
        if normal == False:
            await channel.send(f"🎈")



    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        global voice_dict

        rr = ['🎍', '🎋', '💫', '🌪', ' 🔥', '🌟', '⚡️', '☄️', '💥', '🌚', '🌞', '🍬', '🍭', '🍡', '🌷', '🐾', '🍹', '🍸', '🍱', '🎆', '🎭', '💎', '🎨']
        server = servers.find_one({"server": member.guild.id})
        serv = server['server']
        if server['voice']["voice_category"] != None:
            mainCategory = member.guild.get_channel(server['voice']["voice_category"])

            if after.channel != None and before.channel != None and after.channel.id == server['voice']["voice_channel"] and str(before.channel.id) in list(server['voice']['private_voices'].keys()):
                await member.move_to(before.channel)

            else:
                await voice_check(member.guild)

                if before.channel != None and str(before.channel.id) in list(server['voice']['private_voices'].keys()) and after.channel != None or after.channel != None and after.channel.id == server['voice']["voice_channel"] and before.channel != None or after.channel == None:
                    try:
                        cc = server['voice']['private_voices'][f'{before.channel.id}']
                        if len(before.channel.members) < 1:
                            await before.channel.delete()
                            v = server['voice']
                            v['private_voices'].pop(f'{before.channel.id}')
                            servers.update_one({'server': server['server']},{'$set': {'voice': v}})
                    except Exception:
                        pass

                if after.channel != None and after.channel.id == server['voice']["voice_channel"]:
                    voice = server['voice']
                    r = random.choice(rr)
                    try:
                        channel2 = await after.channel.guild.create_voice_channel(name=f"{r} {member.display_name}",category=mainCategory)
                        voice['private_voices'].update({f"{channel2.id}": member.id})

                        servers.update_one({'server': server['server']},{'$set': {'voice': voice}})
                        await member.move_to(channel2)
                        await channel2.set_permissions(member, manage_channels=True, mute_members=True, deafen_members=True, manage_permissions=True)
                    except Exception:
                        pass


        if before.channel is None and after.channel is not None:
            t1 = time.time()
            voice_time(after.channel.guild, member, t1, 'add')

        if before.channel is not None and after.channel is None:
            t2 = time.time()
            voice_time(before.channel.guild, member, t2, 'delete')

        if server['voice']["randomc_channel"] != None and after.channel != None and after.channel.id == server['voice']["randomc_channel"]:
            serv = after.channel.guild

            def ch(channels, server):
                ch = []
                for i in channels:
                    if type(i) == discord.channel.VoiceChannel:
                        if server['voice']['rc_bl_channels'] == None or i not in server['voice']['rc_bl_channels']:
                            if i.id != server['voice']["randomc_channel"]:
                                if i.user_limit > len(i.members) or i.user_limit == 0:
                                    ch.append(i)
                return ch

            if len(ch(serv.channels, server)) != 0:
                channels = []
                for i in ch(serv.channels, server):
                    if len(i.members) != 0:
                        channels.append(i)

                if len(channels) > 0:
                    channel = random.choice(channels)
                    await member.move_to(channel)
                else:

                    channel = random.choice(ch(serv.channels, server))
                    await member.move_to(channel)


        if server['mod']['log_channel'] != {}:
            counter = 0
            log = server['mod']['log_channel']['logging']
            channel = await self.bot.fetch_channel(server['mod']['log_channel']['channel'])
            emb = discord.Embed(title = f'Обновление статуса войс-канала', color=0xFFDB8B )

            if 'voice_connect' in log or 'all' in log or 'voice' in log:
                if before.channel == None and after.channel != None:
                    emb.add_field(name = ' | Пользователь присоединился', value = f'Пользователь {member.mention} подключился к каналу {after.channel.mention}', inline = True)
                    counter += 1

            if 'voice_disconnect' in log or 'all' in log or 'voice' in log:
                if before.channel != None and after.channel == None:
                    emb.add_field(name = ' | Пользователь отключился', value = f'Пользователь {member.mention} отключился из {before.channel.mention}', inline = True)
                    counter += 1

            if 'voice_reconnect' in log or 'all' in log or 'voice' in log:
                if before.channel != None and after.channel != None:
                    emb.add_field(name = ' | Пользователь переподключился', value = f'Пользователь {member.mention} переподключился из {before.channel.mention} в {after.channel.mention}', inline = True)
                    counter += 1

            if counter != 0:
                await channel.send(embed = emb)



    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):


        async def rr(l, func, message, payload, num):
            roles = []
            server = servers.find_one({"server":payload.guild_id})

            try:
                for i in l[1]:
                    roles.append(message.guild.get_role(i))
                if func == 'add':
                    await payload.member.add_roles(*roles, reason="Добавление роли за реакцию.")
                elif func == 'remove':
                    await payload.member.remove_roles(*roles, reason="Удаление роли за реакцию.")
                elif func == 'verify':
                    await payload.member.add_roles(*roles, reason="Добавление роли за верификацию.")
                    await message.remove_reaction(payload.emoji.name, payload.member)
                elif func == 'limit':
                    if len(l[3]) >= l[2]:
                        await message.remove_reaction(payload.emoji.name, payload.member)
                        return
                    else:
                        rrs = server['rr'].copy()
                        list = rrs[str(payload.message_id)]['emojis'][num][3]
                        list.append(payload.member.id)
                        servers.update_one({'server': payload.guild_id },{'$set': {'rr':rrs}})

                    if server['rr'][str(payload.message_id)]['limit_func'] == 'add':
                        await payload.member.add_roles(*roles, reason="Добавление роли за реакцию.")
                    if server['rr'][str(payload.message_id)]['limit_func'] == 'remove':
                        await payload.member.remove_roles(*roles, reason="Удаление роли за реакцию.")

            except Exception:
                pass

        # try:
        if 1 == 1:
            guild = self.bot.get_guild(payload.guild_id)
            channel = guild.get_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)
            server = servers.find_one({"server":payload.guild_id})
            emoji = payload.emoji
            member = payload.member

            try:
                mm = server['rr'][str(message.id)]
                mr = True
            except Exception:
                mr = False

            if mr == True:
                num = 0
                for i in server['rr'][str(message.id)]['emojis']:
                    l = i
                    if emoji.name in i or emoji.id in i:
                        try:
                            roles = []
                            for i in server['rr'][str(message.id)]['allow roles']:
                                roles.append(message.guild.get_role(i))
                            if list(set(roles) & set(payload.member.roles)) != []:
                                await rr(l, server['rr'][str(message.id)]["func"], message, payload, num)
                            else:
                                await message.remove_reaction(emoji, payload.member)
                                return

                        except Exception:
                            await rr(l, server['rr'][str(message.id)]["func"], message, payload, num)
                        num += 1

            if mr == False:
                if server['tickets'] != {}:
                    if payload.member.bot != True:
                        if message.id == server['tickets']['t_message']:
                            if str(emoji) == '💬':
                                ml = []
                                for nn in list(server['tickets']['tick'].items()):
                                    ml.append(nn[1]['member'])
                                if member.id in ml:
                                    await message.remove_reaction('💬', member)
                                else:
                                    await message.remove_reaction('💬', member)
                                    emb = discord.Embed(title = f'Управление', description = f'Если вы хотите закрыть билет, нажмите ✅', color= server['embed_color'] )
                                    category = await self.bot.fetch_channel(server['tickets']['category'])
                                    overwrites = {
                                                guild.default_role: discord.PermissionOverwrite(view_channel=False),
                                                guild.me: discord.PermissionOverwrite(read_messages=True, manage_messages=True),
                                                payload.member: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                                                }
                                    channel = await guild.create_text_channel(name=f"ticket {server['tickets']['t_n']+1}", category = category,  overwrites=overwrites, reason = "ticket create")
                                    msg = await channel.send(f'{member.mention}',embed = emb)
                                    await msg.add_reaction("✅")
                                    server['tickets']['t_n'] = server['tickets']['t_n']+1
                                    server['tickets']['tick'].update({ str(msg.id): {'member': member.id, 'status': 'open'} })
                                    servers.update_one({'server': guild.id},{"$set": {'tickets': server['tickets'] }})

                        else:
                            # try:
                            if 1 == 1:
                                try:
                                    m = server['tickets']['tick'][str(message.id)]
                                except:
                                    m = None

                                if m != None:
                                    if m['status'] == 'open':
                                        ms = m['member']
                                        if str(emoji) == '✅':
                                            if member.id == ms or funs.roles_check(member, guild.id) == True:
                                                bm = guild.get_member(ms)
                                                await message.delete()

                                                overwrites = {
                                                            guild.default_role: discord.PermissionOverwrite(view_channel=False),
                                                            bm: discord.PermissionOverwrite(read_messages=False, send_messages = False),
                                                            guild.me: discord.PermissionOverwrite(read_messages=True, manage_messages=True)
                                                            }

                                                await message.channel.edit(overwrites = overwrites)

                                                emb = discord.Embed(title = f'Тикет закрыт', description = f'Тикет пользователя {bm.mention} был закрыт\n\nУдалить канал > 🧨\nСохранить историю > 📜', color= server['embed_color'] )
                                                msg = await message.channel.send(embed = emb)

                                                server['tickets']['tick'].update({ str(msg.id): {'status': 'close', 'member': bm.id} })

                                                del server['tickets']['tick'][str(message.id)]
                                                servers.update_one({'server': guild.id},{"$set": {'tickets': server['tickets'] }})

                                                await msg.add_reaction("🧨")
                                                await msg.add_reaction("📜")


                                    if m['status'] == 'close':
                                        if str(emoji) == '🧨':
                                            await message.channel.delete(reason = 'ticket remove')

                                        elif str(emoji) == '📜':
                                            await message.delete()

                                        del server['tickets']['tick'][str(message.id)]
                                        servers.update_one({'server': guild.id},{"$set": {'tickets': server['tickets'] }})


                            # except Exception:
                            #     pass



                if server['pizza_board'] != {}:
                    if payload.member.bot != True:
                        if message.author.bot != True:
                            if str(emoji) == '🍕':

                                r_l = 0
                                for i in message.reactions:
                                    if str(i) == '🍕':
                                        break
                                    else:
                                        r_l += 1

                                if server['pizza_board']['count'] <= message.reactions[r_l].count:
                                    pizz_channel = await self.bot.fetch_channel(server['pizza_board']['channel'])
                                    try:
                                        pzz_mes =  await pizz_channel.fetch_message(server['pizza_board']['messages'][str(message.id)]['m_id'])

                                        emb = discord.Embed(title = f'Сообщение достойное пиццы!', description = f'{ message.content}', color=0xFF8B1F )

                                        try:
                                            emb.set_image(url = message.attachments[0].proxy.url)
                                        except Exception:
                                            pass

                                        emb.set_author(name = payload.member.name, icon_url = payload.member.avatar.url)
                                        emb.add_field(name = 'Ссылка', value = f'[Прыг!]({message.jump.url})')

                                        await pzz_mes.edit(content = f"<:n_pizza:871093811626000414> {message.reactions[r_l].count} ➜ {message.channel.mention}", embed = emb)

                                    except KeyError:
                                        emb = discord.Embed(title = f'Сообщение достойное пиццы!', description = f'{ message.content}', color=0xFF8B1F )

                                        try:
                                            emb.set_image(url = message.attachments[0].proxy.url)
                                        except Exception:
                                            pass

                                        emb.set_author(name = payload.member.name, icon_url = payload.member.avatar.url)
                                        emb.add_field(name = 'Ссылка', value = f'[Прыг!]({message.jump.url})')

                                        pzz_mes = await pizz_channel.send(f"<:n_pizza:871093811626000414> {message.reactions[r_l].count} ➜ {message.channel.mention}", embed = emb)
                                        server['pizza_board']['messages'].update({str(message.id): {'m_id': pzz_mes.id}})
                                        servers.update_one({"server": payload.guild_id}, {"$set": {"pizza_board": server['pizza_board']}})

        # except Exception:
        #     pass

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):

        async def rr(l, func, message, payload, num):
            guild = self.bot.get_guild(payload.guild_id)
            member = guild.get_member(payload.user_id)
            roles = []
            try:

                for i in l[1]:
                    roles.append(message.guild.get_role(i))
                if func == 'add':
                    await member.remove_roles(*roles, reason="Удаление роли за снятие реакции.")
                elif func == 'remove':
                    await member.add_roles(*roles, reason="Добавление роли за снятие реакции.")
                elif func == 'limit':
                    if len(l[3]) > l[2]:
                        return
                    else:
                        try:
                            rrs = server['rr'].copy()
                            list = rrs[str(payload.message_id)]['emojis'][num][3]
                            list.remove(member.id)
                            servers.update_one({'server': payload.guild_id },{'$set': {'rr':rrs}})
                        except Exception:
                            pass

                    if server['rr'][str(payload.message_id)]['limit_func'] == 'remove':
                        await member.add_roles(*roles, reason="Добавление роли за удаление реакцию.")
                    if server['rr'][str(payload.message_id)]['limit_func'] == 'add':
                        await member.remove_roles(*roles, reason="Удаление роли за снятие реакции.")

            except Exception:
                return

        channel = await self.bot.fetch_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        server = servers.find_one({"server":payload.guild_id})

        try:
            mm = server['rr'][str(message.id)]
        except Exception:
            return

        emoji = payload.emoji
        server = servers.find_one({"server": payload.guild_id})

        num = 0
        for i in server['rr'][str(message.id)]['emojis']:
            l = i
            if emoji.name in i or emoji.id in i:
                await rr(l, server['rr'][str(message.id)]["func"], message, payload, num)
            num = 0


    @commands.Cog.listener()
    async def on_member_update(self, before, after):

        async def on_nitro_boost(booster):
            server = servers.find_one({"server": booster.guild.id})
            if server["boost"]["send"] == None:
                return

            channel = await self.bot.fetch_channel(server["boost"]["send"])

            if server['boost']['description'] != None:
                text = funs.text_replase(server['boost']['description'], booster)
            else:
                text = f"Огромное спасибо {booster.mention}, что помог серверу!"

            emb = discord.Embed(title = 'Бустит сервер!', description =f"{text}", color=server['embed_color'] )
            emb.set_author(icon_url = 'https://images-ext-1.discordapp.net/external/t8PQC99J_sKLcmwB6EVhtlmiIq8iG47SHE_gDJcQeOU/https/i.imgur.com/GdS5i6t.gif', name = booster)
            emb.set_thumbnail(url= booster.avatar.url)
            if server["boost"]["url"] != None:
                emb.set_image(url = server["boost"]["url"])
            if server["boost"]["footer"] != None:
                emb.set_footer(text = funs.text_replase(server['boost']['footer'], booster))

            await channel.send(embed = emb)

            if server['boost']['reward'] != []:
                user = funs.user_check(booster, booster.guild)
                for i in server['boost']['reward']:
                    user['inv'].append(server['items'][str(i)])
                funs.user_update(member.id, guild, 'inv', user['inv'])


        if after.premium_since != None and before.premium_since != after.premium_since and before.premium_since != None:
            await on_nitro_boost(before)

        #log
        try:
            server = servers.find_one({"server": after.guild.id})

            if server['mod']['log_channel'] != {}:
                counter = 0
                log = server['mod']['log_channel']['logging']
                channel = await self.bot.fetch_channel(server['mod']['log_channel']['channel'])
                emb = discord.Embed(title = f'Обновление пользователя', description = f'Пользователь {before.mention} был обновлён', color=0xE28112 )

                if 'member_status' in log or 'all' in log or 'member' in log:
                    if before.status != after.status:

                        emb.add_field(name = ' | Пользователь обновил статус', value = f'Изначальный статус: `{ before.status}`\nСейчас статус: `{after.status }`', inline = True)
                        counter += 1

                if 'member_nick' in log or 'all' in log or 'member' in log:
                    if before.nick != after.nick:

                        emb.add_field(name = ' | Обновление никнейма пользователя', value = f'Изначальный ник: `{ before.nick}`\nСейчас ник: `{after.nick}`', inline = True)
                        counter += 1

                if 'member_roles' in log or 'all' in log or 'member' in log:
                    if before.roles != after.roles:

                        drf = list( (set(after.roles) | set(before.roles)) - (set(after.roles) & set(before.roles)) )
                        ddr = [] #удалённые роли
                        adr = [] #добавленые роли

                        for i in drf:
                            if i in before.roles and i not in after.roles:
                                ddr.append(i)
                            if i in after.roles and i not in before.roles:
                                adr.append(i)

                        if ddr != []:
                            text = ''
                            for i in ddr:
                                text += f'{i.mention} '

                            emb.add_field(name = ' | Удалённые роли у пользователя', value = text, inline = True)
                            counter += 1

                        if adr != []:
                            text = ''
                            for i in adr:
                                text += f'{i.mention} '

                            emb.add_field(name = ' | Добавленные роли у пользователя', value = text, inline = True)
                            counter += 1

                if 'member_top_role' in log or 'all' in log or 'member' in log:
                    if before.top_role != after.top_role:

                        emb.add_field(name = ' | Высшая роль пользователя изменилась', value = f'Изначальный роль: `{ before.top_role}`\nСейчас роль: `{after.top_role}`', inline = True)
                        counter += 1


                if counter != 0:
                    await channel.send(embed = emb)
        except Exception:
            pass



    #log

    @commands.Cog.listener()
    async def on_guild_channel_update(self, before, after):

        try:
            if type(before) == discord.channel.CategoryChannel:
                words = ["категории", 'Категория', 'была обновлена.']

            else:
                words = ['канала', 'Канал', 'был обновлён.']

            server = servers.find_one({"server": before.guild.id})

            if server['mod']['log_channel'] != {}:
                counter = 0
                log = server['mod']['log_channel']['logging']
                channel = await self.bot.fetch_channel(server['mod']['log_channel']['channel'])
                emb = discord.Embed(title = f'Обновление {words[0]}', description = f'{words[1]} {before.mention} {words[2]}', color=0xE28112 )

                if 'channel_name' in log or 'all' in log or 'channel' in log:
                    if before.name != after.name:
                        emb.add_field(name = ' | Обновление названия', value = f'Изначальное название: `{ before.name }`\nСейчас называется: `{ after.name }`', inline = True)
                        counter += 1

                if 'channel_category' in log or 'all' in log or 'channel' in log:
                    if before.category != after.category:
                        emb.add_field(name = ' | Обновление категории', value = f'Изначальная категория: `{ before.category }`\nСейчас в категории: `{ after.category }`', inline = True)
                        counter += 1

                if 'channel_rights' in log or 'all' in log or 'channel' in log:
                    if before.overwrites != after.overwrites:

                        dr = {}
                        for i in dict(before.overwrites):
                            n = []
                            for b in dict(before.overwrites)[i]:
                                n.append(b)
                            dr.update({str(i.id): n})

                        dr2 = {}
                        for i in dict(after.overwrites):
                            n = []
                            for b in dict(after.overwrites)[i]:
                                n.append(b)
                            dr2.update({str(i.id): n})

                        afd = {}

                        for x in dr2:
                            md = {}
                            for nx in dr2[str(x)]:
                                md.update({ str(list(nx)[0]) : list(nx)[1]})
                            afd.update({x: md})

                        drf = {} #совпадения двух словарей
                        ddr = [] #удалённые роли
                        adr = {} #добавленые роли

                        for key in dr:
                            try:
                                if dr2[key] != dr[key]:
                                    drf.update({key: list((set(dr2[key]) | set(dr[key])) - (set(dr2[key]) & set(dr[key]))) })

                            except KeyError:
                                ddr.append(key)

                        #добавленные роли
                        for key2 in dr2:
                            try:
                                dr[key2]
                            except KeyError:
                                for l in dr2[key2]:
                                    if list(l)[1] != None:
                                        try:
                                            adr[key2].append( list(l))
                                        except KeyError:
                                            adr.update({ key2: [ list(l) ] })

                        if adr != {}:
                            text = ''
                            op = ''
                            for i in adr:
                                if before.guild.get_member(int(i)) != None:
                                    memb = before.guild.get_member(int(i))
                                    text += f'{memb.mention} '
                                    op == 'пользователя'


                                if before.guild.get_role(int(i)) != None:
                                    rol = before.guild.get_role(int(i))
                                    text += f'{rol.mention} '
                                    op = 'роли'

                                for n in adr[i]:
                                    text += f'| `{n[0]}` {n[1]}\n'

                            emb.add_field(name = f' | Добавление прав для {op}', value = text.replace('True','<:n:869159450588635196>').replace('False','<:f:869169592201777224>'), inline = True)
                            counter += 1

                        if ddr != []:
                            text = ''
                            counter2 = 0
                            op = ''
                            for i in ddr:

                                if before.guild.get_member(int(i)) != None:
                                    memb = before.guild.get_member(int(i))
                                    text += f'{memb.mention}\n'
                                    op == 'пользователя'

                                if before.guild.get_role(int(i)) != None:
                                    rol = before.guild.get_role(int(i))
                                    text += f'{rol.mention}\n'
                                    op = 'роли'


                            emb.add_field(name = f' | Удаление прав у {op}', value = text, inline = True)
                            counter += 1

                        if drf != {}:

                            text = ''
                            op = ''
                            for i in drf:
                                if before.guild.get_member(int(i)) != None:
                                    memb = before.guild.get_member(int(i))
                                    text += f'Пользователь {memb.mention} \n'


                                if before.guild.get_role(int(i)) != None:
                                    rol = before.guild.get_role(int(i))
                                    text += f'Роль {rol.mention} \n'

                                counter2 = 0
                                for n in drf[i]:
                                    if afd[i][n[0]] != n[1]:
                                        counter2 += 1

                                        text += f'{n[1]} ➜ {afd[i][n[0]]} | `{n[0]}`\n'

                            emb.add_field(name = f' | Имзенение прав', value = f'{text}'.replace('True','<:n:869159450588635196>').replace('False','<:f:869169592201777224>').replace('None','<:m:869169622618873906>'), inline = True)
                            counter += 1


                if 'channel_roles' in log or 'all' in log or 'channel' in log:
                    if before.changed_roles != after.changed_roles:
                        nd = ''
                        yd = ''

                        for i in before.changed_roles:
                            if i not in after.changed_roles:
                                nd = i.mention

                        for i in after.changed_roles:
                            if i not in before.changed_roles:
                                yd = i.mention

                        if yd != '':
                            emb.add_field(name = ' | Роль добавлена в права доступа', value = f'{yd}', inline = True)
                            counter += 1
                        if nd != '':
                            emb.add_field(name = ' | Роль убрана из прав доступа', value = f'{nd}', inline = True)
                            counter += 1


                if 'channel_permissions_synced' in log or 'all' in log or 'channel' in log:
                    if before.permissions_synced != after.permissions_synced:
                        if after.permissions_synced == True:
                            words = 'Права канала были синхронизированы с категорией'
                        else:
                            words = 'Права канала более не синхронизированы с категорией'

                        emb.add_field(name = ' | Синхронизация', value = words, inline = True)
                        counter += 1

                if 'channel_position' in log or 'all' in log or 'channel' in log:
                    if before.position != after.position:
                        emb.add_field(name = f' | Измениение позиции {words[0]}', value = f'Изначальная позиция: {before.position}\nСейчас позиция: {after.position}', inline = True)
                        counter += 1
                if type(after) == discord.channel.TextChannel:

                    if 'channel_slowmode' in log or 'all' in log or 'channel' in log:
                        if before.slowmode_delay != after.slowmode_delay:
                            emb.add_field(name = f' | Медленный режим изменён', value = f'Изначальная ожидание: {funs.time_end(before.slowmode_delay)}\nСейчас ожидание: {funs.time_end(after.slowmode_delay)}', inline = True)
                            counter += 1

                    if 'channel_topic' in log or 'all' in log or 'channel' in log:
                        if before.topic != after.topic:
                            emb.add_field(name = f' | Изменение темы', value = f'Изначальная тема: `{before.topic}`\nСейчас тема: `{after.topic}`', inline = True)
                            counter += 1

                    if 'channel_nsfw' in log or 'all' in log or 'channel' in log:
                        if before.is_nsfw() != after.is_nsfw():
                            emb.add_field(name = f' | Изменение nsfw', value = f'Изначально: {before.is_nsfw()}\nСейчас: {after.is_nsfw()}'.replace('True','<:n:869159450588635196>').replace('False','<:f:869169592201777224>'), inline = True)
                            counter += 1

                if type(after) in [discord.channel.VoiceChannel, discord.channel.StageChannel]:

                    if 'channel_bitrate' in log or 'all' in log or 'channel' in log:
                        if before.bitrate != after.bitrate:
                            emb.add_field(name = f' | Изменение битрейта', value = f'Изначальный битрейт: `{before.bitrate}`\nСейчас битрейт: `{after.bitrate}`', inline = True)
                            counter += 1

                    if 'channel_rtc_region' in log or 'all' in log or 'channel' in log:
                        if before.rtc_region != after.rtc_region:
                            emb.add_field(name = f' | Изменение региона', value = f'Изначальный регион: `{before.rtc_region}`\nСейчас регион: `{after.rtc_region}`', inline = True)
                            counter += 1

                if type(after) == discord.channel.VoiceChannel:

                    if 'channel_user_limit' in log or 'all' in log or 'channel' in log:
                        if before.user_limit != after.user_limit:
                            emb.add_field(name = f' | Изменение лимита', value = f'Изначальный лимит: `{before.user_limit}`\nСейчас лимит: `{after.user_limit}`', inline = True)
                            counter += 1

                if counter != 0:
                    await channel.send(embed = emb)
        except Exception:
            pass


    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):

        try:
            server = servers.find_one({"server": channel.guild.id})

            if server['mod']['log_channel'] != {}:

                if 'channel_create' in server['mod']['log_channel']['logging'] or 'all' in server['mod']['log_channel']['logging'] or 'channel' in server['mod']['log_channel']['logging']:

                    dr = {}
                    drf = {} #совпадения двух словарей
                    for i in dict(channel.overwrites):
                        n = []
                        for b in dict(channel.overwrites)[i]:
                            n.append(b)
                        dr.update({str(i.id): n})

                    for key in dr:
                        for l in dr[key]:
                            if list(l)[1] != None:
                                try:
                                    drf[key].append( list(l))
                                except KeyError:
                                    drf.update({ key: [ list(l) ] })

                    text = ''
                    op = ''
                    for i in drf:
                        if channel.guild.get_member(int(i)) != None:
                            memb = channel.guild.get_member(int(i))
                            text += f'\nПользователь {memb.mention}'


                        if channel.guild.get_role(int(i)) != None:
                            rol = channel.guild.get_role(int(i))
                            text += f'\nРоль {rol.mention}'

                        for n in drf[i]:

                            if n[1] == True:
                                tf = '<:n:869159450588635196>'
                            if n[1] == False:
                                tf = "<:f:869169592201777224>"
                            if n[1] == None:
                                tf = '<:m:869169622618873906>'

                            text += f'\n{tf} | `{n[0]}`'


                    if type(channel) == discord.channel.CategoryChannel:
                        words = f'Категория была создана'
                        words2 = f'Категория {channel.name} была создана'

                        inf = f'Название: `{channel.name}`\n ID: `{channel.id}`\n Позиция: `{channel.position}`'

                    if type(channel) == discord.channel.TextChannel:
                        words = f"Текстовой-канал был создан"
                        words2 = f"Текстовой-канал {channel.mention} был создан"

                        inf = f'Название: `{channel.name}`\n ID: `{channel.id}`\n Позиция: `{channel.position}`\n Категория: `{channel.category}`'

                    if type(channel) == discord.channel.VoiceChannel:
                        words = f"Войс-канал был создан"
                        words2 = f"Войс-канал {channel.mention} был создан"

                        inf = f'Название: `{channel.name}`\n ID: `{channel.id}`\n Позиция: `{channel.position}`\n Категория: `{channel.category}`'

                    if type(channel) == discord.channel.StageChannel:
                        words = f"Трибуна была создана"
                        words2 = f"Трибуна {channel.mention} была создана"

                        inf = f'Название: `{channel.name}`\n ID: `{channel.id}`\n Позиция: `{channel.position}`\n Категория: `{channel.category}`'


                    channel = await self.bot.fetch_channel(server['mod']['log_channel']['channel'])
                    emb = discord.Embed(title = f'{words}', description = f'{words2}', color=0xFFDB8B )
                    if text != '':
                        emb.add_field(name = f' | Назначенные права', value = f'{text}', inline = True)
                    emb.add_field(name = f' | Информация', value = f'{inf}', inline = True)
                    await channel.send(embed = emb)
        except Exception:
            pass

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):


        try:
            server = servers.find_one({"server": channel.guild.id})

            if server['mod']['log_channel'] != {}:
                if 'channel_delete' in server['mod']['log_channel']['logging'] or 'all' in server['mod']['log_channel']['logging'] or 'channel' in server['mod']['log_channel']['logging']:

                    if type(channel) == discord.channel.CategoryChannel:
                        words = f'Категория была удалена'
                        words2 = f'Категория {channel.name} была удалена'

                        inf = f'Название: `{channel.name}`\n ID: `{channel.id}`\n Позиция: `{channel.position}`'

                    if type(channel) == discord.channel.TextChannel:
                        words = f"Текстовой-канал был удалён"
                        words2 = f"Текстовой-канал {channel.mention} был удалён"

                        inf = f'Название: `{channel.name}`\n ID: `{channel.id}`\n Позиция: `{channel.position}`\n Категория: `{channel.category}`'

                    if type(channel) == discord.channel.VoiceChannel:
                        words = f"Войс-канал был удалён"
                        words2 = f"Войс-канал {channel.mention} был удалён"

                        inf = f'Название: `{channel.name}`\n ID: `{channel.id}`\n Позиция: `{channel.position}`\n Категория: `{channel.category}`'

                    if type(channel) == discord.channel.StageChannel:
                        words = f"Трибуна была удалена"
                        words2 = f"Трибуна {channel.mention} была удалена"

                        inf = f'Название: `{channel.name}`\n ID: `{channel.id}`\n Позиция: `{channel.position}`\n Категория: `{channel.category}`'

                    channel = await self.bot.fetch_channel(server['mod']['log_channel']['channel'])
                    emb = discord.Embed(title = f'{words}', description = f'{words2}', color=0xFDE910 )
                    emb.add_field(name = f' | Информация', value = f'{inf}', inline = True)
                    await channel.send(embed = emb)

        except Exception:
            pass

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        try:
            server = servers.find_one({"server": guild.id})

            if server['mod']['log_channel'] != {}:
                log = server['mod']['log_channel']['logging']
                if 'member_ban' in log or 'all' in log or 'member' in log:
                    channel = await self.bot.fetch_channel(server['mod']['log_channel']['channel'])
                    emb = discord.Embed(title = f'Бан пользователя', description = f'Пользователь {user.mention} был забанен', color=0xE52B50 )
                    await channel.send(embed = emb)
        except Exception:
            pass

    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):

        try:
            server = servers.find_one({"server": guild.id})

            if server['mod']['log_channel'] != {}:
                log = server['mod']['log_channel']['logging']
                if 'member_unban' in log or 'all' in log or 'member' in log:
                    channel = await self.bot.fetch_channel(server['mod']['log_channel']['channel'])
                    emb = discord.Embed(title = f'Разбан пользователя', description = f'Пользователь {user.mention} был разбанен', color=0xE52B50 )
                    await channel.send(embed = emb)
        except Exception:
            pass

    @commands.Cog.listener()
    async def on_guild_emojis_update(self, guild, before, after):

        try:
            server = servers.find_one({"server": guild.id})
            if server['mod']['log_channel'] != {}:
                lem = list((set(before) | set(after)) - (set(before) & set(after)))

                counter = 0
                log = server['mod']['log_channel']['logging']
                channel = await self.bot.fetch_channel(server['mod']['log_channel']['channel'])

                for i in lem:

                    if i not in before and i in after:
                        if 'emoji_create' in log or 'all' in log or 'emoji' in log:
                            emb = discord.Embed(title = f'Обновление эмоджи', description = f'Эмоджи {i} был добавлен\nID: {i.id}\n[URL]({i.url})', color=0xFFDB8B )
                            counter += 1

                    if i in before and i not in after:
                        if 'emoji_delete' in log or 'all' in log or 'emoji' in log:
                            emb = discord.Embed(title = f'Обновление эмоджи', description = f'Эмоджи {i} был удалён', color=0xFFDB8B )
                            counter += 1


                if counter != 0:
                    await channel.send(embed = emb)
        except Exception:
            pass

    @commands.Cog.listener()
    async def on_invite_create(self, invite):

        try:
            server = servers.find_one({"server": invite.guild.id})
            if server['mod']['log_channel'] != {}:

                counter = 0
                log = server['mod']['log_channel']['logging']
                channel = await self.bot.fetch_channel(server['mod']['log_channel']['channel'])
                if 'invite_create' in log or 'all' in log or 'invite' in log:
                    if invite.max_age == 0:
                        ttime = 'infinity'
                    else:
                        ttime = funs.time_end(invite.max_age)

                    emb = discord.Embed(title = f'Приглашение создано', description = f'Код приглашения: `{invite.code}`\nПригласивший: {invite.inviter.mention}\nЛимит времени: {ttime}\nЛимит использования: {invite.max_uses}\nВременное членство: {invite.temporary}'.replace('True','<:n:869159450588635196>').replace('False','<:f:869169592201777224>'), color=0x0000FF )
                    await channel.send(embed = emb)
        except Exception:
            pass

    @commands.Cog.listener()
    async def on_invite_delete(self, invite):


        try:
            server = servers.find_one({"server": invite.guild.id})
            if server['mod']['log_channel'] != {}:

                counter = 0
                log = server['mod']['log_channel']['logging']
                channel = await self.bot.fetch_channel(server['mod']['log_channel']['channel'])
                if 'invite_delete' in log or 'all' in log or 'invite' in log:
                    emb = discord.Embed(title = f'Приглашение удалено', description = f'Код приглашения: `{invite.code}`', color=0x0000FF )
                    await channel.send(embed = emb)
        except Exception:
            pass

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):

        try:
            server = servers.find_one({"server": before.guild.id})
            if server['mod']['log_channel'] != {}:
                if before.author.bot == True:
                    return

                counter = 0
                log = server['mod']['log_channel']['logging']
                channel = await self.bot.fetch_channel(server['mod']['log_channel']['channel'])
                if 'message_edit' in log or 'all' in log or 'message' in log:
                    emb = discord.Embed(title = f'Сообщение изменено', description = f'Автор сообщения: {after.author.mention}\nКанал: {after.channel.mention}\nСообщение: [Jump]({after.jump_url})', color=0xFFDB8B )
                    emb.add_field(name = f' | Изначальное сообщение', value = f'`{before.content}`', inline = True)
                    emb.add_field(name = f' | Сейчас сообщение', value = f'`{after.content}`', inline = True)
                    await channel.send(embed = emb)
        except Exception:
            pass

    @commands.Cog.listener()
    async def on_message_delete(self, message):


        try:
            server = servers.find_one({"server": message.guild.id})
            if server['mod']['log_channel'] != {}:
                if message.author.bot == True:
                    return

                log = server['mod']['log_channel']['logging']
                channel = await self.bot.fetch_channel(server['mod']['log_channel']['channel'])
                if 'message_delete' in log or 'all' in log or 'message' in log:

                    emb = discord.Embed(title = f'Сообщение удалено', description = f'Автор: {message.author.mention}\nКанал: {message.channel.mention}\nID: {message.id}\nСообщение: `{message.content}`', color=0xFFDB8B )
                    await channel.send(embed = emb)
        except Exception:
            pass

    @commands.Cog.listener()
    async def on_guild_update(self, before, after):


        try:
            server = servers.find_one({"server": before.id})

            if server['mod']['log_channel'] != {}:
                counter = 0
                log = server['mod']['log_channel']['logging']
                channel = await self.bot.fetch_channel(server['mod']['log_channel']['channel'])
                emb = discord.Embed(title = f'Обновление сервера', description = f'Сервер был обновлён', color=0xE28112 )

                if 'guild_afk_channel' in log or 'all' in log or 'guild' in log:
                    if before.afk_channel != after.afk_channel:
                        emb.add_field(name = ' | Обновление AFK канала', value = f'Изначальный канал: {before.afk_channel}\nСейчас канал: { after.afk_channel }', inline = True)
                        counter += 1

                if 'guild_afk_timeout' in log or 'all' in log or 'guild' in log:
                    if before.afk_timeout != after.afk_timeout:
                        emb.add_field(name = ' | Обновление AFK тайм-аут', value = f'Изначальный тайм-аут: `{funs.time_end(before.afk_timeout)}`\nСейчас тайм-аут: `{ funs.time_end(after.afk_timeout) }`', inline = True)
                        counter += 1

                if 'guild_banner' in log or 'all' in log or 'guild' in log:
                    if before.banner.url != after.banner.url:
                        emb.add_field(name = ' | Обновление баннера', value = f'Изначальный баннер: [url]({before.banner.url})\nСейчас баннер: [url]({ after.banner.url })', inline = True)
                        counter += 1

                if 'guild_bitrate_limit' in log or 'all' in log or 'guild' in log:
                    if before.bitrate_limit != after.bitrate_limit:
                        emb.add_field(name = ' | Обновление максимального битрейта', value = f'Изначальный м.бит.: `{before.bitrate_limit}`\nСейчас м.бит.: `{ after.bitrate_limit }`', inline = True)
                        counter += 1

                if 'guild_default_notifications' in log or 'all' in log or 'guild' in log:
                    if before.default_notifications != after.default_notifications:
                        if before.default_notifications == discord.NotificationLevel.only_mentions:
                            bdn = "Только упоминания"
                            adn = "Все сообщения"
                        else:
                            adn = "Только упоминания"
                            bdn = "Все сообщения"

                        emb.add_field(name = ' | Обновление уведомлений', value = f'Изначальные уведомления: `{bdn}`\nСейчас уведомления: `{adn}`', inline = True)
                        counter += 1

                if 'guild_description' in log or 'all' in log or 'guild' in log:
                    if before.description != after.description:
                        emb.add_field(name = ' | Обновление описания', value = f'Изначальное описание: `{before.description}`\nСейчас описание: `{ after.description }`', inline = True)
                        counter += 1

                if 'guild_mfa_level' in log or 'all' in log or 'guild' in log:
                    if before.mfa_level != after.mfa_level:
                        emb.add_field(name = ' | Обновление 2FA', value = f'Изначальный 2FA: `{before.mfa_level}`\nСейчас 2FA: `{after.mfa_level}`'.replace('1','<:n:869159450588635196>').replace('0','<:f:869169592201777224>'), inline = True)
                        counter += 1

                if 'guild_verification_level' in log or 'all' in log or 'guild' in log:
                    if before.verification_level != after.verification_level:
                        emb.add_field(name = ' | Обновление уровня проверки', value = f'Изначальный уровень: `{before.verification_level}`\nСейчас уровень: `{ after.verification_level }`', inline = True)
                        counter += 1

                if 'guild_splash' in log or 'all' in log or 'guild' in log:
                    if before.splash.url != after.splash.url:
                        emb.add_field(name = ' | Обновление фона приглашения', value = f'Изначальный фон: [url]({before.splash.url})\nСейчас фон: [url]({ after.splash.url })', inline = True)
                        counter += 1

                if 'guild_emoji_limit' in log or 'all' in log or 'guild' in log:
                    if before.emoji_limit != after.emoji_limit:
                        emb.add_field(name = ' | Обновление лимита эмоджи', value = f'Изначальный лимит: `{before.emoji_limit}`\nСейчас лимит: `{ after.emoji_limit }`', inline = True)
                        counter += 1

                if 'guild_content_filter' in log or 'all' in log or 'guild' in log:
                    if before.explicit_content_filter != after.explicit_content_filter:
                        emb.add_field(name = ' | Обновление фильтра контента', value = f'Изначально: `{before.explicit_content_filter}`\nСейчас: `{ after.explicit_content_filter }`', inline = True)
                        counter += 1

                if 'guild_filesize_limit' in log or 'all' in log or 'guild' in log:
                    if before.filesize_limit != after.filesize_limit:
                        emb.add_field(name = ' | Обновление максимального размера изображения', value = f'Изначальный размер: `{before.filesize_limit}`\nСейчас размер: `{ after.filesize_limit }`', inline = True)
                        counter += 1

                if 'guild_icon' in log or 'all' in log or 'guild' in log:
                    if before.icon.url != after.icon.url:
                        emb.add_field(name = ' | Обновление иконки сервера', value = f'Изначальная иконка: [url]({before.icon.url})\nСейчас иконка: [url]({ after.icon.url })', inline = True)
                        counter += 1

                if 'guild_name' in log or 'all' in log or 'guild' in log:
                    if before.name != after.name:
                        emb.add_field(name = ' | Обновление названия', value = f'Изначальное название: `{before.name}`\nСейчас название: `{ after.name }`', inline = True)
                        counter += 1

                if 'guild_owner' in log or 'all' in log or 'guild' in log:
                    if before.owner_id != after.owner_id:
                        emb.add_field(name = ' | Обновление создателя', value = f'Изначальный создатель: `{before.owner}`\nСейчас создатель: `{ after.owner }`', inline = True)
                        counter += 1


                if counter != 0:
                    await channel.send(embed = emb)

        except Exception:
            pass

    @commands.Cog.listener()
    async def on_guild_role_create(self, role):


        try:
            server = servers.find_one({"server": role.guild.id})
            if server['mod']['log_channel'] != {}:

                log = server['mod']['log_channel']['logging']
                channel = await self.bot.fetch_channel(server['mod']['log_channel']['channel'])
                if 'role_create' in log or 'all' in log or 'role' in log:
                    emb = discord.Embed(title = f'Роль создана', description = f'Роль {role.mention} была создана', color=0xFFDB8B )
                    emb.add_field(name = ' | Информация', value = f'Название: `{role.name}`\nОтображение отдельно: {role.hoist}\nПозиция: {role.position}\nЦвет: {role.color}\nМожно упоминать: {role.mentionable}'.replace('True','<:n:869159450588635196>').replace('False','<:f:869169592201777224>'), inline = False)
                    text1 = ''
                    text2 = ''
                    con = 0
                    for i in role.permissions:
                        text = ''
                        text += f"{list(i)[1]} {i[0]}\n"

                        text = text.replace('True', '<:n:869159450588635196>')
                        text = text.replace('False', '<:f:869169592201777224>')
                        con += 1
                        if con <= 16:
                            text1 += text
                        else:
                            text2 += text

                    emb.add_field(name = ' | Права', value = text1, inline = True)

                    if text2 != '':
                        emb.add_field(name = ' | Права', value = text2, inline = True)

                    await channel.send(embed = emb)
        except Exception:
            pass

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):


        try:
            server = servers.find_one({"server": role.guild.id})
            if server['mod']['log_channel'] != {}:

                log = server['mod']['log_channel']['logging']
                channel = await self.bot.fetch_channel(server['mod']['log_channel']['channel'])
                if 'role_delete' in log or 'all' in log or 'role' in log:
                    emb = discord.Embed(title = f'Роль удалена', description = f'Роль {role.name} была удалена', color=0xE52B50 )

                    await channel.send(embed = emb)
        except Exception:
            pass

    @commands.Cog.listener()
    async def on_guild_role_update(self, before, after):


        try:
            server = servers.find_one({"server": before.guild.id})
            if server['mod']['log_channel'] != {}:

                counter = 0
                log = server['mod']['log_channel']['logging']
                channel = await self.bot.fetch_channel(server['mod']['log_channel']['channel'])
                emb = discord.Embed(title = f'Роль обновлена', description = f'Роль {after.mention} была обновлена', color=0xE52B50 )

                if 'role_color' in log or 'all' in log or 'guild' in log:
                    if before.color != after.color:
                        emb.add_field(name = ' | Обновление цвета', value = f'Изначальный цвет: {before.color}\nСейчас цвет: { after.color }', inline = True)
                        counter += 1

                if 'role_hoist' in log or 'all' in log:
                    if before.hoist != after.hoist:
                        emb.add_field(name = ' | Обновление отображения', value = f'Изначально: {before.hoist}\nСейчас: { after.hoist }'.replace('True','<:n:869159450588635196>').replace('False','<:f:869169592201777224>'), inline = True)
                        counter += 1

                if 'role_mentionable' in log or 'all' in log or 'guild' in log:
                    if before.mentionable != after.mentionable:
                        emb.add_field(name = ' | Обновление упоминания роли', value = f'Изначально: {before.mentionable}\nСейчас: { after.mentionable }'.replace('True','<:n:869159450588635196>').replace('False','<:f:869169592201777224>'), inline = True)
                        counter += 1

                if 'role_name' in log or 'all' in log or 'guild' in log:
                    if before.name != after.name:
                        emb.add_field(name = ' | Обновление названия', value = f'Изначально название: `{before.name}`\nСейчас название: `{ after.name }`', inline = True)
                        counter += 1

                if 'role_position' in log or 'all' in log or 'guild' in log:
                    if before.position != after.position:
                        emb.add_field(name = ' | Обновление позиции', value = f'Изначальная позиция: `{before.position}`\nСейчас позиция: `{ after.position }`', inline = True)
                        counter += 1

                if 'role_permissions' in log or 'all' in log or 'guild' in log:
                    if before.permissions != after.permissions:
                        text1 = ''
                        text2 = ''
                        aftlist = {}
                        con = 0
                        for i in after.permissions:
                            aftlist.update({ str(list(i)[0]): list(i)[1] })

                        for i in before.permissions:
                            text = ''
                            if str(aftlist[ str(list(i)[0]) ]) != str(list(i)[1]):
                                text += f'{list(i)[1]} {list(i)[0]}\n'
                                text = text.replace('False', '<:n:869159450588635196>')
                                text = text.replace('True', '<:f:869169592201777224>')
                                con += 1
                                if con <= 16:
                                    text1 += text
                                else:
                                    text2 += text

                        emb.add_field(name = ' | Обновление прав', value = text1, inline = True)
                        counter += 1

                        if text2 != '':
                            emb.add_field(name = ' | Обновление прав', value = text2, inline = True)
                            counter += 1

                if counter != 0:
                    await channel.send(embed = emb)
        except Exception:
            pass

def setup(bot):
    bot.add_cog(MainCog(bot))
