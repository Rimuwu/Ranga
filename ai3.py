# -*- coding: utf-8 -*-
import nextcord as discord
from nextcord import Interaction, SlashOption, ChannelType
from nextcord.ext import tasks, commands
from nextcord.utils import utcnow

import requests
from PIL import Image, ImageFont, ImageDraw, ImageOps, ImageSequence, ImageFilter
import io
from io import BytesIO
import random
from random import choice
import asyncio
import time
from datetime import datetime, timedelta
import os
import pymongo
import math
from fuzzywuzzy import fuzz
import config
import pprint
import os
from functions import functions


client = pymongo.MongoClient(config.cluster_token)
db = client.bot

backs = db.bs
servers = db.servers
settings = db.settings

start_time = time.time()

# префикс ======================================= #

def get_prefix(client, message):
    global servers
    try:
        prefix_server = servers.find_one({"server": message.guild.id})["prefix"]
        return str(prefix_server)
    except:
        return "+"

bot = commands.Bot(command_prefix = get_prefix, intents = discord.Intents.all())


# коги ======================================= #

bot.remove_command( "help" )

for filename in os.listdir("./Cog"):
    if filename.endswith(".py"):
        bot.load_extension(f"Cog.{filename[:-3]}")

    else:
        if os.path.isfile(filename):
            print(f"Unable to load {filename[:-3]}")


# slash ====================================== #

# @bot.slash_command(guild_ids = [660507362758754311])
# async def repeat(Interaction:Interaction, message:str):
#     await Interaction.response.send_message( f'{Interaction} {message}')

g_ids = [601124004224434357, 660507362758754311, 827219604701970482, 847102750928011274]

@bot.slash_command(guild_ids = g_ids, description = '🍡 | Погладить пользователя.')
async def pat(Interaction:Interaction, member:discord.Member):
    server = servers.find_one({"server": Interaction.guild.id})
    author = Interaction.user

    if member == author:
        msg = f'{author.mention} погладил(а) самого себя, вот чсв....'
    else:
        msg = f'{author.mention} погладил(а) {member.mention}'

    emb=discord.Embed(description = str(msg), title = "🍡 | Реакция: погладить", color=server['embed_color'])
    rli = ["https://static.grouple.co/uploads/pics/10/83/525_o.gif",
            "https://pa1.narvii.com/6607/1f16bfa7ba7763602c172cfef17510ec863872a0_hq.gif",
            "https://data.whicdn.com/images/116773791/original.gif",
            "https://animegif.ru/up/photos/album/oct17/171021_210.gif",
            "https://i.gifer.com/78D.gif",
            "https://media.tenor.com/images/a671268253717ff877474fd019ef73e9/tenor.gif",
            "https://i.pinimg.com/originals/e3/e2/58/e3e2588fbae9422f2bd4813c324b1298.gif",
            "https://i.gifer.com/embedded/download/8jQj.gif"]

    emb.set_image(url = random.choice(rli))
    await Interaction.response.send_message(embed=emb)

@bot.slash_command(guild_ids = g_ids, description = '❤ | Поцеловать пользователя.')
async def kiss(Interaction:Interaction, member:discord.Member):
    server = servers.find_one({"server": Interaction.guild.id})
    author = Interaction.user

    if member == author:
        msg = f'{author.mention} поцеловал(а) самого себя, без комментариев'
    else:
        msg = f'{author.mention} поцеловал(а) {member.mention}'

    emb=discord.Embed(description = str(msg), title = "❤ | Реакция: поцеловать", color=server['embed_color'])

    rli = ["https://lifeo.ru/wp-content/uploads/gif-anime-kisses-48.gif",
    "https://data.whicdn.com/images/294084710/original.gif",
    'https://giffiles.alphacoders.com/131/131257.gif',
    'https://i.pinimg.com/originals/6b/8a/4d/6b8a4d963f5221df1bf6eb22cd5fe1a4.gif',

    ]
    emb.set_image(url = random.choice(rli))
    await Interaction.response.send_message(embed=emb)


# event ====================================== #

async def global_chat(message, s, server):

    async def emb(word, server):
        embed = discord.Embed(title = f"Ошибка", description = f"Данное слово (`{word}`) запрещено в межсервереом чате!", color=0xf44a4a)
        webhook = await bot.fetch_webhook(server['globalchat']['webhook'])
        await webhook.send(username = "Система межсервера", avatar_url = 'https://img.icons8.com/dusk/64/000000/web-shield.png', embed=embed)

    try:
        if message.webhook_id == None:
            if message.author.bot == True: return
            #проверка на варны
            try:
                wmax = s['bl global chat'][str(message.author.id)][max(s['bl global chat'][str(message.author.id)].keys())]
                if time.time() < wmax['time']:
                    try:
                        await message.delete()
                    except Exception:
                        pass
                    return

            except Exception:
                pass
            #проверка на бан в межсервере
            try:
                s['bl global chat'][str(message.author.id)]['ban']
                try:
                    await message.delete()
                except Exception:
                    pass
                return

            except Exception:
                pass

            if message.channel.id == server['globalchat']['channel']:

                #проверка на слова
                for word in s['off-words']:
                    allword = ''
                    for spw in message.content.split():
                        allword = allword + spw
                        if fuzz.token_sort_ratio(word,allword) > 90:
                            await emb(word, server)
                            await message.delete()
                            return

                        if allword.find(str(word)) != -1:
                            await emb(word, server)
                            await message.delete()
                            return

                        if spw.find(str(word)) != -1:
                            await emb(word, server)
                            await message.delete()
                            return

                #проверка на флуд
                messages = await message.channel.history().flatten()
                l = []

                for mess in messages:
                    if mess.author.id == message.author.id:
                        if message.content != '':
                            l.append(mess)

                lm = []
                counter = 0
                m = []
                for i in l:
                    if counter != 3:
                        m.append(i)
                        lm.append(i.content)
                        counter += 1

                flud_p = 0
                for mes in lm:
                    if fuzz.token_sort_ratio(message.content, mes) > 80 or fuzz.ratio(message.content, mes) > 80:
                        flud_p += 1


                if flud_p >= 3:
                    for i in m:
                        try:
                            await i.delete()
                        except Exception:
                            pass


                    try:
                        id = message.author.id
                        reason = 'Auto flud warn'
                        s = settings.find_one({"sid": 1})
                        s['bl global chat'][str(id)]
                        nw = len(s['bl global chat'][str(id)].keys())

                        if nw < 3:
                            s['bl global chat'][str(id)].update({str(nw+1):{'reason':reason,"time":time.time() + 2628000}})
                            settings.update_one({"sid": 1},{'$set': {'bl global chat':s['bl global chat']}})
                            await message.channel.send(f"Пользователь c id `{id}` получил варн #{nw+1}\nПо причине: Auto flud warn")
                        else:
                            s['bl global chat'][str(id)].update({'ban':f'{reason} | auto ban due to 3 warns'})
                            settings.update_one({"sid": 1},{'$set': {'bl global chat':s['bl global chat']}})
                            await message.channel.send(f"Пользователь c id `{id}` был автоматически забанен за х3 предупреждения\nПо причине: Auto flud warn")


                    except Exception:
                        s['bl global chat'].update({str(id):{'1':{'reason':reason,"time":time.time() + 604800}}})
                        settings.update_one({"sid": 1},{'$set': {'bl global chat':s['bl global chat']}})
                        await message.channel.send(f"Пользователь c id `{id}` получил варн #1\nПо причине: Auto flud warn")



                try:
                    code = int(server['global_code'])
                except Exception:
                    code = 0

                if code == 0:
                    guilds = servers.find({'globalchat':{'$ne':None}})
                else:
                    guilds = servers.find({'global_code': code})

                for i in guilds:
                    try:
                        ccode = i['global_code']
                        if ccode == None:
                            ccode = 0
                    except Exception:
                        ccode = 0

                    try:
                        if i['server'] != server['server']:

                            if code == ccode:
                                try:
                                    y = 0
                                    try:
                                        webhook = await bot.fetch_webhook(i['globalchat']['webhook'])
                                        y = 1
                                    except Exception:
                                        y = 2

                                    if y == 1:
                                        await webhook.send(message.clean_content, files = [await a.to_file() for a in message.attachments], username = f"{message.author.name}#{message.author.discriminator}", avatar_url = message.author.avatar.url)
                                except Exception:
                                    pass

                    except Exception:
                        pass

                channel = await bot.fetch_channel(865527704085856256)
                try:
                    await channel.send(f'Имя: {message.author.name}#{message.author.discriminator}\nID: {message.author.id}\nСервер ID: {message.author.guild.id}\nCode: {code}\nКонтент: `{message.clean_content}`', files = [await a.to_file() for a in message.attachments])
                except Exception:
                    pass
    except Exception:
        pass

async def lvl_up_image(message, user, server):

    server = servers.find_one({"server": message.guild.id})
    user = functions.user_check(message.author, message.guild)

    upitems = server["upsend_sett"]['upitems']
    UpSend = server["upsend_sett"]['upsend']
    ust = server["upsend_sett"]
    lvl = user['lvl']

    try:
        mr = upitems[str(lvl)]['money']
    except Exception:
        mr = 0
        lv = lvl
        while mr == 0:
            lv -= 1
            if lv != 0:
                try:
                    mr += upitems[str(lv)]['money']
                except:
                    pass
            if lv <= 0:
                mr = 350



    bal = random.randint(int(mr - mr / 100 * 50), mr)

    functions.user_update(message.author.id, message.guild, "xp", 0)
    functions.user_update(message.author.id, message.guild, "lvl", user['lvl']+1)

    functions.user_update(message.author.id, message.guild, "money", user['money']+bal)

    try:
        for i in upitems[str(lvl+1)]['items']:
            user['inv'].append(functions.creat_item(message.guild.id, i))
        functions.user_update(message.author.id, message.guild, "inv", user['inv'])
    except Exception:
        pass

    if UpSend == 777777777777777771 or UpSend == None:
        return


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
        mask = Image.new('L',(720, 217))
        ImageDraw.Draw(mask).polygon(xy=[(550, 0),(720, 0),(720,217),(450,217)], fill = 250)
        mask = mask.filter(ImageFilter.BoxBlur(1.5))
        im.paste(im.filter( ImageFilter.GaussianBlur(radius=12) ), mask=mask)
        return im


    member = message.author

    alpha = Image.open('elements/alpha.png')
    alpha = alpha.resize((720, 217), Image.ANTIALIAS) # улучшение качества

    if server['upsend_sett']['image_url'] == None:
        listurl = [
        'https://ic.wampi.ru/2021/08/19/card-1.png',
        'https://ic.wampi.ru/2021/08/19/card-2.png',
        'https://ic.wampi.ru/2021/08/19/card-3.png',
        'https://ic.wampi.ru/2021/08/19/card-4.png',
        'https://ic.wampi.ru/2021/08/19/card-5.png',
        'https://ic.wampi.ru/2021/08/19/card-6.png',
        ]
        url = random.choice(listurl)
    else:
        url = server['upsend_sett']['image_url']

    if ust['type'] == "png":

        response = requests.get(url, stream = True)
        response = Image.open(io.BytesIO(response.content))
        response = response.convert("RGBA")
        img = response.resize((720, 217), Image.ANTIALIAS) # улучшение качества

    if ust['type'] == "gif":

        response = requests.get(url, stream=True)
        response.raw.decode_content = True
        img = Image.open(response.raw)


    mask = Image.new('L', (720, 217))
    bar = Image.new('RGB', (720, 217))

    ImageDraw.Draw(mask).polygon(xy=[(550, 0),(720, 0),(720,217),(450,217)], fill = 160)
    ImageDraw.Draw(bar).polygon(xy=[(550, 0),(720, 0),(720,217),(450,217)], fill = (0, 0, 0) )
    bar = bar.filter(ImageFilter.BoxBlur(0.5))
    mask = mask.filter(ImageFilter.BoxBlur(1.5))
    alpha = Image.composite(bar, alpha, mask)

    idraw = ImageDraw.Draw(alpha)
    para = ImageFont.truetype("fonts/20421.ttf", size = 30)
    paga = ImageFont.truetype("fonts/20421.ttf", size = 60)
    pata = ImageFont.truetype("fonts/20421.ttf", size = 50)
    idraw.text((515,70), f"+{str(bal)}\n монет", font = para)

    if len(str(lvl)) == 1:
        idraw.text((530,130), f"{lvl} > {lvl+1}", font = paga)
    elif len(str(lvl)) == 2:
        idraw.text((500,130), f"{lvl} > {lvl+1}", font = paga)
    else:
        idraw.text((500,130), f"{lvl} > {lvl+1}", font = pata)


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
    response1 = response1.resize((200, 200), Image.ANTIALIAS)
    size = (200, 200)

    im = response1
    im = crop(im, size)
    im.putalpha(prepare_mask(size, 4))

    bg_img = alpha
    fg_img = im
    alpha = trans_paste(fg_img, bg_img, 1.0, (10, 10, 210, 210))


    if ust['type'] == "png":
        img = bl_f(img)

        bg_img = img
        fg_img = alpha
        img = trans_paste(fg_img, bg_img, 1.0)

        image = img
        output = BytesIO()
        image.save(output, 'png')
        image_pix=BytesIO(output.getvalue())

        file = discord.File(fp = image_pix, filename="up_card.png")
        ul = 'png'

    if ust['type'] == "gif":
        fs = []
        for frame in ImageSequence.Iterator(img):
            frame = frame.convert("RGBA")
            frame = frame.resize((720, 217), Image.ANTIALIAS)
            frame = bl_f(frame)

            bg_img = frame
            fg_img = alpha
            img = trans_paste(fg_img, bg_img, 1.0)

            b = io.BytesIO()
            frame.save(b, format="GIF",optimize=True, quality=75)
            frame = Image.open(b)
            fs.append(frame)


        fs[0].save('up_card.gif', save_all=True, append_images=fs[1:], loop = 0, optimize=True, quality=75)

        file = discord.File(fp = "up_card.gif", filename="up_card.gif")
        ul = 'gif'


    up_text = functions.text_replase(server['upsend_sett']['up_message'], message.author)
    if up_text == None:
        up_text = f'<@{message.author.id}>'

    if UpSend == 777777777777777777 or UpSend == True:
        up = message.channel
    else:
        up =  bot.get_channel(UpSend)

    try:

        if server['upsend_sett']['emb_st'] == False:
            await up.send(up_text, file = file)

        if server['upsend_sett']['emb_st'] == True:
            emb = discord.Embed(description = up_text, color= server['embed_color'])
            emb.set_image(url=f"attachment://up_card.{ul}")
            await up.send(file=file, embed = emb)

    except Exception:
        pass


    try:
        os.remove(f'up_card.{ul}')
    except Exception:
        pass



async def lvl(message, server):

    user = functions.user_check(message.author, message.guild)
    expn = 5 * user['lvl']*user['lvl'] + 50 * user['lvl'] + 100
    expi = random.randint(0, server['economy']['lvl_xp'])
    expii = user['xp'] + expi
    functions.user_update(message.author.id, message.guild, "xp", expii)

    if expn <= user['xp']:
        try:
            await lvl_up_image(message, user, server)
        except Exception:
            pass

    return True



async def mod_flud(message, server, met = None):
    #Возвращаем False если всё норм, True если замечено нарушение

    messages = await message.channel.history().flatten()
    l = []

    for mess in messages:
        if mess.author.id == message.author.id:
            if message.content != '':
                l.append(mess)



    if met == None:
        lm = []
        counter = 0
        for i in l:
            if counter != server['mod']['flud_shield']['repetitions']:
                lm.append(i.content)
                counter += 1

        flud_p = 0
        for mes in lm:
            if fuzz.token_sort_ratio(message.content, mes) > 80 or fuzz.ratio(message.content, mes) > 80:
                flud_p += 1


        if flud_p >= server['mod']['flud_shield']['repetitions']:
            return True

        else:
            return False

    else:
        lm = []
        counter = 0
        for i in l:
            if counter != server['mod']['flud_shield']['repetitions']:
                lm.append(i)
                counter += 1

        return lm

def mod_bad_words(message, server):

    allword = ''

    for word in server['mod']['bad_words']['words']:
        for spw in message.content.split():
            allword = allword + spw
            if fuzz.token_sort_ratio(word,allword) > 90:
                return True

            if allword.find(str(word)) != -1:
                return True

            if spw.find(str(word)) != -1:
                return True

    return False

def mod_media(message):
    count = 0
    for attach in message.attachments:
        count += 1

    if count > 0:
        return False
    else:
        return True

async def punishment_mod(message, server, p, reason, shield):

    user = message.author

    if 'ban' in p:
        try:
            await message.author.ban(reason="Auto flud ban")
        except Exception:
            pass

    if 'ban' not in p:

        if 'kick' in p:
            try:
                await message.author.kick(reason= 'Auto flud kick')
            except Exception:
                pass

        if 'kick' not in p:

            if 'warn' in p:
                await functions.warn(await bot.get_context(message), message.author, reason, bot.user)

            if 'role-add' in p:
                if server['mod'][shield]['add-role'] != None:
                    try:
                        await user.add_roles(bot.get_guild(message.guild.id).get_role(server['mod'][shield]['add-role']))
                    except Exception:
                        pass

            if 'role-remove' in p:
                if server['mod'][shield]['roleremove'] != None:
                    try:
                        await user.remove_roles(bot.get_guild(message.guild.id).get_role(server['mod'][shield]['remove-role']))
                    except Exception:
                        pass

    if 'message' in p:
        if server['mod'][shield]['message'] != None:
            try:
                if server['mod'][shield]['mess-type'] == 'emb':
                    emb = discord.Embed(description = server['mod'][shield]['message'], color=0xf03e65)
                    await message.channel.send(embed = emb)
                if server['mod'][shield]['mess-type'] == 'mes':
                    await message.channel.send(server['mod'][shield]['message'])
            except Exception:
                pass

    if 'delete-all' in p:
        ms = await mod_flud(message, server, 'noNone')
        for mess in ms:
            try:
                await mess.delete()
            except Exception:
                pass

    if 'delete' in p:
        if 'delete-all' not in p:
            try:
                await message.delete()
            except Exception:
                pass


cooldown = commands.CooldownMapping.from_cooldown(1, 60, commands.BucketType.member)#куллдаун на 60 сек после одного отправленного сообщения

@bot.event
async def on_message(message):

    st = time.time()
    s = settings.find_one({"sid": 1})

    if message.author.bot == True: return
    if message.guild == None:
        emb = discord.Embed(description = "Йоу, перейдите на сервер что бы использовать бота. \n Если у вас нету подходящего сервера, вы можете перейти на сервер поддержки бота > [Клик](https://discord.gg/cFa8K37pBa)", color=0xf03e65)
        await message.channel.send(embed = emb)
        return
    if message.guild.id in s['bl servers']: return

    server = servers.find_one({"server": message.guild.id})
    if server == None:
        functions.insert_server(message.guild)
        server = servers.find_one({"server": message.guild.id})

    #не выполнение команды если человек в мьюте
    try:
        mm = server['mute_members'][f"{message.author.id}"]

        try:
            await message.delete()
        except Exception:
            pass

        return
    except Exception:
        pass

    try:
        if message.content == f'{bot.user.mention}':
            await message.channel.send(f"Гав! Мой префикс `{server['prefix']}`")
    except Exception:
        pass

    if message.author.id in s['black list']: return

    try:
        if message.channel.id in server['mod']['black_channels']: return
    except Exception:
        pass
    try:
        if message.channel.id == server['globalchat']['channel']:
            await global_chat(message, s, server)
            return
    except Exception:
        pass

    # #auto mod
    try:
        if server['mod']['media_channels'] != {} or server['mod']['bad_words'] != {} or server['mod']['flud_shield'] != {} or server['mod']['members_mention'] != {} or server['mod']['roles_mention'] != {}:

            if server['mod']['black_channels'] == [] or message.channel.id not in server['mod']['black_channels']:
                if server['mod']['wlist_members'] == [] or message.author.id not in server['mod']['wlist_members']:

                    list_roles = []
                    for role in message.author.roles: list_roles.append(role.id)
                    if list(set(server['mod']['wlist_roles']) & set(list_roles)) == []:

                        if server['mod']['flud_shield'] != {}:
                            if message.channel.id not in server['mod']['flud_ch_nor']:
                                if await mod_flud(message, server) == True:
                                    try:
                                        await punishment_mod(message, server, server['mod']['flud_shield']['punishment'], 'Auto flud warn', 'flud_shield')
                                    except Exception:
                                        pass

                        if server['mod']['bad_words'] != {}:
                            if mod_bad_words(message, server) == True:
                                try:
                                    await punishment_mod(message, server, server['mod']['bad_words']['punishment'], 'Auto bad-words warn', 'bad_words')
                                except Exception:
                                    pass

                        if server['mod']['media_channels'] != {}:
                            if message.channel.id in server['mod']['media_channels']['channels']:
                                if mod_media(message) == True:
                                    try:
                                        await punishment_mod(message, server, server['mod']['media_channels']['punishment'], 'Auto media-channel warn','media_channels')
                                    except Exception:
                                        pass

                        if server['mod']['members_mention'] != {}:
                            if len(message.raw_mentions) >= server['mod']['members_mention']['repetitions']:
                                try:
                                    await punishment_mod(message, server, server['mod']['members_mention']['punishment'], 'Auto mention warn', 'members_mention')
                                except Exception:
                                    pass

                        if server['mod']['roles_mention'] != {}:
                            if len(message.raw_role_mentions) >= server['mod']['roles_mention']['repetitions']:
                                try:
                                    await punishment_mod(message, server, server['mod']['roles_mention']['punishment'], 'Auto mention warn', 'roles_mention')
                                except Exception:
                                    pass

    except Exception:
        pass


    #выполнение команды
    ctx = await bot.get_context(message)
    try:
        ctx.command = bot.get_command(ctx.invoked_with.lower())
        com_f = True
    except:
        com_f = False

    if com_f == True:
        if ctx.command != None:
            await ctx.trigger_typing()
            if ctx.command.name not in server['mod']['off_commands']:
                if functions.cooldown_check(message.author, message.guild, ctx.command.name, 'check') == False:
                    await bot.process_commands(message) # Выполнение команды
                    print(ctx.command.name, 'no_errors', functions.time_end(time.time() - st))

                    if ctx.command.name in server['mod']['cooldowns'].keys():
                        functions.cooldown_check(message.author, message.guild, ctx.command.name, 'add')

                else:
                    if server['mod']['cooldowns'][ctx.command.name]['type'] == 'users':

                        if server['mod']['cooldowns'][ctx.command.name]['users'][str(message.author.id)] - int(time.time()) < 0:
                            tt = 0
                        else:
                            tt = int(server['mod']['cooldowns'][ctx.command.name]['users'][str(message.author.id)] - time.time())

                    elif server['mod']['cooldowns'][ctx.command.name]['type'] == 'server':

                        if server['mod']['cooldowns'][ctx.command.name]['server_c'] - int(time.time()) < 0:
                            tt = 0
                        else:
                            tt = int(server['mod']['cooldowns'][ctx.command.name]['server_c'] - time.time())

                    elif server['mod']['cooldowns'][ctx.command.name]['type'] == 'roles':

                        if server['mod']['cooldowns'][ctx.command.name]['role_c'] - int(time.time()) < 0:
                            tt = 0
                        else:
                            tt = int(server['mod']['cooldowns'][ctx.command.name]['role_c'] - time.time())

                    emb = discord.Embed(title = '⏲️ | Режим ожидания', description = f"Команда `{ctx.command}` может быть активированна повторно только через\n**{functions.time_end(tt)}**", color = server['embed_color'])
                    emb.set_footer(icon_url = ctx.message.author.avatar.url, text = ctx.message.author)
                    await message.channel.send(embed = emb)

    try:
        if message.channel.id == server['emoji']["emoji_channel"]:
            if server['emoji']["emojis"] != []:
                try:
                    for x in server['emoji']["emojis"]:
                        await message.add_reaction(x)
                except Exception:
                    pass
    except Exception:
        pass

    if message.channel.id in server['mod']['part_channels']:
        print(message.content.find('discord.gg/'))
        if message.content.find('discord.gg/') != -1:
            user = functions.user_check(message.author, message.guild)
            try:
                user['cache']['part']
            except:
                user['cache']['part'] = {'all': 0, 'daily': 0, 'day': [None,None]}

            if user['cache']['part']['day'][0] != time.strftime('%j'):
                user['cache']['part']['daily'] = 0

            user['cache']['part']['all'] += 1
            user['cache']['part']['daily'] += 1
            user['cache']['part']['day'][0] = time.strftime('%j')
            user['cache']['part']['day'][1] = int(time.time())

            functions.user_update(message.author.id, message.guild, 'cache', user['cache'])




    if functions.user_check(message.author, message.guild) != False:
        if len(message.content) >= 5:
            retry_after = cooldown.update_rate_limit(message)
            if not retry_after:
                await lvl(message, server)

#============================================конец=================================================================#
bot.run(config.bot_token)
