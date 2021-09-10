import nextcord as discord
from nextcord.ext import tasks, commands
import requests
from PIL import Image, ImageFont, ImageDraw, ImageOps, ImageSequence, ImageFilter
import io
import sys
import random
from random import choice
import asyncio
import time
import pymongo

sys.path.append("..")
from ai3 import functions as funs
import config

client = funs.mongo_c()
db = client.bot
users = db.users
backs = db.bs
servers = db.servers

class settings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        global servers


    @commands.command(usage = '(lvl) (money) (items)', description = 'Добавить награду за уровень.', help = 'Награда за уровень')
    async def add_up(self, ctx, lvl:int, money:int, *item:int):
        global servers
        if funs.roles_check(ctx.author, ctx.guild.id) == False:
            await ctx.send("У вас недостаточно прав для использования этой команды!")
            return
        if lvl < 1:
            await ctx.send("Награда не может выдаваться раньше 1-го уровня")
            return
        if money < 1:
            await ctx.send("Монеты за уровень не могут быть меньше 1-ой!")
            return

        server = servers.find_one({"server": ctx.guild.id})
        a = server['upsend_sett']

        if server['premium'] != True:
            mk = 20
            if len(a['upitems'].keys()) >= 50:
                await ctx.send("Не имея подписки premium, вы не можете назначить больше 50 нагрда за уровень! ")
                return

        if server['premium'] == True:
            mk = 50

        if server['premium'] != True:
            if len(a['upitems'].keys()) >= 100:
                await ctx.send("Нельзя добавить больше 100 наград!")
                return

        items = []
        for i in item:
            try:
                server['items'][str(i)]
                items.append(i)
            except:
                pass

        if len(items) == 0:
            await ctx.send("Не один из предметов не был найден!")
            return
        if len(items) > mk:
            await ctx.send(f"Нельзя выдать больше {mk} предметов за раз!!")
            return

        a['upitems'].update({ str(lvl): {'items': items, 'money': money} })
        servers.update_one( {"server": ctx.guild.id}, {"$set": {'upsend_sett': a}} )
        await ctx.send(f'Награда за уровень {lvl}, была успешно добавленна!')

    @commands.command(usage = '(lvl)', description = 'Удалить награду за уровень.', help = 'Награда за уровень')
    async def delete_up(self,ctx, lvl:int):
        global servers
        if funs.roles_check(ctx.author, ctx.guild.id) == False:
            await ctx.send("У вас недостаточно прав для использования этой команды!")
            return

        server = servers.find_one({"server": ctx.guild.id})

        a = server['upsend_sett']

        try:
            del a['upitems'][str(lvl)]
        except KeyError:
            await ctx.send("Награда за этот уровень не найдена!")
            return

        servers.update_one( {"server": ctx.guild.id}, {"$set": {'upsend_sett': a}} )
        await ctx.send(f'Награда за уровень {lvl} была удалена!')

    @commands.command(usage = '-', description = 'Список наград за уровень.', help = 'Награда за уровень')
    async def uplist(self,ctx):
        global servers
        server = servers.find_one({'server':ctx.guild.id})

        if server['upsend_sett']['upitems'] == {}:
            await ctx.send("Тут пусто! 😯")
            return

        solutions = ['◀', '▶', '❌']
        member = ctx.author
        reaction = 'a'
        numberpage = 1

        keys = []
        for i in list(server['upsend_sett']['upitems'].keys()):
            keys.append(int(i))
        keys = sorted(keys)

        if len(keys) % 6 != 0:
            l = int(len(keys) / 6 + 1)
        else:
            l = int(len(keys) / 6)

        def top_embed(numberpage):
            nonlocal ctx
            nonlocal l

            num1 = 0
            num2 = 0
            page = numberpage
            text = ''

            if numberpage != 1:
                numberpage *= 6
                numberpage -= 6

                if numberpage > 5:
                    numberpage += 1

            if len(keys) <= 6:
                emb = discord.Embed(title = 'Награды за уровени', description = '',color=server['embed_color'])
                for i in keys:
                    ii = []
                    for n in server['upsend_sett']['upitems'][str(i)]['items']:
                        ii.append(server['items'][str(n)]['name'])

                    mr = server['upsend_sett']['upitems'][str(i)]['money']

                    emb.add_field(name = f"Уровень {i}", value = f"Предметы: {', '.join(ii)}\nМонеты: (от {int(mr - mr / 100 * 50)} до {mr})")

            elif len(keys) > 6:
                emb = discord.Embed(title = 'Топ лидеров по уровню', description = '',color=server['embed_color'])
                for i in keys:
                    num1 += 1
                    if num1 >= numberpage and num2 < 5:
                        num2 += 1

                        ii = []
                        for n in server['upsend_sett']['upitems'][str(i)]['items']:
                            ii.append(server['items'][str(n)]['name'])

                        mr = server['upsend_sett']['upitems'][str(i)]['money']

                        emb.add_field(name = f"Уровень {i}", value = f"Предметы: {', '.join(ii)}\nМонеты: (от {int(mr - mr / 100 * 50)} до {mr})")


            emb.set_footer(text=f"Страница {page}/{l}")
            return emb

        msg = await ctx.send(embed = top_embed(numberpage))

        def check( reaction, user):
            nonlocal msg
            return user == ctx.author and str(reaction.emoji) in solutions and str(reaction.message) == str(msg)

        async def rr():
            nonlocal reaction
            nonlocal numberpage
            nonlocal l
            if str(reaction.emoji) == '◀':
                await msg.remove_reaction('◀', member)
                numberpage -= 1
                if numberpage < 1:
                    numberpage = 1

                await msg.edit(embed = top_embed(numberpage))


            elif str(reaction.emoji) == '▶':
                await msg.remove_reaction('▶', member)
                numberpage += 1
                if numberpage > l:
                    numberpage = l

                await msg.edit(embed = top_embed(numberpage))


            elif str(reaction.emoji) == '❌':
                await msg.clear_reactions()
                return

        async def reackt():
            nonlocal reaction
            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=30.0, check = check)
            except asyncio.TimeoutError:
                await msg.clear_reactions()
            else:
                await rr(), await reackt()

        if len(keys) > 6:
            for x in solutions:
                await msg.add_reaction(x)
            await reackt()


    @commands.command(usage = '(#channel)', description = 'Канал оповещения о повышении уровня.', help = 'Награда за уровень')
    async def setupchannel(self,ctx, channel:discord.TextChannel):
        global servers
        if funs.roles_check(ctx.author, ctx.guild.id) == False:
            await ctx.send("У вас недостаточно прав для использования этой команды!")
            return

        server = servers.find_one({'server':ctx.guild.id})
        a = server['upsend_sett']
        a.update({'upsend': channel.id})
        await ctx.send(f"Канал отправки был установлен на <#{channel.id}>")
        servers.update_one( {"server": ctx.guild.id}, {"$set":{"upsend_sett": a}})

    @commands.command(usage = '-', description = 'Отключить оповещение об уровне.', help = 'Награда за уровень')
    async def upoff(self,ctx):
        global servers
        if funs.roles_check(ctx.author, ctx.guild.id) == False:
            await ctx.send("У вас недостаточно прав для использования этой команды!")
            return
        await ctx.send("Канал уведомлений отключён")
        server = servers.find_one({'server':ctx.guild.id})
        a = server['upsend_sett']
        a.update({"upsend": True})
        servers.update_one( {"server": ctx.guild.id}, {"$set":{"upsend_sett": a}})

    @commands.command(usage = '(url) [type]', description = 'Установить своё изображение повышения уровня.', help = 'Награда за уровень')
    async def up_image(self, ctx, url, type = 'png'):
        global servers
        if funs.roles_check(ctx.author, ctx.guild.id) == False:
            await ctx.send("У вас недостаточно прав для использования этой команды!")
            return

        server = servers.find_one({"server": ctx.guild.id})

        try:
            emb1 = discord.Embed(title = "Изображение", color=server['embed_color'])
            emb1.set_image(url = url)
            msg = await ctx.send(embed = emb1)
        except Exception:
            await ctx.send("Требовалось указать __ссылку__ на баннер, повторите настройку ещё раз.")
            return

        try:
            await msg.delete()
        except Exception:
            pass

        server = servers.find_one({'server':ctx.guild.id})
        a = server['upsend_sett']
        a.update({"image_url": url})

        if type == 'png' or type == 'gif':
            a.update({"type":type })

        elif type not in ['png', 'gif']:
            await ctx.send("Тип указан не правильно ")
            return

        await ctx.send(f'Изображение установлено!')

        servers.update_one( {"server": ctx.guild.id}, {"$set":{"upsend_sett": a}})

    @commands.command(usage = '(message)', description = 'Сообщение о повышении.', help = 'Награда за уровень')
    async def up_message(self, ctx, *message):
        global servers
        if funs.roles_check(ctx.author, ctx.guild.id) == False:
            await ctx.send("У вас недостаточно прав для использования этой команды!")
            return

        print(message)

        if message == () or message == 'text':
            await ctx.send(funs.text_replase("text"))
            return

        if len(message) > 1000:
            await ctx.send(f'Сообщение не может быть более 1000-ти символов')
            return

        message = ' '.join(message)

        await ctx.send(funs.text_replase(message, ctx.author))
        await ctx.send(f'Сообщение от ващего имение которое будет выслано при повышении уровня установлено!')

        server = servers.find_one({'server':ctx.guild.id})
        a = server['upsend_sett']
        a.update({"up_message": message})
        servers.update_one( {"server": ctx.guild.id}, {"$set":{"upsend_sett": a}})

    @commands.command(usage = '-', description = 'Удалить приватные войсы.', help = 'Приватные войс-каналы')
    async def clearvoicechannel(self,ctx):
        global servers
        if funs.roles_check(ctx.author, ctx.guild.id) == False:
            await ctx.send("У вас недостаточно прав для использования этой команды!")
            return
        await ctx.send("Настройки приватного войс-канал cброшены")
        server = servers.find_one({'server':ctx.guild.id})
        a = server['voice']
        a.update({'voice_category': None})
        a.update({'voice_channel': None})
        servers.update_one( {"server": ctx.guild.id}, {"$set": {'voice': a}} )

    @commands.command(usage = '[#voice_channel] [category_id]', description = 'Установить приватные войсы.', help = 'Приватные войс-каналы')
    async def setvoicechannel(self,ctx, voicechannel:discord.VoiceChannel = None, category:int = None):
        global servers
        if funs.roles_check(ctx.author, ctx.guild.id) == False:
            await ctx.send("У вас недостаточно прав для использования этой команды!")
            return

        if category == None:
            cat = await ctx.guild.create_category('Приватные войсы')
            category = cat.id
            if voicechannel == None:
                voicechannel = await ctx.guild.create_voice_channel(name=f"+", category=cat)

        c = ctx.guild.get_channel(category)
        if c == None or type(c) != discord.CategoryChannel:
            await ctx.send(f"Требовалось указать id категории, укажите правильный, либо не указывайте этот аргумент. Категория создастся автоматически!")
            return

        await ctx.send(f"Канал создания приватного войс-канала был установлен на <#{voicechannel.id}>")
        server = servers.find_one({'server':ctx.guild.id})
        a = server['voice']
        a.update({'voice_category': category})
        a.update({'voice_channel': voicechannel.id})
        servers.update_one( {"server": ctx.guild.id}, {"$set": {'voice': a}} )

    @commands.command(usage = '[#channel]', description = 'Установить канал для рандомного входа.', help = 'Рандомный войс-канал')
    async def set_random_channel(self,ctx, voicechannel:discord.VoiceChannel = None):
        global servers
        if funs.roles_check(ctx.author, ctx.guild.id) == False:
            await ctx.send("У вас недостаточно прав для использования этой команды!")
            return

        server = servers.find_one({'server':ctx.guild.id})
        a = server['voice']

        if voicechannel == None:
            voicechannel = await ctx.guild.create_voice_channel(name=f"random", category=category)

        await ctx.send(f"Канал с рандомным перекидыванием был установлен на <#{voicechannel.id}>")

        a.update({'randomc_channel': voicechannel.id})
        servers.update_one( {"server": ctx.guild.id}, {"$set": {'voice': a}} )

    # @commands.command(usage = '[#channels]', description = '')
    # async def set_bl_random(self,ctx, *, channels:discord.VoiceChannel):
    #     global servers
    #     if funs.roles_check(ctx.author, ctx.guild.id) == False:
    #         await ctx.send("У вас недостаточно прав для использования этой команды!")
    #         return
    #
    #     server = servers.find_one({'server':ctx.guild.id})
    #     a = server['voice']
    #
    #     bl_c = []
    #     for l in channels:
    #         if l.id not in bl_c:
    #             bl_c.append(l.id)
    #
    #
    #     await ctx.send(f"Канал с рандомным перекидыванием был установлен на <#{voicechannel.id}>")
    #
    #     a.update({'rc_bl_channels': voicechannel.id})
    #     servers.update_one( {"server": ctx.guild.id}, {"$set": {'voice': a}} )

    @commands.command(usage = '[prefix <= 4 characters]', description = 'Изменить префикс.', help = 'Настройка модерации')
    async def it_prefix(self, ctx, arg: str = None):
        if funs.roles_check(ctx.author, ctx.guild.id) == False:
            await ctx.send("У вас недостаточно прав для использования этой команды!")
            return

        server = servers.find_one({"server": ctx.guild.id})
        if arg is None:
            emb = discord.Embed(title = "| Изменение префикса", description = "", color=server['embed_color'])
            emb.add_field(name = "Префикс установлен по умолчанию", value = f"Префикс +")
            servers.update_one({"server": ctx.guild.id}, {"$set": {"prefix": "+"}})
            await ctx.send(embed = emb)

        elif len(str(arg)) > 4:
            emb = discord.Embed(title = "| Изменение префикса", description = "Введите префикс не больше 4-ёх символов", color=server['embed_color'])
            emb.add_field(name = "Пример использования комманды", value = f"{ctx.prefix}prefix (ваш префикс)")
            await ctx.send(embed = emb)

        else:
            servers.update_one({"server": ctx.guild.id}, {"$set": {"prefix": arg}})
            emb = discord.Embed(title = "| Изменение префикса", description = f"Префикс сервера был обновлён на: {arg}", color=server['embed_color'])
            await ctx.send(embed = emb)

    @commands.command(usage = '(#channel)', description = 'Изменить канал оповещения о входе.', help = 'Настройки вход | выход')
    async def set_join_channel(self, ctx, channel:discord.TextChannel):
        global servers
        if funs.roles_check(ctx.author, ctx.guild.id) == False:
            await ctx.send("У вас недостаточно прав для использования этой команды!")
            return
        server = servers.find_one({'server':ctx.guild.id})
        if server['send']['joinsend'] == None or server['send']['joinsend'] == 777777777777777777:
            await ctx.send(f"Приветствие не настроено!")
            return
        await ctx.send(f"Канал приветствия был сменён на <#{channel.id}>")
        a = server['send']
        a.update({"joinsend": channel.id})
        servers.update_one( {"server": ctx.guild.id}, {"$set":{"send": a}} )

    @commands.command(usage = '(#channel)', description = 'Изменить канал оповещения о выходе.', help = 'Настройки вход | выход')
    async def set_leave_channel(self, ctx, channel:discord.TextChannel):
        global servers
        if funs.roles_check(ctx.author, ctx.guild.id) == False:
            await ctx.send("У вас недостаточно прав для использования этой команды!")
            return
        server = servers.find_one({'server':ctx.guild.id})
        if server['send']['leavensend'] == None or server['send']['leavensend'] == 777777777777777777:
            await ctx.send(f"Прощание не настроено!")
            return
        await ctx.send(f"Канал прощания был сменён на <#{channel.id}>")
        a = server['send']
        a.update({"leavensend": channel.id})
        servers.update_one( {"server": ctx.guild.id}, {"$set":{"send": a}} )


    @commands.command(usage = '-', description = 'Создание кастомного оповещения о входе.', help = 'Настройки вход | выход')
    async def set_join(self, ctx):
        if funs.roles_check(ctx.author, ctx.guild.id) == False:
            await ctx.send("У вас недостаточно прав для использования этой команды!")
            return

        member = ctx.author
        server = servers.find_one({"server": member.guild.id})
        user = users.find_one({"userid": member.id})
        name = member.name
        tag = member.discriminator
        reaction = 'a'

        def make_ellipse_mask(size, x0, y0, x1, y1, blur_radius):
            img = Image.new("L", size, color=0)
            draw = ImageDraw.Draw(img)
            draw.ellipse((x0, y0, x1, y1), fill=255)
            return img.filter(ImageFilter.GaussianBlur(radius=blur_radius))

        l = len(name) + len(tag) + 1


        emb = discord.Embed(title = "Настройка входа", description = "", color=server['embed_color'])
        emb.add_field(name = "Канал отправки:", value = f"Укажите [id](https://support.discord.com/hc/ru/articles/206346498-%D0%93%D0%B4%D0%B5-%D0%BC%D0%BD%D0%B5-%D0%BD%D0%B0%D0%B9%D1%82%D0%B8-ID-%D0%BF%D0%BE%D0%BB%D1%8C%D0%B7%D0%BE%D0%B2%D0%B0%D1%82%D0%B5%D0%BB%D1%8F-%D1%81%D0%B5%D1%80%D0%B2%D0%B5%D1%80%D0%B0-%D1%81%D0%BE%D0%BE%D0%B1%D1%89%D0%B5%D0%BD%D0%B8%D1%8F-) канала или `dm` если хотите отправлять сообщение о входе пользователю в личные сообщения.")
        emb.set_footer(text= 'В чат без использования команд введите id')
        message = await ctx.send(embed = emb)

        def embed(channel, avatar_join_url = "не указано", f_el = "не указано", f_we = "не указано", f_na = "не указано", text = "не указано", em = "не указано", position = "не указано"):
            nonlocal server

            emb = discord.Embed(title = "Настройка входа", description = "", color=server['embed_color'])
            if channel == 'dm':
                emb.add_field(name = "Канал отправки:", value = f"Личные сообщения")
            else:
                emb.add_field(name = "Канал отправки:", value = f"<#{channel}>")

            emb.add_field(name = "Ссылка на изображение:", value = f"{avatar_join_url}")
            emb.add_field(name = "Цвет рамки:", value = f"{f_el}")
            emb.add_field(name = "Цвет надписи Welcome:", value = f"{f_we}")
            emb.add_field(name = "Цвет имени:", value = f"{f_na}")
            emb.add_field(name = "Текст:", value = f"{text}", inline = False)
            emb.add_field(name = "Эмбет", value = f"{em}")
            emb.add_field(name = "Тип", value = f"{position}")
            emb.set_footer(text = "У вас есть 2 минуты на настройку")
            if avatar_join_url != "не указано":
                if avatar_join_url != "Укажите в ссылку на изображение":
                    emb.set_image(url = avatar_join_url)
            return emb


        try:
            msg = await self.bot.wait_for('message', timeout=120.0, check=lambda message: message.author == ctx.author and message.channel.id == ctx.channel.id)
        except asyncio.TimeoutError:
            await ctx.send("Время вышло.")
            return
        else:
            try:
                await msg.delete()
            except Exception:
                pass
            if msg.content == 'dm':
                channel = 'dm'

            if msg.content != 'dm':
                try:
                    if self.bot.get_channel(int(msg.content)) != None:
                        await message.edit(embed = embed(msg.content))
                        channel = int(msg.content)

                    else:
                        await ctx.send("Ошибка указания канала")
                        return
                except Exception:
                    await ctx.send("Ошибка указания канала")
                    return

        try:
            await message.edit(embed = embed(channel, "Укажите в ссылку на изображение"))
            msg = await self.bot.wait_for('message', timeout=120.0, check=lambda message: message.author == ctx.author and message.channel.id == ctx.channel.id)
        except asyncio.TimeoutError:
            await ctx.send("Время вышло.")
            return
        else:
            try:
                await msg.delete()
            except Exception:
                pass
            try:
                img = requests.get(f"{msg.content}", stream = True)
                img = Image.open(io.BytesIO(img.content))
                img = img.convert("RGBA")
                img = img.resize((960, 470), Image.ANTIALIAS)

                idraw = ImageDraw.Draw(img)

                url = msg.content
                link = msg.content

                await message.edit(embed = embed(channel, msg.content))

            except Exception:
                await ctx.send("Укажите ссылку")
                return
        if server['premium'] == True:
            try:
                msg2 = await ctx.send("Уточните тип изображения, если вы хотите выводить изображение гифкой, укажите `+`, если статичной картинкой `-`\n\nНе стоит для статичной картинки указывать тип gif")
                msg = await self.bot.wait_for('message', timeout=120.0, check=lambda message: message.author == ctx.author and message.channel.id == ctx.channel.id)
            except asyncio.TimeoutError:
                await ctx.send("Время вышло.")
                return
            else:
                try:
                    await msg.delete()
                    await msg2.delete()
                except Exception:
                    pass
                if msg.content == '+':
                    gif = True
                elif msg.content == '-':
                    gif = False
                else:
                    await ctx.send("Требовалось указать + или -")
                    return

        if server['premium'] == False:
            gif = False


        try:
            await message.edit(embed = embed(channel, link, "Укажите в формате hex (#ffffff) или `none`"))
            msg = await self.bot.wait_for('message', timeout=120.0, check=lambda message: message.author == ctx.author and message.channel.id == ctx.channel.id)
        except asyncio.TimeoutError:
            await ctx.send("Время вышло.")
            return
        else:
            try:
                await msg.delete()
            except Exception:
                pass
            try:
                if msg.content == "none":
                    f_el = None
                else:
                    idraw.ellipse((ap1 - 10, ap2 - 10, ap1 + size[0] + 10, ap2 + size[1] + 10), fill = f"{msg.content}")
                    f_el = msg.content

                await message.edit(embed = embed(channel, link, msg.content))

            except Exception:
                await ctx.send("Укажите цвет формата hex")
                return

        try:
            await message.edit(embed = embed(channel, link, f_el,"Укажите в формате hex (#ffffff) или `none`"))
            msg = await self.bot.wait_for('message', timeout=120.0, check=lambda message: message.author == ctx.author and message.channel.id == ctx.channel.id)
        except asyncio.TimeoutError:
            await ctx.send("Время вышло.")
            return
        else:
            try:
                await msg.delete()
            except Exception:
                pass
            try:
                if msg.content == "none":
                    f_we = None
                else:
                    idraw.text((wp1, wp2), f"W E L C O M E", font = big, fill = f"{msg.content}")
                    f_we = msg.content

                await message.edit(embed = embed(channel, link, f_el, f_we))

            except Exception:
                await ctx.send("Укажите цвет формата hex")
                return

        try:
            await message.edit(embed = embed(channel, link, f_el, f_we, "Укажите в формате hex (#ffffff) или `none`"))
            msg = await self.bot.wait_for('message', timeout=120.0, check=lambda message: message.author == ctx.author and message.channel.id == ctx.channel.id)
        except asyncio.TimeoutError:
            await ctx.send("Время вышло.")
            return
        else:
            try:
                await msg.delete()
            except Exception:
                pass
            try:
                if msg.content == "none":
                    f_na = None
                else:
                    idraw.text((tp1, tp2), f"{name}#{tag}", font = headline, fill = f"{msg.content}")
                    f_na = msg.content

                await message.edit(embed = embed(channel, link, f_el, f_we, f_na))

            except Exception:
                await ctx.send("Укажите цвет формата hex")
                return

        try:
            await message.edit(embed = embed(channel, link, f_el, f_we, f_na, "Введите сообщение входа"))
            msg2 = await ctx.send(funs.text_replase("text") + "\nУкажите `none` если хотите оставить:\n`Goodbye {member.name.tag}`")
            msg = await self.bot.wait_for('message', timeout=120.0, check=lambda message: message.author == ctx.author and message.channel.id == ctx.channel.id)
        except asyncio.TimeoutError:
            await ctx.send("Время вышло.")
            return
        else:
            try:
                await msg.delete()
                await msg2.delete()
            except Exception:
                pass
            if msg.content == 'none':
                w_text = None
            else:
                w_text = msg.content

            await message.edit(embed = embed(channel, link, f_el, f_we, f_na, msg.content))


        try:
            await message.edit(embed = embed(channel, link, f_el, f_we, f_na, w_text, "Использовать эмбет при отправке?"))
            msg2 = await ctx.send("Укажите `+` или `-`")
            msg = await self.bot.wait_for('message', timeout=120.0, check=lambda message: message.author == ctx.author and message.channel.id == ctx.channel.id)
        except asyncio.TimeoutError:
            await ctx.send("Время вышло.")
            return
        else:
            try:
                await msg.delete()
                await msg2.delete()
            except Exception:
                pass
            if msg.content == '+':
                emb = True
            elif msg.content == '-':
                emb = False
            else:
                await ctx.send("Требовалось указать + или -")
                return

        try:
            await message.edit(embed = embed(channel, link, f_el, f_we, f_na, w_text, emb, "Укажите тип информации (0 или 1)\n0 - центральное расположение\n1 - расположение относительно лево"))
            msg = await self.bot.wait_for('message', timeout=120.0, check=lambda message: message.author == ctx.author and message.channel.id == ctx.channel.id)
        except asyncio.TimeoutError:
            await ctx.send("Время вышло.")
            return
        else:
            try:
                await msg.delete()
            except Exception:
                pass
            if msg.content == '0':
                position = 0
            elif msg.content == '1':
                position = 1
            else:
                await ctx.send("Требовалось указать 1 или 0")
                return

        await message.edit(embed = embed(channel, link, f_el, f_we, f_na, w_text, emb, position))


        url = link
        user = users.find_one({"userid": ctx.author.id})

        if gif == False:

            response = requests.get(url, stream = True)
            response = Image.open(io.BytesIO(response.content))
            response = response.convert("RGBA")
            alpha = response.resize((960, 470), Image.ANTIALIAS) # улучшение качества

        if gif == True:

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

        if position == 0:

            wp1 = 245          #x
            wp2 = 275          #y

            tp2 = 400
            tp1 = int(400 - l * number) #текст

            size = (250,250)        #y
            ap1 = int(960 / 2 - size[0] / 2)         #x
            ap2 = 30          #y

        if position == 1:

            wp1 = 300          #x
            wp2 = 170          #y

            tp2 = 280 #y
            tp1 = 305 #текст имени  x

            size = (250,250)
            ap1 = 20         #x
            ap2 = 115          #y

        if f_we == None:
            idraw.text((wp1, wp2), f"WELCOME", font = big)
        else:
            idraw.text((wp1, wp2), f"WELCOME", font = big, fill = f"{f_we}")

        if f_na == None:
            idraw.text((tp1, tp2), f"{name}#{tag}", font = headline)
        else:
            idraw.text((tp1, tp2), f"{name}#{tag}", font = headline,fill = f"{f_na}")

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
        if f_el == None:
            mask_image = make_ellipse_mask((960, 470), ap1 - 10, ap2 - 10, ap1 + size[0] + 10, ap2 + size[1] + 10, 1)
            alpha = Image.composite(overlay_image, alpha, mask_image)
        else:
            idraw.ellipse((ap1 - 10, ap2 - 10, ap1 + size[0] + 10, ap2 + size[1] + 10), fill = f"{f_el}")

        #аватарка
        bg_img = alpha
        fg_img = im
        p = trans_paste(fg_img, bg_img, 1.0, (ap1, ap2, ap1 + size[0], ap2 + size[0]))

        if w_text == None:
            text = f"Welcome {name}#{tag} to {member.guild.name}"
        else:
            text = w_text
            text = funs.text_replase(text, member)

        if gif == False:


            image = alpha
            output = BytesIO()
            image.save(output, 'png')
            image_pix=BytesIO(output.getvalue())

            file = discord.File(fp = image_pix, filename="welcome_card.png")
            ul = 'png'

        if gif == True:
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
            msg = await ctx.channel.send(f"{text}", file = file)
        except Exception:
            pass

        try:
            os.remove(f'welcome_card.{ul}')
        except Exception:
            pass


        solutions = ['✅', '❌']

        def check( reaction, user):
            nonlocal msg
            return user == ctx.author and str(reaction.emoji) in solutions and str(reaction.message) == str(msg)

        async def rr():
            nonlocal reaction
            nonlocal channel, link, f_el, f_we, f_na, w_text, emb, position, gif

            if str(reaction.emoji) == '✅':
                try:
                    await msg.remove_reaction('✅', member), await msg.clear_reactions()
                except Exception:
                    pass

                a = server['welcome']
                a.update({"el_fill": f_el, "wel_text": w_text, "nam_fill": f_na, "wel_fill": f_we, 'emb': emb, 'join_type': gif})
                servers.update_one( {"server": member.guild.id}, {"$set":{"welcome": a }} )

                a = server['send']
                a.update({"joinsend": channel, "avatar_join_url": link, "join_position_avatar": position})
                servers.update_one( {"server": member.guild.id}, {"$set":{"send": a}} )

                await ctx.send("Вход настроен")
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

        for x in solutions:
            await msg.add_reaction(x)

        await reackt()

    @commands.command(usage = '-', description = 'Отключение оповещения о входе.', help = 'Настройки вход | выход')
    async def join_off(self, ctx):
        global servers
        if funs.roles_check(ctx.author, ctx.guild.id) == False:
            await ctx.send("У вас недостаточно прав для использования этой команды!")
            return
        await ctx.send(f"Канал оповещений о входе был отключён.")
        servers.update_one( {"server": ctx.guild.id}, {"$set":{'send':{"joinsend": None}}} )

    @commands.command(usage = '-', description = 'Отключение оповещения о выходе.', help = 'Настройки вход | выход')
    async def leave_off(self, ctx):
        global servers
        if funs.roles_check(ctx.author, ctx.guild.id) == False:
            await ctx.send("У вас недостаточно прав для использования этой команды!")
            return
        await ctx.send(f"Канал оповещений о выходе был отключён.")
        servers.update_one( {"server": ctx.guild.id}, {"$set":{'send':{"leavesend": None}}} )

    @commands.command(usage = '-', description = 'Создание кастомного оповещения о выходе.', help = 'Настройки вход | выход')
    async def set_leave(self, ctx):
        if funs.roles_check(ctx.author, ctx.guild.id) == False:
            await ctx.send("У вас недостаточно прав для использования этой команды!")
            return

        member = ctx.author
        server = servers.find_one({"server": member.guild.id})
        user = users.find_one({"userid": member.id})
        name = member.name
        tag = member.discriminator
        reaction = 'a'

        def make_ellipse_mask(size, x0, y0, x1, y1, blur_radius):
            img = Image.new("L", size, color=0)
            draw = ImageDraw.Draw(img)
            draw.ellipse((x0, y0, x1, y1), fill=255)
            return img.filter(ImageFilter.GaussianBlur(radius=blur_radius))

        l = len(name) + len(tag) + 1


        emb = discord.Embed(title = "Настройка выхода", description = "", color=server['embed_color'])
        emb.add_field(name = "Канал отправки:", value = f"Укажите [id](https://support.discord.com/hc/ru/articles/206346498-%D0%93%D0%B4%D0%B5-%D0%BC%D0%BD%D0%B5-%D0%BD%D0%B0%D0%B9%D1%82%D0%B8-ID-%D0%BF%D0%BE%D0%BB%D1%8C%D0%B7%D0%BE%D0%B2%D0%B0%D1%82%D0%B5%D0%BB%D1%8F-%D1%81%D0%B5%D1%80%D0%B2%D0%B5%D1%80%D0%B0-%D1%81%D0%BE%D0%BE%D0%B1%D1%89%D0%B5%D0%BD%D0%B8%D1%8F-) канала.")
        emb.set_footer(text= 'В чат без использования команд введите id')
        message = await ctx.send(embed = emb)

        def embed(channel, avatar_join_url = "не указано", f_el = "не указано", f_we = "не указано", f_na = "не указано", text = "не указано", em = "не указано", position = "не указано"):
            nonlocal server

            emb = discord.Embed(title = "Настройка выхода", description = "", color=server['embed_color'])

            emb.add_field(name = "Канал отправки:", value = f"<#{channel}>")

            emb.add_field(name = "Ссылка на изображение:", value = f"{avatar_join_url}")
            emb.add_field(name = "Цвет рамки:", value = f"{f_el}")
            emb.add_field(name = "Цвет надписи Goodbye:", value = f"{f_we}")
            emb.add_field(name = "Цвет имени:", value = f"{f_na}")
            emb.add_field(name = "Текст:", value = f"{text}", inline = False)
            emb.add_field(name = "Эмбет", value = f"{em}")
            emb.add_field(name = "Тип", value = f"{position}")
            emb.set_footer(text = "У вас есть 2 минуты на настройку")
            if avatar_join_url != "не указано":
                if avatar_join_url != "Укажите в ссылку на изображение":
                    emb.set_image(url = avatar_join_url)
            return emb


        try:
            msg = await self.bot.wait_for('message', timeout=120.0, check=lambda message: message.author == ctx.author and message.channel.id == ctx.channel.id)
        except asyncio.TimeoutError:
            await ctx.send("Время вышло.")
            return
        else:
            try:
                await msg.delete()
            except Exception:
                pass

            try:
                if self.bot.get_channel(int(msg.content)) != None:
                    await message.edit(embed = embed(msg.content))
                    channel = int(msg.content)

                else:
                    await ctx.send("Ошибка указания канала")
                    return
            except Exception:
                await ctx.send("Ошибка указания канала")
                return

        try:
            await message.edit(embed = embed(channel, "Укажите в ссылку на изображение"))
            msg = await self.bot.wait_for('message', timeout=120.0, check=lambda message: message.author == ctx.author and message.channel.id == ctx.channel.id)
        except asyncio.TimeoutError:
            await ctx.send("Время вышло.")
            return
        else:
            try:
                await msg.delete()
            except Exception:
                pass
            try:
                img = requests.get(f"{msg.content}", stream = True)
                img = Image.open(io.BytesIO(img.content))
                img = img.convert("RGBA")
                img = img.resize((960, 470), Image.ANTIALIAS)

                idraw = ImageDraw.Draw(img)

                url = msg.content
                link = msg.content

                await message.edit(embed = embed(channel, msg.content))

            except Exception:
                await ctx.send("Укажите ссылку")
                return
        if server['premium'] == True:
            try:
                msg2 = await ctx.send("Уточните тип изображения, если вы хотите выводить изображение гифкой, укажите `+`, если статичной картинкой `-`\n\nНе стоит для статичной картинки указывать тип gif")
                msg = await self.bot.wait_for('message', timeout=120.0, check=lambda message: message.author == ctx.author and message.channel.id == ctx.channel.id)
            except asyncio.TimeoutError:
                await ctx.send("Время вышло.")
                return
            else:
                try:
                    await msg.delete()
                    await msg2.delete()
                except Exception:
                    pass
                if msg.content == '+':
                    gif = True
                elif msg.content == '-':
                    gif = False
                else:
                    await ctx.send("Требовалось указать + или -")
                    return

        if server['premium'] == False:
            gif = False


        try:
            await message.edit(embed = embed(channel, link, "Укажите в формате hex (#ffffff) или `none`"))
            msg = await self.bot.wait_for('message', timeout=120.0, check=lambda message: message.author == ctx.author and message.channel.id == ctx.channel.id)
        except asyncio.TimeoutError:
            await ctx.send("Время вышло.")
            return
        else:
            try:
                await msg.delete()
            except Exception:
                pass
            try:
                if msg.content == "none":
                    f_el = None
                else:
                    idraw.ellipse((ap1 - 10, ap2 - 10, ap1 + size[0] + 10, ap2 + size[1] + 10), fill = f"{msg.content}")
                    f_el = msg.content

                await message.edit(embed = embed(channel, link, msg.content))

            except Exception:
                await ctx.send("Укажите цвет формата hex")
                return

        try:
            await message.edit(embed = embed(channel, link, f_el,"Укажите в формате hex (#ffffff) или `none`"))
            msg = await self.bot.wait_for('message', timeout=120.0, check=lambda message: message.author == ctx.author and message.channel.id == ctx.channel.id)
        except asyncio.TimeoutError:
            await ctx.send("Время вышло.")
            return
        else:
            try:
                await msg.delete()
            except Exception:
                pass
            try:
                if msg.content == "none":
                    f_we = None
                else:
                    idraw.text((wp1, wp2), f"W E L C O M E", font = big, fill = f"{msg.content}")
                    f_we = msg.content

                await message.edit(embed = embed(channel, link, f_el, f_we))

            except Exception:
                await ctx.send("Укажите цвет формата hex")
                return

        try:
            await message.edit(embed = embed(channel, link, f_el, f_we, "Укажите в формате hex (#ffffff) или `none`"))
            msg = await self.bot.wait_for('message', timeout=120.0, check=lambda message: message.author == ctx.author and message.channel.id == ctx.channel.id)
        except asyncio.TimeoutError:
            await ctx.send("Время вышло.")
            return
        else:
            try:
                await msg.delete()
            except Exception:
                pass
            try:
                if msg.content == "none":
                    f_na = None
                else:
                    idraw.text((tp1, tp2), f"{name}#{tag}", font = headline, fill = f"{msg.content}")
                    f_na = msg.content

                await message.edit(embed = embed(channel, link, f_el, f_we, f_na))

            except Exception:
                await ctx.send("Укажите цвет формата hex")
                return

        try:
            await message.edit(embed = embed(channel, link, f_el, f_we, f_na, "Введите сообщение входа"))
            msg2 = await ctx.send(funs.text_replase("text") + "\nУкажите `none` если хотите оставить:\n`Welcome {member.name.tag} to {guild.name}`")
            msg = await self.bot.wait_for('message', timeout=120.0, check=lambda message: message.author == ctx.author and message.channel.id == ctx.channel.id)
        except asyncio.TimeoutError:
            await ctx.send("Время вышло.")
            return
        else:
            try:
                await msg.delete()
                await msg2.delete()
            except Exception:
                pass
            if msg.content == 'none':
                w_text = None
            else:
                w_text = msg.content

            await message.edit(embed = embed(channel, link, f_el, f_we, f_na, msg.content))


        try:
            await message.edit(embed = embed(channel, link, f_el, f_we, f_na, w_text, "Использовать эмбет при отправке?"))
            msg2 = await ctx.send("Укажите `+` или `-`")
            msg = await self.bot.wait_for('message', timeout=120.0, check=lambda message: message.author == ctx.author and message.channel.id == ctx.channel.id)
        except asyncio.TimeoutError:
            await ctx.send("Время вышло.")
            return
        else:
            try:
                await msg.delete()
                await msg2.delete()
            except Exception:
                pass
            if msg.content == '+':
                emb = True
            elif msg.content == '-':
                emb = False
            else:
                await ctx.send("Требовалось указать + или -")
                return

        try:
            await message.edit(embed = embed(channel, link, f_el, f_we, f_na, w_text, emb, "Укажите тип информации (0 или 1)\n0 - центральное расположение\n1 - расположение относительно лево"))
            msg = await self.bot.wait_for('message', timeout=120.0, check=lambda message: message.author == ctx.author and message.channel.id == ctx.channel.id)
        except asyncio.TimeoutError:
            await ctx.send("Время вышло.")
            return
        else:
            try:
                await msg.delete()
            except Exception:
                pass
            if msg.content == '0':
                position = 0
            elif msg.content == '1':
                position = 1
            else:
                await ctx.send("Требовалось указать 1 или 0")
                return

        await message.edit(embed = embed(channel, link, f_el, f_we, f_na, w_text, emb, position))


        url = link
        user = users.find_one({"userid": ctx.author.id})

        if gif == False:

            response = requests.get(url, stream = True)
            response = Image.open(io.BytesIO(response.content))
            response = response.convert("RGBA")
            alpha = response.resize((960, 470), Image.ANTIALIAS) # улучшение качества

        if gif == True:

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

        if position == 0:

            wp1 = 245          #x
            wp2 = 275          #y

            tp2 = 400
            tp1 = int(400 - l * number) #текст

            size = (250,250)        #y
            ap1 = int(960 / 2 - size[0] / 2)         #x
            ap2 = 30          #y

        if position == 1:

            wp1 = 300          #x
            wp2 = 170          #y

            tp2 = 280 #y
            tp1 = 305 #текст имени  x

            size = (250,250)
            ap1 = 20         #x
            ap2 = 115          #y

        if f_we == None:
            idraw.text((wp1, wp2), f"Goodbye", font = big)
        else:
            idraw.text((wp1, wp2), f"Goodbye", font = big, fill = f"{f_we}")

        if f_na == None:
            idraw.text((tp1, tp2), f"{name}#{tag}", font = headline)
        else:
            idraw.text((tp1, tp2), f"{name}#{tag}", font = headline,fill = f"{f_na}")

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
        if f_el == None:
            mask_image = make_ellipse_mask((960, 470), ap1 - 10, ap2 - 10, ap1 + size[0] + 10, ap2 + size[1] + 10, 1)
            alpha = Image.composite(overlay_image, alpha, mask_image)
        else:
            idraw.ellipse((ap1 - 10, ap2 - 10, ap1 + size[0] + 10, ap2 + size[1] + 10), fill = f"{f_el}")

        #аватарка
        bg_img = alpha
        fg_img = im
        p = trans_paste(fg_img, bg_img, 1.0, (ap1, ap2, ap1 + size[0], ap2 + size[0]))

        if w_text == None:
            text = f"Goodbye {name}#{tag}"
        else:
            text = w_text
            text = funs.text_replase(text, member)

        if gif == False:


            image = alpha
            output = BytesIO()
            image.save(output, 'png')
            image_pix=BytesIO(output.getvalue())

            file = discord.File(fp = image_pix, filename="goodbye_card.png")
            ul = 'png'

        if gif == True:
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
            msg = await ctx.channel.send(f"{text}", file = file)
        except Exception:
            pass

        try:
            os.remove(f'goodbye_card.{ul}')
        except Exception:
            pass


        solutions = ['✅', '❌']

        def check( reaction, user):
            nonlocal msg
            return user == ctx.author and str(reaction.emoji) in solutions and str(reaction.message) == str(msg)

        async def rr():
            nonlocal reaction
            nonlocal channel, link, f_el, f_we, f_na, w_text, emb, position, gif

            if str(reaction.emoji) == '✅':
                try:
                    await msg.remove_reaction('✅', member), await msg.clear_reactions()
                except Exception:
                    pass

                a = server['goodbye']
                a.update({"el_fill_l": f_el, "lea_text": w_text, "nam_fill_l": f_na, "wel_fill_l": f_we, 'emb': emb, 'leave_type': gif})
                servers.update_one( {"server": member.guild.id}, {"$set":{"goodbye": a }} )

                a = server['send']
                a.update({"leavensend": channel, "avatar_leave_url": link, "leave_position_avatar": position})
                servers.update_one( {"server": member.guild.id}, {"$set":{"send": a}} )

                await ctx.send("Выход настроен")
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

        for x in solutions:
            await msg.add_reaction(x)

        await reackt()

    @commands.command(usage = '(@role)', description = 'Установка роли за мьют.', help = 'Настройка модерации')
    async def setmuterole(self, ctx, role:discord.Role):
        global servers
        if funs.roles_check(ctx.author, ctx.guild.id) == False:
            await ctx.send("У вас недостаточно прав для использования этой команды!")
            return
        server = servers.find_one({'server':ctx.guild.id})
        await ctx.send(f"Роль мьюта на сервере установлена ({role.name})\nБот не настраивает каналы на отключение прав, но при этом удаляет сообщени от пользователей с этой ролью")
        a = server['mod']
        a.update({'muterole': role.id})
        servers.update_one( {"server": ctx.guild.id}, {"$set": {'mod': a}} )

    @commands.command(usage = '-', description = 'Редактирования наказания за варн.', help = 'Настройка модерации')
    async def set_punishment(self, ctx):
        global servers
        if funs.roles_check(ctx.author, ctx.guild.id) == False:
            await ctx.send("У вас недостаточно прав для использования этой команды!")
            return
        server = servers.find_one({'server':ctx.guild.id})
        try:
            await ctx.send('Укажите номер варна наказание за которое будет настроено.\nВ чат без использования команд введите число.')
            msg = await self.bot.wait_for('message', timeout=60.0, check=lambda message: message.author == ctx.author and message.channel.id == ctx.channel.id)
        except asyncio.TimeoutError:
            await ctx.send("Время вышло.")
            return
        else:
            try:
                warnid = int(msg.content)
                if warnid == 0:
                    await ctx.send('Укажите чиcло больше 0-ля. Ошибка...')
                    return
                if warnid > 20:
                    await ctx.send('Укажите чиcло меньше 21. Ошибка...')
                    return
            except Exception:
                await ctx.send('Укажите __число__. Ошибка...')
                return
        try:
            await ctx.send(f'Укажите наказание за варн #{warnid}\nВ чат без использования команд введите число соответствуещее наказанию.\n0 - ничего\n1 - мьют\n2 - кик\n3 - бан\n4 - выдача роли\n5 - удаление ролей\n6 - отправка сообщения')
            msg = await self.bot.wait_for('message', timeout=60.0, check=lambda message: message.author == ctx.author and message.channel.id == ctx.channel.id)
        except asyncio.TimeoutError:
            await ctx.send("Время вышло.")
            return
        else:
            try:
                punishment = int(msg.content)
            except Exception:
                await ctx.send('Укажите __число__. Ошибка...')
                return

        if punishment == 0:
            await ctx.send(f"Варн {warnid} настроен на ничего. По умолчанию у всех варнов стоит ничего. ")
            return

        elif punishment == 1:
            punishments_warns = server['mod']['punishments_warns']
            try:
                await ctx.send(f'Укажите время мьюта за варн #{warnid}\nВ чат без использования команд введите время, Формат: 10m `(s/m/h/d)`')
                msg = await self.bot.wait_for('message', timeout=60.0, check=lambda message: message.author == ctx.author and message.channel.id == ctx.channel.id)
            except asyncio.TimeoutError:
                await ctx.send("Время вышло.")
                return
            else:
                try:
                    punishment = int(msg.content[:-1])
                except Exception:
                    await ctx.send('Укажите __число__. Ошибка...')
                    return


                if msg.content.endswith("s"):
                    tim = int(msg.content[:-1])

                elif msg.content.endswith("m"):
                    tim = int(msg.content[:-1])*60

                elif msg.content.endswith("h"):
                    tim = int(msg.content[:-1])*3600

                elif msg.content.endswith("d"):
                    tim = int(msg.content[:-1])*86400

                else:
                    await ctx.send('Ошибка указания времени.')
                    return


            punishments_warns.update({str(warnid): {'punishment': 1, "time": tim} })
            a = server['mod']
            a.update({'punishments_warns': punishments_warns})
            servers.update_one({'server':ctx.guild.id},{'$set': {'mod': a }})
            await ctx.send(f"Варн {warnid} настроен на мьют. При получении варна, человек получит мьют на `{msg.content}`")

        elif punishment == 2:
            punishments_warns = server['mod']['punishments_warns']
            punishments_warns.update({str(warnid): {'punishment': 2} })
            a = server['mod']
            a.update({'punishments_warns': punishments_warns})
            servers.update_one({'server':ctx.guild.id},{'$set': {'mod': a }})
            await ctx.send(f"Варн {warnid} настроен на кик.")

        elif punishment == 3:
            punishments_warns = server['mod']['punishments_warns']
            punishments_warns.update({str(warnid): {'punishment': 3} })
            a = server['mod']
            a.update({'punishments_warns': punishments_warns})
            servers.update_one({'server':ctx.guild.id},{'$set': {'mod': a }})
            await ctx.send(f"Варн {warnid} настроен на бан.")

        elif punishment == 4:
            punishments_warns = server['mod']['punishments_warns']
            try:
                await ctx.send(f'Укажите id роли которая будет выдаваться за варн #{warnid}')
                msg = await self.bot.wait_for('message', timeout=60.0, check=lambda message: message.author == ctx.author and message.channel.id == ctx.channel.id)
            except asyncio.TimeoutError:
                await ctx.send("Время вышло.")
                return
            else:
                try:
                    idrole = int(msg.content)
                except Exception:
                    await ctx.send('Укажите __id__. Ошибка...')
                    return

            punishments_warns.update({str(warnid): {'punishment': 4, 'role': idrole} })
            a = server['mod']
            a.update({'punishments_warns': punishments_warns})
            servers.update_one({'server':ctx.guild.id},{'$set': {'mod': a }})
            await ctx.send(f"Варн {warnid} настроен на выдачу роли.")

        elif punishment == 5:
            punishments_warns = server['mod']['punishments_warns']
            try:
                await ctx.send(f'Укажите id роли которая будет удаляться за варн #{warnid}')
                msg = await self.bot.wait_for('message', timeout=60.0, check=lambda message: message.author == ctx.author and message.channel.id == ctx.channel.id)
            except asyncio.TimeoutError:
                await ctx.send("Время вышло.")
                return
            else:
                try:
                    idrole = int(msg.content)
                except Exception:
                    await ctx.send('Укажите __id__. Ошибка...')
                    return

            punishments_warns.update({str(warnid): {'punishment': 5, 'role': idrole} })
            a = server['mod']
            a.update({'punishments_warns': punishments_warns})
            servers.update_one({'server':ctx.guild.id},{'$set': {'mod': a }})
            await ctx.send(f"Варн {warnid} настроен на удаление роли.")

        elif punishment == 6:
            punishments_warns = server['mod']['punishments_warns']
            try:
                await ctx.send(f'Укажите сообщение выводимое за варн #{warnid}')
                msg = await self.bot.wait_for('message', timeout=60.0, check=lambda message: message.author == ctx.author and message.channel.id == ctx.channel.id)
            except asyncio.TimeoutError:
                await ctx.send("Время вышло.")
                return
            else:
                message = msg.content
                if len(message) > 1500:
                    await ctx.send('Сообщение не может быть длинной более 1.5к символов!')
                    return

            punishments_warns.update({str(warnid): {'punishment': 6, 'message': message} })
            a = server['mod']
            a.update({'punishments_warns': punishments_warns})
            servers.update_one({'server':ctx.guild.id},{'$set': {'mod': a }})
            await ctx.send(f"Варн {warnid} настроен на вывод сообщения.")

    @commands.command(usage = '[page]', description = 'Список наказаний за варны.', help = 'Настройка модерации')
    async def punishment_list(self, ctx, numberpage:int = 1):
        server = servers.find_one({'server':ctx.guild.id})
        if server['mod']['punishments_warns'] == {}:
            text = 'Тут ничего нет'
        else:
            d = server['mod']['punishments_warns']
            list_keys = list(sorted(d.keys(),key=int, reverse=False))

            num1 = 0
            num2 = 0
            text = ''
            page = 1

            if len(d) % 10 != 0:
                l = int(len(d) / 10 + 1)
            else:
                l = int(len(d) / 10)

            if numberpage > l :
                await ctx.send("Такой страницы нет!")
                return

            if numberpage != 1:
                page = numberpage
                numberpage *= 10
                numberpage -= 10

                if numberpage > 9:
                    numberpage += 1


            if len(server['mod']['punishments_warns']) <= 10:
                text = ''
                for i in list_keys:
                    num1 += 1
                    if d[i]['punishment'] == 1:
                        text += f"#{i} мьют на {funs.time_end(d[i]['time'])}\n"
                    if d[i]['punishment'] == 2:
                        text += f"#{i} кик\n"
                    if d[i]['punishment'] == 3:
                        text += f"#{i} бан\n"
                    if d[i]['punishment'] == 4:
                        text += f"#{i} выдача роли <@&{d[i]['role']}>\n"
                    if d[i]['punishment'] == 5:
                        text += f"#{i} снятие роли <@&{d[i]['role']}>\n"
                    if d[i]['punishment'] == 5:
                        text += f"#{i} сообщение: {d[i]['message']}\n"
                    if d[i]['punishment'] == 0:
                        text += f"#{i} ничего\n"

            elif len(server['mod']['punishments_warns']) > 10:
                for i in list_keys:

                    num1 += 1

                    if num1 >= numberpage and num2 < 10:
                        num2 += 1

                        if d[i]['punishment'] == 1:
                            text += f"#{i} мьют на {funs.time_end(d[i]['time'])}\n"
                        if d[i]['punishment'] == 2:
                            text += f"#{i} кик\n"
                        if d[i]['punishment'] == 3:
                            text += f"#{i} бан\n"
                        if d[i]['punishment'] == 4:
                            text += f"#{i} выдача роли <@&{d[i]['role']}>\n"
                        if d[i]['punishment'] == 5:
                            text += f"#{i} снятие роли <@&{d[i]['role']}>\n"
                        if d[i]['punishment'] == 5:
                            text += f"#{i} сообщение: {d[i]['message']}\n"
                        if d[i]['punishment'] == 0:
                            text += f"#{i} ничего\n"

            emb = discord.Embed(title = 'Наказания', description = text, color=server['embed_color'])
            emb.set_footer(text=f"Страница {page}/{l}")
            await ctx.send(embed = emb)


    @commands.command(usage = '[code]', description = 'Установка межсерверного чата.', help = 'Межсервер')
    async def set_globalchannel(self,ctx, code:int = 0):
        if funs.roles_check(ctx.author, ctx.guild.id) == False:
            await ctx.send("У вас недостаточно прав для использования этой команды!")
            return
        webhook = await ctx.channel.create_webhook(name="Межсерверный чат")
        if code != 0:
            servers.update_one({'server':ctx.guild.id},{'$set':{'globalchat':{'channel':ctx.channel.id,'webhook':webhook.id}} })
            servers.update_one({'server':ctx.guild.id},{'$set': {'global_code': code } })
        else:
            servers.update_one({'server':ctx.guild.id},{'$set':{'globalchat':{'channel':ctx.channel.id,'webhook':webhook.id}}})
        await ctx.send(f'Межсерверный чат настроен на сервере "{ctx.guild.name}"')

    @commands.command(usage = '-', description = 'Удалить межсерверный чат.', help = 'Межсервер')
    async def delete_globalchannel(self, ctx):
        global servers
        if funs.roles_check(ctx.author, ctx.guild.id) == False:
            await ctx.send("У вас недостаточно прав для использования этой команды!")
            return
        server = servers.find_one({'server':ctx.guild.id})
        channel = self.bot.get_channel(server['globalchat']['channel'])
        webhook = discord.utils.get(await channel.webhooks(), id=server['globalchat']['webhook'])
        await webhook.delete()

        servers.update_one({'server':ctx.guild.id},{'$set':{'globalchat':{'channel':None,'webhook':None}}})
        try:
            servers.update_one({'server':ctx.guild.id},{'$set': {'global_code': None } })
        except:
            pass
        await ctx.send(f'Межсерверный чат удалён')

    @commands.command(usage = '-', description = 'Список игнорируемых каналов.', help = 'Настройка модерации')
    async def bchannels(self, ctx):
        global servers
        server = servers.find_one({'server':ctx.guild.id})
        a = server['mod']['black_channels']
        text = ''
        for i in a:
            c = self.bot.get_channel(i)
            text = text + f', {c.mention}'
        message = await ctx.send(embed = discord.Embed(title="ЧС каналов",description=text, color=server['embed_color']))

    @commands.command(usage = '(#channel)', description = 'Добавить игнорируемый канал.', help = 'Настройка модерации')
    async def bchannels_add(self, ctx, channel:discord.TextChannel):
        global servers
        if funs.roles_check(ctx.author, ctx.guild.id) == False:
            await ctx.send("У вас недостаточно прав для использования этой команды!")
            return
        server = servers.find_one({'server':ctx.guild.id})
        a = server['mod']['black_channels']
        a.append(channel.id)

        b = server['mod']
        b.update({'black_channels': a})
        servers.update_one({'server':ctx.guild.id},{'$set': {'mod': b }})
        await ctx.send(f'Канал {channel.mention} добавлен в чс бота.')

    @commands.command(usage = '(#channel)', description = 'Удалить игнорируемый канал.', help = 'Настройка модерации')
    async def bchannels_delete(self, ctx, channel:discord.TextChannel):
        global servers
        if funs.roles_check(ctx.author, ctx.guild.id) == False:
            await ctx.send("У вас недостаточно прав для использования этой команды!")
            return
        server = servers.find_one({'server':ctx.guild.id})
        a = server['mod']['black_channels'].copy()
        try:
            a.remove(channel.id)
        except Exception:
            await ctx.send('Канал не добавлен в чс.')
            return

        b = server['mod']
        b.update({'black_channels': a})
        servers.update_one({'server':ctx.guild.id},{'$set': {'mod': b }})
        await ctx.send(f'Канал {channel.mention} удалён из чс бота.')

    @commands.command(usage = '-', description = 'Информация о ролях по реакции.', help = 'Роли по реакциям')
    async def rr(self, ctx):
        server = servers.find_one({"server": ctx.guild.id})
        hh = '[id сообщения](https://support.discord.com/hc/ru/articles/206346498-%D0%93%D0%B4%D0%B5-%D0%BC%D0%BD%D0%B5-%D0%BD%D0%B0%D0%B9%D1%82%D0%B8-ID-%D0%BF%D0%BE%D0%BB%D1%8C%D0%B7%D0%BE%D0%B2%D0%B0%D1%82%D0%B5%D0%BB%D1%8F-%D1%81%D0%B5%D1%80%D0%B2%D0%B5%D1%80%D0%B0-%D1%81%D0%BE%D0%BE%D0%B1%D1%89%D0%B5%D0%BD%D0%B8%D1%8F-)'
        if ctx.invoked_subcommand is None:

            emb = discord.Embed(title = 'Формат создания', description = f'`{ctx.prefix}rr_set (message-id) (emoji) (function) (roles)`\n(message-id) - укажите {hh}\n(emoji) - :unicorn: (любой эмоджи)\n(function) - функция (add/remove/verify/limit)\n(roles) - через пробел @укажите роли или id роли', color=server['embed_color'])

            emb.add_field(name = 'Формат очистки', value = f'`{ctx.prefix}rr_clear (message-id)`\n(message-id) - укажите {hh}')

            emb.add_field(name = 'Формат удаления', value = f'`{ctx.prefix}rr_remove (message-id) (emoji)`\n(message-id) - укажите {hh}\n(emoji) - :unicorn: (любой эмоджи)')

            emb.add_field(name = 'Формат насройки ролей которые могут использовать реакции', value = f'`{ctx.prefix}rr set_roles (message-id) (roles)`\n(message-id) - укажите {hh}\n(roles) - через пробел @укажите роли', inline = False)
            await ctx.send(embed = emb)

    @commands.command(usage = '(message_id) (:emoji:) (function) (@roles)', description = 'Удалить игнорируемый канал.', help = 'Роли по реакциям')
    async def rr_set(self, ctx, message_id:int, emoji:str, function:str, *, roles):
        if funs.roles_check(ctx.author, ctx.guild.id) == False:
            await ctx.send("У вас недостаточно прав для использования этой команды!")
            return

        try:
            message = await ctx.channel.fetch_message(message_id)
        except Exception:
            await ctx.send('Сообщение не найдено!')
            return

        try:
            if len(emoji) != 1:
                l = len(emoji) - 19
                em = int(emoji[l:-1])
            else:
                em = emoji
        except Exception:
            await ctx.send('Эмоджи указан не верно!')
            return


        ls = [] #проверка на роли
        roles = roles.split()
        for i in roles:
            i = i.replace('<', '')
            i = i.replace('@', '')
            i = i.replace('>', '')
            i = i.replace('&', '')
            r = ctx.guild.get_role(int(i))
            if r == None:
                await ctx.send(f"Укажите @роль, для справки напишите `{ctx.prefix}rr`")
                return

            ls.append(int(i))


        if function not in ['add', 'remove', 'verif', 'limit']:
            await ctx.send(f"Укажите доступную функцию, для справки напишите `{ctx.prefix}rr`")
            return

        if function == 'limit':
            try:
                help_message = await ctx.send(f"Введите в чат без использования команд remove/add и число лимита\nПример: add 100 / remove 12")
                msg = await self.bot.wait_for('message', timeout=60.0, check=lambda message: message.author == ctx.author and message.channel.id == ctx.channel.id)
            except asyncio.TimeoutError:
                await ctx.send("Время вышло.")
                return
            else:
                try:
                    await msg.delete()
                    await help_message.delete()
                except Exception:
                    pass
                msg = msg.content.split()
                if msg[0] not in ['add', 'remove']:
                    await ctx.send(f"Введите в чат без использования команд remove/add.")
                    return
                try:
                    msg[1] = int(msg[1])
                except Exception:
                    await ctx.send(f"Требовалось ввести вторым аргументом __число__!")
                    return

                server = servers.find_one({"server": ctx.guild.id})

                rrs = server['rr'].copy()

                try:
                    list = rrs[str(message_id)]['emojis']
                    list.append([em, ls, msg[1], [] ])
                    rrs.update({str(message_id): {'emojis': list, 'func': function, 'limit_func': msg[0] }})
                except Exception:
                    rrs.update({str(message_id): {'emojis': [[em, ls, msg[1], [] ]], 'func': function, 'limit_func': msg[0] }})

                await message.add_reaction(emoji)
                servers.update_one({'server':ctx.guild.id},{'$set': {'rr':rrs}})
                await ctx.send("Роль за реакцию настроена!")

        else:
            await message.add_reaction(emoji)
            server = servers.find_one({"server": ctx.guild.id})

            rrs = server['rr'].copy()

            try:
                list = rrs[str(message_id)]['emojis']
                list.append([em, ls])
                rrs.update({str(message_id): {'emojis': list, 'func': function }})
            except Exception:
                rrs.update({str(message_id): {'emojis': [[em, ls]], 'func': function }})

            await ctx.send("Роль за реакцию настроена!")
            servers.update_one({'server':ctx.guild.id},{'$set': {'rr':rrs}})

    @commands.command(usage = '(message_id)', description = 'Сбросить все реакции с сообщения.', help = 'Роли по реакциям')
    async def rr_clear(self, ctx, message_id:int):
        if funs.roles_check(ctx.author, ctx.guild.id) == False:
            await ctx.send("У вас недостаточно прав для использования этой команды!")
            return

        server = servers.find_one({"server": ctx.guild.id})

        try:
            m = server['rr'][str(message_id)] #при не нахождении выводит ошибку
            try:
                message = await ctx.channel.fetch_message(message_id) #при не нахождении выводит ошибку
            except Exception:
                r = server['rr'].copy()
                r.pop(str(message_id), None)
                servers.update_one({'server':ctx.guild.id},{'$set': {'rr':r}})
                await ctx.send('Сообщение не найдено!')
                return
        except Exception:
            await ctx.send('Сообщение не найдено!')
            return


        rr = server['rr'].copy()
        rr.pop(str(message_id), None)
        servers.update_one({'server':ctx.guild.id},{'$set': {'rr':rr}})
        await ctx.send('Все реакции с сообщения сброшены')

    @commands.command(usage = '(message_id) (:emoji:)', description = 'Удалить реакцию.', help = 'Роли по реакциям')
    async def rr_remove(self, ctx, message_id:int, emoji:str):
        if funs.roles_check(ctx.author, ctx.guild.id) == False:
            await ctx.send("У вас недостаточно прав для использования этой команды!")
            return
        server = servers.find_one({"server": ctx.guild.id})

        try:
            m = server['rr'][str(message_id)] #при не нахождении выводит ошибку
            try:
                message = await ctx.channel.fetch_message(message_id) #при не нахождении выводит ошибку
            except Exception:
                r = server['rr'].copy()
                r.pop(str(message_id), None)
                servers.update_one({'server':ctx.guild.id},{'$set': {'rr':r}})
                await ctx.send('Сообщение не найдено!')
                return
        except Exception:
            await ctx.send('Сообщение не найдено!')
            return

        if len(emoji) != 1:
            l = len(emoji) - 19
            em = int(emoji[l:-1])
        else:
            em = emoji

        r = server['rr'].copy()
        ch = 0
        for i in server['rr'][str(message_id)]['emojis']:
            if em in i:
                r[str(message_id)]['emojis'].remove(i)
                servers.update_one({'server':ctx.guild.id},{'$set': {'rr':r}})
                ch += 1

        rs = server['rr'].copy()
        if rs[str(message_id)]['emojis'] == []:
            rs.pop(str(message_id), None)
            servers.update_one({'server':ctx.guild.id},{'$set': {'rr':rs}})

        if ch == 0:
            await ctx.send('Реакция не найдена!')
            return
        else:
            await ctx.send(f'Роль за реакцию была удалена!')

    @commands.command(usage = '-', description = 'Информация об активных ролей по реакциям.', help = 'Роли по реакциям')
    async def rr_info(self, ctx):
        server = servers.find_one({"server": ctx.guild.id})
        if server['rr'] == {}:
            await ctx.send('Пусто')
            return

        text = ''
        roles = []

        for i in server['rr']:
            for a in server['rr'][str(i)]['emojis']:
                for role in a[1]:
                    r = ctx.guild.get_role(role)
                    roles.append(r.mention)

                if len(str(a[0])) != 1:
                    e = self.bot.get_emoji(a[0])
                else:
                    e = a[0]
                roles =  ' '.join(roles)
                f = server['rr'][str(i)]['func']
                try:
                    aroles = []
                    for role in server['rr'][str(i)]['allow roles']:
                        r = ctx.guild.get_role(role)
                        aroles.append(r.mention)
                    aroles = ' '.join(aroles)
                    text = text + f'`{i}`: {e} - {f} {roles}, only for: {aroles} \n'
                except Exception:
                    text = text + f'`{i}`: {e} - {f} {roles}\n'
                roles = []


        emb = discord.Embed(title = 'Роли по реакциям', description = text, color=server['embed_color'])
        await ctx.send(embed = emb)

    @commands.command(usage = '(message_id) (@roles)', description = 'Настройка доступа для определённых ролей.', help = 'Роли по реакциям')
    async def rr_set_roles(self, ctx, message_id:int, *, roles):
        if funs.roles_check(ctx.author, ctx.guild.id) == False:
            await ctx.send("У вас недостаточно прав для использования этой команды!")
            return
        server = servers.find_one({"server": ctx.guild.id})

        try:
            m = server['rr'][str(message_id)] #при не нахождении выводит ошибку
            try:
                message = await ctx.channel.fetch_message(message_id) #при не нахождении выводит ошибку
            except Exception:
                r = server['rr'].copy()
                r.pop(str(message_id), None)
                servers.update_one({'server':ctx.guild.id},{'$set': {'rr':r}})
                await ctx.send('Сообщение не найдено!')
                return
        except Exception:
            await ctx.send('Сообщение не найдено!')
            return

        ls = [] #проверка на роли
        roles = roles.split()
        for i in roles:
            i = i.replace('<', '')
            i = i.replace('@', '')
            i = i.replace('>', '')
            i = i.replace('&', '')
            r = ctx.guild.get_role(int(i))
            if r == None:
                await ctx.send(f"Укажите @роль, для справки напишите `{ctx.prefix}rr`")
                return

            ls.append(int(i))

        r = server['rr'].copy()
        r[str(message_id)].update({'allow roles': ls})
        servers.update_one({'server':ctx.guild.id},{'$set': {'rr':r}})
        emb = discord.Embed(title = 'Доступ для ролей добавлен',color=server['embed_color'])
        await ctx.send(embed = emb)

    @commands.command(usage = '(#channel)', description = 'Установить канал оповещения о бусте.', help = 'Оповещение о бусте')
    async def boost_channel(self, ctx, channel:discord.TextChannel):
        global servers
        if funs.roles_check(ctx.author, ctx.guild.id) == False:
            await ctx.send("У вас недостаточно прав для использования этой команды!")
            return
        server = servers.find_one({'server':ctx.guild.id})
        a = server['boost'].copy()
        a.update({"send": channel.id})

        servers.update_one({'server':ctx.guild.id},{'$set':{'boost': a}})
        await ctx.send(f'Канал {channel.mention} установлен для оповещения о бустах.')

    @commands.command(usage = '[description]', description = 'Установить описание при бусте.', help = 'Оповещение о бусте')
    async def boost_description(self, ctx, *, description:str = None):
        global servers
        if funs.roles_check(ctx.author, ctx.guild.id) == False:
            await ctx.send("У вас недостаточно прав для использования этой команды!")
            return
        if description == None:
            await ctx.send(funs.text_replase("text"))
            return
        if len(description) > 1500:
            await ctx.send(f'Сообщение не может быть более 1.5к символов')
            return

        server = servers.find_one({'server':ctx.guild.id})
        a = server['boost']
        a.update({'description': description})

        servers.update_one({'server':ctx.guild.id},{'$set':{'boost': a}})
        await ctx.send(funs.text_replase(description, ctx.author))
        await ctx.send('Текст установлен (текст указан как бы он был при бусте от вашего имени в данный момент)')

    @commands.command(usage = '(url)', description = 'Установить изображение при бусте.', help = 'Оповещение о бусте')
    async def boost_url(self, ctx, url):
        global servers
        if funs.roles_check(ctx.author, ctx.guild.id) == False:
            await ctx.send("У вас недостаточно прав для использования этой команды!")
            return
        server = servers.find_one({"server": ctx.guild.id})
        try:
            emb = discord.Embed(description = 'Вы поменяли изображение!', color=server['embed_color'])
            emb.set_image(url = url)
        except Exception:
            await ctx.send(f'Укажите ссылка.')
            return

        server = servers.find_one({'server':ctx.guild.id})
        a = server['boost'].copy()
        a.update({"url": url})

        servers.update_one({'server':ctx.guild.id},{'$set':{'boost': a}})
        await ctx.send(embed = emb)

    @commands.command(usage = '(description)', description = 'Установить подвал при бусте.', help = 'Оповещение о бусте')
    async def boost_footer(self, ctx, *, description = None):
        global servers
        if funs.roles_check(ctx.author, ctx.guild.id) == False:
            await ctx.send("У вас недостаточно прав для использования этой команды!")
            return
        if description == None:
            await ctx.send(funs.text_replase("text"))
            return
        if len(description) > 1500:
            await ctx.send(f'Сообщение не может быть более 1.5к символов')
            return

        server = servers.find_one({'server':ctx.guild.id})
        a = server['boost']
        a.update({'description': description})

        servers.update_one({'server':ctx.guild.id},{'$set':{'boost': a}})
        text = funs.text_replase(description, ctx.author)
        emb = discord.Embed(description = 'Вы поменяли подвал сообщения!', color=server['embed_color'])
        emb.set_footer(text = text)
        await ctx.send(embed = emb)

    @commands.command(usage = '-', description = 'Тестовое сообщение о бусте.', help = 'Оповещение о бусте')
    async def boost_test(self, ctx):
        if funs.roles_check(ctx.author, ctx.guild.id) == False:
            await ctx.send("У вас недостаточно прав для использования этой команды!")
            return
        booster = ctx.author
        server = servers.find_one({"server": ctx.guild.id})
        if server["boost"]["send"] == None:
            await ctx.send("Буст не настроен.")
            return

        if server['boost']['description'] != None:
            text = funs.text_replase(server['boost']['description'], booster)
        else:
            text = funs.text_replase("Огромное спасибо {member.mention}, что помог серверу!", booster)

        emb = discord.Embed(title = 'Бустит сервер!', description =f"{text}", color=server['embed_color'])
        emb.set_author(icon_url = 'https://images-ext-1.discordapp.net/external/t8PQC99J_sKLcmwB6EVhtlmiIq8iG47SHE_gDJcQeOU/https/i.imgur.com/GdS5i6t.gif', name = booster)
        emb.set_thumbnail(url= ctx.author.avatar.url)
        if server["boost"]["url"] != None:
            emb.set_image(url = server["boost"]["url"])
        if server["boost"]["footer"] != None:
            emb.set_footer(text = funs.text_replase(server['boost']['footer'], booster))

        await ctx.send(embed = emb)

    @commands.command(usage = '-', description = 'Сбросить буст.', help = 'Оповещение о бусте')
    async def boost_reset(self, ctx):
        global servers
        if funs.roles_check(ctx.author, ctx.guild.id) == False:
            await ctx.send("У вас недостаточно прав для использования этой команды!")
            return
        server = servers.find_one({'server':ctx.guild.id})
        a = server['boost'].copy()
        a.update({"send": None})

        servers.update_one({'server':ctx.guild.id},{'$set':{'boost': a}})
        await ctx.send("Кастомный буст отключён.")

    @commands.command(usage = '(currency)', description = 'Установить значок экономики.', help = 'Настройка экономики')
    async def set_currency(self, ctx, arg:str):
        global servers
        if funs.roles_check(ctx.author, ctx.guild.id) == False:
            await ctx.send("У вас недостаточно прав для использования этой команды!")
            return
        if len(arg) > 50:
            await ctx.send("Значок экономики не может быть больше 50-ти символов!")
            return

        server = servers.find_one({'server':ctx.guild.id})
        a = server['economy'].copy()
        a.update({"currency": arg})

        servers.update_one({'server':ctx.guild.id},{'$set':{'economy': a}})
        await ctx.send(f"Значок экономики был изменён на {arg}.")

    @commands.command(usage = '(commands)', description = 'Отключить команду.', help = 'Управление командами')
    async def disable(self, ctx, *arg:str):
        global servers
        if funs.roles_check(ctx.author, ctx.guild.id) == False:
            await ctx.send("У вас недостаточно прав для использования этой команды!")
            return
        server = servers.find_one({'server':ctx.guild.id})
        a = server['mod']['off_commands']
        for i in arg:
            c = self.bot.get_command(i)
            if c == None:
                await ctx.send(f'Команды {i} не было найдено!')
                return
            elif c.name in ['disable', 'enable']:
                await ctx.send(f'Команду не возможно отключить!')
                return
            elif c.name in a:
                await ctx.send(f'Команда уже отключена!')
                return
            a.append(c.name)

        await ctx.send('Команда(ы) были отключены на данном сервере.')
        b = server['mod']
        b.update({'off_commands': a})
        servers.update_one({'server':ctx.guild.id},{'$set': {'mod': b }})

    @commands.command(usage = '(commands)', description = 'Включить команду.', help = 'Управление командами')
    async def enable(self, ctx, *arg:str):
        global servers
        if funs.roles_check(ctx.author, ctx.guild.id) == False:
            await ctx.send("У вас недостаточно прав для использования этой команды!")
            return
        server = servers.find_one({'server':ctx.guild.id})
        a = server['mod']['off_commands']
        for i in arg:
            c = self.bot.get_command(i)
            if c == None:
                await ctx.send(f'Команды {i} не было найдено!')
                return
            if c.name not in server['mod']['off_commands']:
                await ctx.send(f'Команда `{c.name}` не отключена!')
                return
            a.remove(c.name)
        await ctx.send('Команда(ы) были включены на данном сервере.')
        b = server['mod']
        b.update({'off_commands': a})
        servers.update_one({'server':ctx.guild.id},{'$set': {'mod': b }})

    @commands.command(aliases = ['disabled'], usage = '-', description = 'Список отключённых команд.', help = 'Управление командами')
    async def disabled_commands(self, ctx):
        global servers
        if funs.roles_check(ctx.author, ctx.guild.id) == False:
            await ctx.send("У вас недостаточно прав для использования этой команды!")
            return
        server = servers.find_one({'server':ctx.guild.id})
        a = server['mod']['off_commands']
        emb = discord.Embed(title = f'Отключённые команды',description = ', '.join(a),color=server['embed_color'])
        await ctx.send(embed = emb)

    @commands.command(usage = '(roles)', description = 'Добавить административную роль.', help = 'Настройка модерации')
    async def add_admin_roles(self, ctx, *role:discord.Role):
        global servers
        if funs.roles_check(ctx.author, ctx.guild.id) == False:
            await ctx.send("У вас недостаточно прав для использования этой команды!")
            return
        server = servers.find_one({'server':ctx.guild.id})
        a = server['mod']['admin_roles']
        for i in role:
            a.append(i.id)
        await ctx.send('Пользователи с данными ролью(ми) теперь могут настраивать бота и управлять модерацией!')
        a = server['mod']
        a.update({'admin_roles': a})
        servers.update_one({'server':ctx.guild.id},{'$set': {'mod': a }})

    @commands.command(usage = '(roles)', description = 'Удалить административную роль.', help = 'Настройка модерации')
    async def remove_admin_roles(self, ctx, *role:discord.Role):
        global servers
        if funs.roles_check(ctx.author, ctx.guild.id) == False:
            await ctx.send("У вас недостаточно прав для использования этой команды!")
            return
        server = servers.find_one({'server':ctx.guild.id})
        a = server['mod']['admin_roles']
        for i in role:
            if i.id not in server['mod']['admin_roles']:
                await ctx.send(f'Роль `{i}` не назначена!')
                return
            else:
                a.remove(i.id)
        await ctx.send('Пользователи с данной ролью(ми) тперь не могут управлять настройками бота и модерацией!')
        a = server['mod']
        a.update({'admin_roles': a})
        servers.update_one({'server':ctx.guild.id},{'$set': {'mod': a }})

    @commands.command(usage = '-', description = 'Список админ ролей.', help = 'Настройка модерации')
    async def admins_roles(self, ctx):
        global servers
        if funs.roles_check(ctx.author, ctx.guild.id) == False:
            await ctx.send("У вас недостаточно прав для использования этой команды!")
            return
        server = servers.find_one({'server':ctx.guild.id})
        a = server['mod']['admin_roles']
        text = ''
        for i in a:
            text += f"<@&{i}>, "
        emb = discord.Embed(title = f'Роли с доступом',description = text,color=server['embed_color'])
        await ctx.send(embed = emb)

    @commands.command(usage = '-', description = 'Проверить админ роли.', help = 'Настройка модерации')
    @commands.has_permissions( administrator = True)
    async def check_admins_roles(self, ctx):
        global servers
        server = servers.find_one({'server':ctx.guild.id})
        a = server['mod']['admin_roles']
        n = 0
        for i in a:
            role = ctx.guild.get_role(i)
            if role == None:
                a.remove(i)
                n += 1

        servers.update_one({'server':ctx.guild.id},{'$set': {'mod': {'admin_roles': a}}})
        emb = discord.Embed(title = f'Проверка',description = f"Управляющие роли проверены, удалённые роли были исключены! `({n})`",color=server['embed_color'])
        await ctx.send(embed = emb)

    @commands.command(usage = '-', description = 'Установить эмбет для входа.', help = 'Настройки вход | выход')
    async def set_welcom_emb(self, ctx):
        global servers
        if funs.roles_check(ctx.author, ctx.guild.id) == False:
            await ctx.send("У вас недостаточно прав для использования этой команды!")
            return
        server = servers.find_one({'server':ctx.guild.id})
        if server['welcome']['emb_st'] == False:
            server['welcome'].update({'emb_st': True})
            text = "Режим embed активирован"

        elif server['welcome']['emb_st'] == True:
            server['welcome'].update({'emb_st': False})
            text = "Режим embed деактивирован"

        servers.update_one({'server':ctx.guild.id},{'$set':{'welcome': server['welcome']}})
        emb = discord.Embed(description = text,color=server['embed_color'])
        await ctx.send(embed = emb)

    @commands.command(usage = '-', description = 'Установить эмбет для выхода.', help = 'Настройки вход | выход')
    async def set_goodbye_emb(self, ctx):
        global servers
        if funs.roles_check(ctx.author, ctx.guild.id) == False:
            await ctx.send("У вас недостаточно прав для использования этой команды!")
            return
        server = servers.find_one({'server':ctx.guild.id})
        if server['goodbye']['emb_st'] == False:
            server['goodbye'].update({'emb_st': True})
            text = "Режим embed активирован"

        elif server['goodbye']['emb_st'] == True:
            server['goodbye'].update({'emb_st': False})
            text = "Режим embed деактивирован"

        servers.update_one({'server':ctx.guild.id},{'$set':{'goodbye': server['goodbye']}})
        emb = discord.Embed(description = text,color=server['embed_color'])
        await ctx.send(embed = emb)

    @commands.command(usage = '(#channel) (emojis)', description = 'Установить канал с автоматическими эмоджи.', help = 'Эмоджи-канал')
    async def set_emoji_channel(self, ctx, channel:discord.TextChannel, *emojis):
        global servers
        if funs.roles_check(ctx.author, ctx.guild.id) == False:
            await ctx.send("У вас недостаточно прав для использования этой команды!")
            return

        test_msg = await ctx.send("Тестовое сообщение\n Не удаляйте его, оно быдут удалено автоматически при наличии прав у бота")
        list = []

        try:
            for x in emojis:
                await test_msg.add_reaction(x)
                list.append(x)

        except Exception:
            await ctx.send("Требовалось указать emoji через пробел")
            return

        server = servers.find_one({'server':ctx.guild.id})

        try:
            await test_msg.delete()
        except Exception:
            return

        if len(list) > 2 and server['premium'] == False:
                await ctx.send("У вас нет премиум подписки, вам доступна только 2 эмоджи!")
                return

        if len(list) > 20:
            await ctx.send("Нельзя добавить больше 20-ти реакций под сообщение!")
            return

        server = servers.find_one({'server':ctx.guild.id})
        a = server['emoji']
        a.update({'emoji_channel': channel.id,'emojis': list})
        servers.update_one({'server':ctx.guild.id},{'$set': {'emoji': a }})

    @commands.command(usage = '(url) (met) (color) (time_zone) (gps)', description = 'Установить кастомный баннер сервера.', help = 'Кастомный баннер')
    async def set_banner(self, ctx, url:str, met:str, color:str, time_zone:int, gps:str):
        global servers
        if funs.roles_check(ctx.author, ctx.guild.id) == False:
            await ctx.send("У вас недостаточно прав для использования этой команды!")
            return

        server = servers.find_one({'server':ctx.guild.id})

        try:
            pr = server['premium']
        except Exception:
            pr = False

        if pr == False:
            blist = ['time', 'stat', 'stat-nb']
        else:
            blist = ['time', 'top-lvl', 'stat', 'voice-stat', 'common', 'stat-nb', 'voice-stat-nb']

        if ctx.guild.premium_subscription_count < 15:
            await ctx.send("У вас не достаточно бустов сервера!")
            return

        try:
            emb1 = discord.Embed(title = "Изображение", color=server['embed_color'])
            emb1.set_image(url = url)
            msg = await ctx.send(embed = emb1)
        except Exception:
            await ctx.send("Требовалось указать __ссылку__ на баннер, повторите настройку ещё раз.")
            return

        await msg.delete()


        if met in blist:
            met_d = True
        else:
            met_d = False

        if met_d != True:
            await ctx.send(f"Вариант баннера указан не правильно, проверьте правильно ли вы указали тип баннера и имеется ли у вас подписка для данного баннера!")
            return

        if color not in ['gard','mini', 'blue-sky']:
            await ctx.send("Вариант цвета баннера указан не правильно!\nДоступные цвета: gard, mini, blue-sky")
            return

        if gps not in ['center', 'center-top', 'center-bottom', 'lower-left-corner', 'upper-left-corner', 'bottom-right-corner', 'upper-right-corner']:
            await ctx.send(f"Вариант положения указан не правильно!\nДоступные положения: center, center-top, center-bottom, lower-left-corner, upper-left-corner, bottom-right-corner, upper-right-corner\nПросмотрите их написав {ctx.prefix}gps_banner")
            return

        if time_zone < -12 or time_zone > 14:
            await ctx.send("Требовалось указать временную зону от -12 до 14")
            return

        servers.update_one({'server':ctx.guild.id},{'$set':
        {'banner': {'url': url,
                    'met': met,
                    'color': color,
                    'time': time_zone,
                    'gps': gps
        }}})
        servers.update_one({'server':ctx.guild.id},{'$set':{'banner_status': True}})

        await ctx.send("Баннер успешно настроен, смена баннера происходит 1 раз в минуту, при смене изображения в самом дискрд сервере ничего не произайдёт, изменяйте изображение в боте или отключите смену баннера!")


    @commands.command(usage = '-', description = 'Удалить баннер.', help = 'Кастомный баннер')
    async def remove_banner(self, ctx):
        global servers
        if funs.roles_check(ctx.author, ctx.guild.id) == False:
            await ctx.send("У вас недостаточно прав для использования этой команды!")
            return

        servers.update_one({'server':ctx.guild.id},{'$set':{'banner_status': False}})
        await ctx.send('Баннер был удалён.')

    @commands.command(usage = '-', description = 'Информация о кастомном баннере.', help = 'Кастомный баннер')
    async def info_banner(self, ctx):
        server = servers.find_one({"server": ctx.guild.id})

        emb = discord.Embed(title = "Информация о кастоных баннерах",
        color=server['embed_color'])
        emb.add_field(name = f'{ctx.prefix}set_banner (url) (time/top-lvl/stat/voice-stat/common) (gard/mini/blue-sky) (time zone) (gps)', value = f'Установка кастомного баннера.\n**(url)** - укажите ссылку на картинку **__960х540__** пикселей\n**(time/top-lvl/stat/voice-stat/common/stat-nb/voice-stat-nb)** - Для серверов без премиум подписки доступны: time, stat\nДля серверов с премиум подпиской доступны: time, top-lvl, stat, voice-stat, common, stat-nb, voice-stat-nb\n**(gard/mini/blue-sky)** - укажите цвет баннера, gard - гардиент цветов, mini - минимализм, белый цвет, blue-sky - цвет вечернего неба\n**(time zone)** - укажите число от -12 до 14\n (gps) - установка положения информации на баннере (center/center-top/ center-bottom/lower-left-corner/upper-left-corner/bottom-right-corner/upper-right-corner) **(для информации вызовите {ctx.prefix}gps_banner)**')
        emb.add_field(name = f'{ctx.prefix}remove_banner', value = 'Удаление баннера. Это команда отключит смену баннера.', inline = False)
        emb.set_image(url = 'https://ic.wampi.ru/2021/08/18/imagec24053e9b5c795eb.png')
        await ctx.send(embed = emb)

    @commands.command(usage = '-', description = 'Полоение для информации на баннере.', help = 'Кастомный баннер')
    async def gps_banner(self, ctx):
        server = servers.find_one({"server": ctx.guild.id})
        emb = discord.Embed(title = "Информация о положении информации на баннере",
        color=server['embed_color'])
        emb.set_image(url = 'https://ic.wampi.ru/2021/07/10/gps8b1b0b4cebf8616d.png')
        await ctx.send(embed = emb)

    @commands.command(usage = '(command) (type) (time)', description = 'Установить задержку использования для команды.', help = 'Управление командами')
    async def add_cooldown(self, ctx, command:str, type:str, time:int):
        global servers
        if funs.roles_check(ctx.author, ctx.guild.id) == False:
            await ctx.send("У вас недостаточно прав для использования этой команды!")
            return

        com = self.bot.get_command(command)
        if com == None:
            await ctx.send("Требовалось указать существующее название команды и без префикса.")
            return

        if com.name == 'reset_cooldown' or com.name == 'remove_cooldown' or com.name == 'daily':
            await ctx.send("Для данной команды нельзя установить задержку.")
            return

        if type not in ['users', 'server', 'roles']:
            await ctx.send("Требовалось указать тип: `users`, `server`, `roles`\n`users` - задержка использования для каждого пользователя отдельно.\n`server` - задержка использования для всего сервера сразу.\n`roles` - задержка использования для ролей.")
            return

        if time < 0 or time > 2592001:
            await ctx.send("Требовалось указать число секунд задержки больше 0 и меньше 2592001 (30 дней, 1 секунда).")
            return

        if type == 'users':
            com_cool = {
            'type': type,
            'time': time,
            'users': {},
            }
        elif type == 'server':
            com_cool = {
            'type': type,
            'time': time,
            'server_c': 0,
            }
        elif type == 'roles':
            com_cool = {
            'type': type,
            'time': time,
            'role_c': 0,
            }

        server = servers.find_one({'server':ctx.guild.id})
        server['mod']['cooldowns'].update({command : com_cool})

        servers.update_one({'server':ctx.guild.id},{'$set': {'mod': server['mod'] }})
        await ctx.send(f"Задержка на использование команды `{command}` было установлено на {funs.time_end(time)}")

    @commands.command(usage = '(command)', description = 'Удаление задержки для команды.', help = 'Управление командами')
    async def remove_cooldown(self, ctx, command:str):
        global servers
        if funs.roles_check(ctx.author, ctx.guild.id) == False:
            await ctx.send("У вас недостаточно прав для использования этой команды!")
            return

        server = servers.find_one({'server':ctx.guild.id})
        com = self.bot.get_command(command)
        if com == None:
            await ctx.send("Требовалось указать существующее название команды и без префикса.")
            return

        try:
            server['mod']['cooldowns'].pop(com.name)
        except Exception:
            await ctx.send("Для команды не назначена задержка.")
            return

        servers.update_one({'server':ctx.guild.id},{'$set': {'mod': server['mod'] }})
        await ctx.send(f"Задержка для команды {com.name} была удалена.")


    @commands.command(usage = '(command) (@member) [met]', description = 'Сбросить задержку для пользователей.', help = 'Управление командами')
    async def reset_cooldown(self, ctx, command:str, member: discord.Member, met:str = 'one'):
        global servers
        if funs.roles_check(ctx.author, ctx.guild.id) == False:
            await ctx.send("У вас недостаточно прав для использования этой команды!")
            return

        com = self.bot.get_command(command)
        if com == None:
            await ctx.send("Требовалось указать существующее название команды и без префикса.")
            return

        if met not in ['all', 'one']:
            await ctx.send("Требовалось указать all/one \nall - обнулить всем пользователям задержку\none - обнулить указанному пользователю задержку\n**Требуется указывать если у комманды задержка типа `users`**")
            return

        if met == 'one':
            if funs.cooldown_check(member, ctx.guild, command, 'reset') == True:
                await ctx.send("Пользователю была обнулена задержка на данную команду.")
            else:
                await ctx.send("У пользователя нет задержки.")
        else:
            if funs.cooldown_check(member, ctx.guild, command, 'reset', True) == True:
                await ctx.send("Всем пользователям была обнулена задержка для данной команды.")

    @commands.command(usage = '(met1) (met2)', description = 'Установка сохранения данных для вышедших пользователей.', help = 'Настройки вход | выход')
    async def save_change(self, ctx, arg1, arg2:bool):
        if funs.roles_check(ctx.author, ctx.guild.id) == False:
            await ctx.send("У вас недостаточно прав для использования этой команды!")
            return

        if arg1 not in ['name', 'roles', 'date']:
            await ctx.send("Требовалось указать `name`/`roles`/`date`\nname - сохранение никенейма/имени\nroles - сохранение ролей пользователя\ndate - сохранение общих данных не сохраняя роли и имя ")
            return

        if arg2 not in [True, False]:
            await ctx.send("Требовалось указать True/False\n`True` - включить\n`False` - выключить")
            return

        server = servers.find_one({'server':ctx.guild.id})
        server['save'].update({arg1 + "_save" : arg2})
        servers.update_one({'server':ctx.guild.id},{'$set':{'save': server['save'] }})
        await ctx.send(f"Сохранено {arg1}: `{arg2}`")

    @commands.command(usage = '-', description = 'Информация о соранении.', help = 'Настройки вход | выход')
    async def save_info(self, ctx):

        server = servers.find_one({'server':ctx.guild.id})
        emb = discord.Embed(title = "Информация об сохранении данных",
        color=server['embed_color'], description = f"Сохранение имени пользователя: `{server['save']['name_save']}`\nСохранение ролей пользователя: `{server['save']['roles_save']}`\nСохранение общих данных пользователя (без сохранения имени и ролей): `{server['save']['date_save']}`")

        await ctx.send(embed = emb)

    @commands.command(usage = '(@roles)', description = 'Роли за вход.', help = 'Настройки вход | выход')
    async def join_roles(self, ctx, *role:discord.Role):
        if funs.roles_check(ctx.author, ctx.guild.id) == False:
            await ctx.send("У вас недостаточно прав для использования этой команды!")
            return

        a = []
        for i in role:
            a.append(i.id)
        await ctx.send('Роли для новых участников были установлены!')
        servers.update_one({'server':ctx.guild.id},{'$set':{'join_roles': a}})

    @commands.command(usage = '-', description = 'Отключить роль зи вход.', help = 'Настройки вход | выход')
    async def join_roles_off(self, ctx):
        if funs.roles_check(ctx.author, ctx.guild.id) == False:
            await ctx.send("У вас недостаточно прав для использования этой команды!")
            return

        await ctx.send('Роли для новых участников были отключены.')
        servers.update_one({'server':ctx.guild.id},{'$set':{'join_roles': [] }})

    @commands.command(usage = '[new_name]', description = 'Изменение имени для вошедштх пользователей.', help = 'Настройки вход | выход')
    async def nick_change(self, ctx, *, description:str = None):
        global servers
        if funs.roles_check(ctx.author, ctx.guild.id) == False:
            await ctx.send("У вас недостаточно прав для использования этой команды!")
            return

        if description == None:
            await ctx.send(funs.text_replase("text"))
            return

        if len(description) > 20:
            await ctx.send(f'Сообщение не может быть более 20-ти символов')
            return

        server = servers.find_one({'server':ctx.guild.id})

        servers.update_one({'server':ctx.guild.id},{'$set':{'nick_change': description}})
        await ctx.send(funs.text_replase(description, ctx.author))
        await ctx.send('Установлено изменение ника при входе (текст указан как бы это выглядело зайдя вы на сервер)')

    @commands.command(usage = '-', description = 'Информация о защите от флуда.', help = 'Настройка модерации')
    async def flud_info(self, ctx):
        server = servers.find_one({"server": ctx.guild.id})
        emb = discord.Embed(title = f'Информация о настройке защиты от флуда', description = f'`{ctx.prefix}set_flud (repetitions) (punishment)`', color=server['embed_color'] )
        emb.add_field(name = 'repetitions (int)', value = f'Укажите сколько одинаковых сообщений требуется ввести пользователю что бы получить наказание\nПример: 3')
        emb.add_field(name = 'punishment (*str)', value = f'Через пробел укажите наказания из этого списка - ( ban, kick, warn, role-add, role-remove, message, delete-all, delete, role-add, role-remove )\nПример: warn message delete-all')
        await ctx.send(embed = emb)

    @commands.command(usage = '(repetitions) (punishments)', description = 'Настройка защиты от флуда.', help = 'Настройка авто-модерации')
    async def set_flud(self, ctx, repetitions:int, *punishment:str):
        global servers
        if funs.roles_check(ctx.author, ctx.guild.id) == False:
            await ctx.send("У вас недостаточно прав для использования этой команды!")
            return

        pun = []
        for i in punishment:
            if i in ["ban", "kick", "warn", "message", "delete-all", "delete", "role-add", "role-remove"]:
                pun.append(i)
        if pun != []:
            server = servers.find_one({'server':ctx.guild.id})
            server['mod']['flud_shield'].update({
            'repetitions': repetitions,
            'punishment': pun,
             })

            if 'message' in pun:
                await ctx.send(f'Пропишите команду {ctx.prefix}set_flud_message\n для настройки сообщения')
                server['mod']['flud_shield'].update({'message': None, 'mess-type': None})

            if 'role-add' in pun or "role-remove" in pun:
                await ctx.send(f'Пропишите команду {ctx.prefix}set_flud_role\n для настройки роли')
                server['mod']['flud_shield'].update({'add-role': None, 'roleremove': None})

            servers.update_one({'server':ctx.guild.id},{'$set':{'mod': server['mod']}})
            await ctx.send(f'Анти-флуд настроен')
        else:
            await ctx.send(f'Нету ни одного совпадения с доступными наказаниями')

    @commands.command(usage = '(type) (message)', description = 'Сообщение при флуде.', help = 'Настройка авто-модерации')
    async def set_flud_message(self, ctx, type = None, *message):
        global servers
        if funs.roles_check(ctx.author, ctx.guild.id) == False:
            await ctx.send("У вас недостаточно прав для использования этой команды!")
            return

        server = servers.find_one({'server':ctx.guild.id})
        if type == None:
            await ctx.send(f"{ctx.prefix}set_flud_message (type) (message)\ntype - укажите отображение emb или mes\nmessge - введите сообщени длинной максимум 1500 символов\nПример: {ctx.prefix}set_flud_message emb Ты плохой человек")
        else:
            if type not in ['emb', 'mes']:
                await ctx.send('Требовалось указать emb или mes')
                return
            if len(str(message)) > 1500:
                await ctx.send(f'Требовалось указать сообщение длинной меньше или равной 1500 символов (Сейчас {len(str(message))})')
                return

            server['mod']['flud_shield'].update({'mess-type': type, 'message': message})
            servers.update_one({'server':ctx.guild.id},{'$set':{'mod': server['mod']}})
            await ctx.send("Сообщение настроено")

    @commands.command(usage = '(type) (@role)', description = 'Роль при флуде.', help = 'Настройка авто-модерации')
    async def set_flud_role(self, ctx, type = None, role: discord.Role = None):
        global servers
        if funs.roles_check(ctx.author, ctx.guild.id) == False:
            await ctx.send("У вас недостаточно прав для использования этой команды!")
            return

        server = servers.find_one({'server':ctx.guild.id})
        if type == None:
            await ctx.send(f"{ctx.prefix}set_flud_role (type) (role)\ntype - укажите add или remove\nrole - укажите роль\nПример: {ctx.prefix}set_flud_role add @флудер")
        if role != None:
            if type == 'add':
                server['mod']['flud_shield'].update({'add-role': role.id})
                servers.update_one({'server':ctx.guild.id},{'$set':{'mod': server['mod']}})
            if type == 'remove':
                server['mod']['flud_shield'].update({'remove-role': role.id})
                servers.update_one({'server':ctx.guild.id},{'$set':{'mod': server['mod']}})

            else:
                await ctx.send(f"{ctx.prefix}set_flud_role (type) (role)\ntype - укажите add или remove\nrole - укажите роль\nПример: {ctx.prefix}set_flud_role add @флудер")
                return

            await ctx.send('Роль настроена')

        else:
            await ctx.send(f"{ctx.prefix}set_flud_role (type) (role)\ntype - укажите add или remove\nrole - укажите роль\nПример: {ctx.prefix}set_flud_role add @флудер")

    @commands.command(usage = '-', description = 'Информация о защите от плохих слов\сообщений', help = 'Настройка авто-модерации')
    async def bad_words_info(self, ctx):
        server = servers.find_one({"server": ctx.guild.id})
        emb = discord.Embed(title = f'Информация о настройке запрещённых слов', description = f'`{ctx.prefix}add_bad_words (*words)`', color=server['embed_color'] )
        emb.add_field(name = 'words (*str)', value = f'Через пробел укажите запрещённые слова\nПример: дурак тупой')
        emb.add_field(name = 'Настройка наказания', value = f'`{ctx.prefix}bad_words_pun (*punishment)`', inline = False)
        emb.add_field(name = 'punishment (*str)', value = f'Через пробел укажите наказания из этого списка - ( ban, kick, warn, role-add, role-remove, message, delete-all, delete, role-add, role-remove )\nПример: warn message delete-all')
        await ctx.send(embed = emb)

    @commands.command(usage = '(words)', description = 'Добавить запретное слово.', help = 'Настройка авто-модерации')
    async def add_bad_words(self, ctx, *words:str):
        global servers
        if funs.roles_check(ctx.author, ctx.guild.id) == False:
            await ctx.send("У вас недостаточно прав для использования этой команды!")
            return

        w = []
        for i in words:
            w.append(i)

        server = servers.find_one({'server':ctx.guild.id})
        server['mod']['bad_words'].update({'words': w})
        servers.update_one({'server':ctx.guild.id},{'$set':{'mod': server['mod']}})

        await ctx.send("Запрещённые слова были добавлены в список!")

    @commands.command(usage = '(punishments)', description = 'Добавить наказание за плохое слово.', help = 'Настройка авто-модерации')
    async def bad_words_pun(self, ctx, *punishment:str):
        global servers
        if funs.roles_check(ctx.author, ctx.guild.id) == False:
            await ctx.send("У вас недостаточно прав для использования этой команды!")
            return

        l = ["ban", "kick", "warn", "message", "delete-all", "delete", "role-add", "role-remove"]

        if punishment == ():
            await ctx.send(f"Выберите из этого списка: {', '.join(l)}")
            return

        pun = []
        for i in punishment:
            if i in l:
                pun.append(i)
        if pun != []:
            server = servers.find_one({'server':ctx.guild.id})
            server['mod']['bad_words'].update({'punishment': pun,})
            servers.update_one({'server':ctx.guild.id},{'$set':{'mod': server["mod"] }})

            if 'message' in pun:
                await ctx.send(f'Пропишите команду {ctx.prefix}bad_words_message\n для настройки сообщения')
                server['mod']['bad_words'].update({'message': None, 'mess-type': None})

            if 'role-add' in pun or "role-remove" in pun:
                await ctx.send(f'Пропишите команду {ctx.prefix}bad_words_role\n для настройки роли')
                server['mod']['bad_words'].update({'add-role': None, 'roleremove': None})

            await ctx.send(f'Наказания настроены')
        else:
            await ctx.send(f'Нету ни одного совпадения с доступными наказаниями')

    @commands.command(usage = '(type) (message)', description = 'Добавить сообщение за плохое слово.', help = 'Настройка авто-модерации')
    async def bad_words_message(self, ctx, type = None, *message):
        global servers
        if funs.roles_check(ctx.author, ctx.guild.id) == False:
            await ctx.send("У вас недостаточно прав для использования этой команды!")
            return

        server = servers.find_one({'server':ctx.guild.id})
        if type == None:
            await ctx.send(f"{ctx.prefix}bad_words_message (type) (message)\ntype - укажите отображение emb или mes\nmessge - введите сообщени длинной максимум 1500 символов\nПример: {ctx.prefix}bad_words_message emb Ты плохой человек")
        else:
            if type not in ['emb', 'mes']:
                await ctx.send('Требовалось указать emb или mes')
                return
            if len(str(message)) > 1500:
                await ctx.send(f'Требовалось указать сообщение длинной меньше или равной 1500 символов (Сейчас {len(str(message))})')
                return

            server['mod']['bad_words'].update({'mess-type': type, 'message': message})
            servers.update_one({'server':ctx.guild.id},{'$set':{'mod': server['mod']}})
            await ctx.send("Сообщение настроено")

    @commands.command(usage = '(type) (@role)', description = 'Добавить роль за плохое слово.', help = 'Настройка авто-модерации')
    async def bad_words_role(self, ctx, type = None, role: discord.Role = None):
        global servers
        if funs.roles_check(ctx.author, ctx.guild.id) == False:
            await ctx.send("У вас недостаточно прав для использования этой команды!")
            return

        server = servers.find_one({'server':ctx.guild.id})
        if type == None:
            await ctx.send(f"{ctx.prefix}bad_words_role (type) (role)\ntype - укажите add или remove\nrole - укажите роль\nПример: {ctx.prefix}bad_words_role add @проказник")
        if role != None:
            if type == 'add':
                server['mod']['bad_words'].update({'add-role': role.id})
                servers.update_one({'server':ctx.guild.id},{'$set':{'mod': server['mod']}})
            if type == 'remove':
                server['mod']['bad_words'].update({'remove-role': role.id})
                servers.update_one({'server':ctx.guild.id},{'$set':{'mod': server['mod']}})

            else:
                await ctx.send(f"{ctx.prefix}bad_words_role (type) (role)\ntype - укажите add или remove\nrole - укажите роль\nПример: {ctx.prefix}bad_words_role add @проказник")
                return

            await ctx.send('Роль настроена')

        else:
            await ctx.send(f"{ctx.prefix}bad_words_role (type) (role)\ntype - укажите add или remove\nrole - укажите роль\nПример: {ctx.prefix}bad_words_role add @проказник")

    @commands.command(usage = '(@roles)', description = 'Добавить роль в белый список модерации.', help = 'Настройка авто-модерации')
    async def add_wlist_roles(self, ctx, *role: discord.Role):
        global servers
        if funs.roles_check(ctx.author, ctx.guild.id) == False:
            await ctx.send("У вас недостаточно прав для использования этой команды!")
            return

        server = servers.find_one({'server':ctx.guild.id})
        wl = server['mod']['wlist_roles']
        for i in role:
            if i.id not in wl:
                wl.append(i.id)

        server['mod'].update({'wlist_roles': wl})
        servers.update_one({'server':ctx.guild.id},{'$set':{'mod': server['mod']}})
        await ctx.send("Роли, на которые не реагирует авто-модерация, добавлены")

    @commands.command(usage = '(@members)', description = 'Добавить пользователя в белый список модерации.', help = 'Настройка авто-модерации')
    async def add_wlist_members(self, ctx, *mem: discord.Role):
        global servers
        if funs.roles_check(ctx.author, ctx.guild.id) == False:
            await ctx.send("У вас недостаточно прав для использования этой команды!")
            return

        server = servers.find_one({'server':ctx.guild.id})
        wl = server['mod']['wlist_members']
        for i in mem:
            if i.id not in wl:
                wl.append(i.id)

        server['mod'].update({'wlist_members': wl})
        servers.update_one({'server':ctx.guild.id},{'$set':{'mod': server['mod']}})
        await ctx.send("Пользователи, на которых не реагирует авто-модерация, добавлены")

    @commands.command(usage = '-', description = 'Список ролей в белом списке модерации.', help = 'Настройка авто-модерации')
    async def wlist_roles(self, ctx):
        server = servers.find_one({'server':ctx.guild.id})
        if server['mod']['wlist_roles'] == []:
            text = 'Пусто'
        else:
            text = ''
            for i in server['mod']['wlist_roles']:
                r = ctx.guild.get_role(i)
                text += f"{r.mention} "

        emb = discord.Embed(title = f'Роли с иммунитетом к авто-моду', description = text, color= server['embed_color'] )
        await ctx.send(embed = emb)


    @commands.command(usage = '-', description = 'Список пользователей в белом списке.', help = 'Настройка авто-модерации')
    async def wlist_members(self, ctx):
        server = servers.find_one({'server':ctx.guild.id})
        if server['mod']['wlist_members'] == []:
            text = 'Пусто'
        else:
            text = ''
            for i in server['mod']['wlist_members']:
                r = ctx.guild.get_member(i)
                text += f"{r.mention} "

        emb = discord.Embed(title = f'Пользователи с иммунитетом к авто-моду', description = text, color= server['embed_color'] )
        await ctx.send(embed = emb)

    @commands.command(usage = '(#channels)', description = 'Добавить медиа-канал.', help = 'Настройка авто-модерации')
    async def add_media_channels(self, ctx, *channel:discord.TextChannel):
        global servers
        if funs.roles_check(ctx.author, ctx.guild.id) == False:
            await ctx.send("У вас недостаточно прав для использования этой команды!")
            return

        server = servers.find_one({'server':ctx.guild.id})
        wl = []
        for i in channel:
            wl.append(i.id)

        server['mod']['media_channels'].update({'channels': wl})
        servers.update_one({'server':ctx.guild.id},{'$set':{'mod': server['mod']}})
        await ctx.send("Каналы с режимом медиа-канал были добавлены.")

    @commands.command(usage = '(punishments)', description = 'Настроить наказание за нарушение в медиа-канале.', help = 'Настройка авто-модерации')
    async def media_channels_pun(self, ctx, *punishment:str):
        global servers
        if funs.roles_check(ctx.author, ctx.guild.id) == False:
            await ctx.send("У вас недостаточно прав для использования этой команды!")
            return

        l = ["ban", "kick", "warn", "message", "delete-all", "delete", "role-add", "role-remove"]

        if punishment == ():
            await ctx.send(f"Выберите из этого списка: {', '.join(l)}")
            return

        pun = []
        for i in punishment:
            if i in l:
                pun.append(i)
        if pun != []:
            server = servers.find_one({'server':ctx.guild.id})
            server['mod']['media_channels'].update({'punishment': pun})
            servers.update_one({'server':ctx.guild.id},{'$set':{'mod': server["mod"] }})

            if 'message' in pun:
                await ctx.send(f'Пропишите команду {ctx.prefix}media_channels_message\n для настройки сообщения')
                server['mod']['media_channels'].update({'message': None, 'mess-type': None})

            if 'role-add' in pun or "role-remove" in pun:
                await ctx.send(f'Пропишите команду {ctx.prefix}media_channels_role\n для настройки роли')
                server['mod']['media_channels'].update({'add-role': None, 'roleremove': None})

            await ctx.send(f'Наказания настроены')
        else:
            await ctx.send(f'Нету ни одного совпадения с доступными наказаниями')

    @commands.command(usage = '(type) (message)', description = 'Добавить сообщение за нарушение в дмедиа канале.', help = 'Настройка авто-модерации')
    async def media_channels_message(self, ctx, type = None, *message):
        global servers
        if funs.roles_check(ctx.author, ctx.guild.id) == False:
            await ctx.send("У вас недостаточно прав для использования этой команды!")
            return

        server = servers.find_one({'server':ctx.guild.id})
        if type == None:
            await ctx.send(f"{ctx.prefix}media_channels_message (type) (message)\ntype - укажите отображение emb или mes\nmessge - введите сообщени длинной максимум 1500 символов\nПример: {ctx.prefix}bad_words_message emb Ты плохой человек")
        else:
            if type not in ['emb', 'mes']:
                await ctx.send('Требовалось указать emb или mes')
                return
            if len(str(message)) > 1500:
                await ctx.send(f'Требовалось указать сообщение длинной меньше или равной 1500 символов (Сейчас {len(str(message))})')
                return

            server['mod']['bad_words'].update({'mess-type': type, 'message': message})
            servers.update_one({'server':ctx.guild.id},{'$set':{'mod': server['mod']}})
            await ctx.send("Сообщение настроено")

    @commands.command(usage = '(type) (@role)', description = 'Добавить роль за нарушение в медиа канале.', help = 'Настройка авто-модерации')
    async def media_channels_role(self, ctx, type = None, role: discord.Role = None):
        global servers
        if funs.roles_check(ctx.author, ctx.guild.id) == False:
            await ctx.send("У вас недостаточно прав для использования этой команды!")
            return

        server = servers.find_one({'server':ctx.guild.id})
        if type == None:
            await ctx.send(f"{ctx.prefix}bad_words_role (type) (role)\ntype - укажите add или remove\nrole - укажите роль\nПример: {ctx.prefix}bad_words_role add @проказник")
        if role != None:
            if type == 'add':
                server['mod']['media_channels'].update({'add-role': role.id})
                servers.update_one({'server':ctx.guild.id},{'$set':{'mod': server['mod']}})
            if type == 'remove':
                server['mod']['media_channels'].update({'remove-role': role.id})
                servers.update_one({'server':ctx.guild.id},{'$set':{'mod': server['mod']}})

            else:
                await ctx.send(f"{ctx.prefix}media_channels_role (type) (role)\ntype - укажите add или remove\nrole - укажите роль\nПример: {ctx.prefix}bad_words_role add @проказник")
                return

            await ctx.send('Роль настроена')

        else:
            await ctx.send(f"{ctx.prefix}media_channels_role (type) (role)\ntype - укажите add или remove\nrole - укажите роль\nПример: {ctx.prefix}bad_words_role add @проказник")

    @commands.command(usage = '(#channel) (events)', description = 'Установить лог канал.', help = 'Лог')
    async def set_log(self, ctx, channel:discord.TextChannel, *events):
        global servers
        if funs.roles_check(ctx.author, ctx.guild.id) == False:
            await ctx.send("У вас недостаточно прав для использования этой команды!")
            return

        log_events = ['all', 'member', 'member_join', 'member_remove', 'member_status', 'member_nick', 'member_roles', 'member_top_role', 'member_ban', 'member_unban', 'voice', 'voice_connect', 'voice_disconnect', 'voice_reconnect', 'channel', 'channel_name', 'channel_category', 'channel_rights', 'channel_roles', 'channel_permissions_synced', 'channel_position', 'channel_slowmode', 'channel_topic', 'channel_nsfw', 'channel_bitrate', 'channel_rtc_region', 'channel_user_limit', 'channel_create', 'channel_delete', 'emoji', 'emoji_create', 'emoji_delete', 'invite', 'invite_create', 'invite_delete', 'message', 'message_edit', 'message_delete', 'guild', 'guild_afk_channel', 'guild_afk_timeout', 'guild_banner', 'guild_bitrate_limit', 'guild_default_notifications', 'guild_description', 'guild_mfa_level', 'guild_verification_level', 'guild_splash', 'guild_emoji_limit', 'guild_content_filter', 'guild_filesize_limit', 'guild_icon', 'guild_name', 'guild_owner', 'role', 'role_create', 'role_delete', 'role_color', 'role_hoist', 'role_mentionable', 'role_name', 'role_position', 'role_permissions']

        server = servers.find_one({"server": ctx.guild.id})
        lg_ev = []
        for i in events:
            if i in log_events:
                lg_ev.append(i)

        server['mod']['log_channel'].update({'channel': channel.id, 'logging': lg_ev})
        servers.update_one({'server':ctx.guild.id},{'$set':{'mod': server['mod']}})

        await ctx.send(f"Лог канал настроен!")

    @commands.command(usage = '-', description = 'Информация о лог канале.', help = 'Лог')
    async def log_info(self, ctx):
        log_events = ['all', 'member', 'member_join', 'member_remove', 'member_status', 'member_nick', 'member_roles', 'member_top_role', 'member_ban', 'member_unban', 'voice', 'voice_connect', 'voice_disconnect', 'voice_reconnect', 'channel', 'channel_name', 'channel_category', 'channel_rights', 'channel_roles', 'channel_permissions_synced', 'channel_position', 'channel_slowmode', 'channel_topic', 'channel_nsfw', 'channel_bitrate', 'channel_rtc_region', 'channel_user_limit', 'channel_create', 'channel_delete', 'emoji', 'emoji_create', 'emoji_delete', 'invite', 'invite_create', 'invite_delete', 'message', 'message_edit', 'message_delete', 'guild', 'guild_afk_channel', 'guild_afk_timeout', 'guild_banner', 'guild_bitrate_limit', 'guild_default_notifications', 'guild_description', 'guild_mfa_level', 'guild_verification_level', 'guild_splash', 'guild_emoji_limit', 'guild_content_filter', 'guild_filesize_limit', 'guild_icon', 'guild_name', 'guild_owner', 'role', 'role_create', 'role_delete', 'role_color', 'role_hoist', 'role_mentionable', 'role_name', 'role_position', 'role_permissions']

        emb = discord.Embed(title = f'Информация о настройке лог-канала', description =f'{ctx.prefix}set_log (#канал) (*события)',color=0xE52B50 )
        emb.add_field(name = '*события', value = f'Через пробел укажите события из этого списка:\n `{", ".join(log_events)}`', inline = False)
        emb.add_field(name = 'Пример', value = f'{ctx.prefix}set_log {ctx.channel.mention} channel guild member ', inline = False)

        await ctx.send(embed = emb)

    @commands.command(usage = '(#channel) (count)', description = 'Установить доску для пиццы!', help = 'Другие системы')
    async def set_pizza_board(self, ctx, channel:discord.TextChannel, count):
        global servers
        if funs.roles_check(ctx.author, ctx.guild.id) == False:
            await ctx.send("У вас недостаточно прав для использования этой команды!")
            return

        try:
            count = int(count)
        except Exception:
            await ctx.send("Требовалось указать число!")
            return

        if count < 1 or count > 55:
            await ctx.send("Требовалось указать число от 1-го до 55-ти!")
            return

        servers.update_one({'server':ctx.guild.id},{'$set':{'pizza_board': {
        'channel': channel.id,
        'count': count,
        }}})

        await ctx.send("Pizza Board настроен!")

    @commands.command(usage = '[mini] [max] [percent]', description = 'Настроить игру собери 21.', help = 'Настройка экономики')
    async def set_blackjack(self, ctx, mini:int = 100, max:int = 10000, percent:float = 1.25):
        global servers
        if funs.roles_check(ctx.author, ctx.guild.id) == False:
            await ctx.send("У вас недостаточно прав для использования этой команды!")
            return

        server = servers.find_one({"server": ctx.guild.id})

        if mini < 10:
            await ctx.send("Минимальная сумма не может быть меньше 10-ти монет!")
            return

        if max < 20:
            await ctx.send("Максимальная сумма не может быть меньше 20-ти монет!")
            return

        if max < mini:
            await ctx.send("Минимальная сумма не может быть меньше максимальной суммы!")
            return

        server['economy']['games']['blackjack'].update({'mini': mini})
        server['economy']['games']['blackjack'].update({'max': max})
        server['economy']['games']['blackjack'].update({'percent': percent})

        servers.update_one({'server':ctx.guild.id},{'$set':{'economy': server['economy']}})

        await ctx.send(f"Минимальная сумма: {mini}\nМаксимальная сумма: {max}\nУмножение суммы при победе: {percent}" )

    @commands.command(usage = '[mini] [max] [percent]', description = 'Настроить игру слоты.', help = 'Настройка экономики')
    async def set_slots(self, ctx, mini:int = 100, max:int = 10000, percent:float = 1.25):
        global servers
        if funs.roles_check(ctx.author, ctx.guild.id) == False:
            await ctx.send("У вас недостаточно прав для использования этой команды!")
            return

        server = servers.find_one({"server": ctx.guild.id})

        if mini < 10:
            await ctx.send("Минимальная сумма не может быть меньше 10-ти монет!")
            return

        if max < 20:
            await ctx.send("Максимальная сумма не может быть меньше 20-ти монет!")
            return

        if percent < 1.0:
            await ctx.send("Процент не может быть меньше 1%!")
            return

        if max < mini:
            await ctx.send("Минимальная сумма не может быть меньше максимальной суммы!")
            return

        server['economy']['games']['slots'].update({'mini': mini})
        server['economy']['games']['slots'].update({'max': max})
        server['economy']['games']['slots'].update({'percent': percent})

        servers.update_one({'server':ctx.guild.id},{'$set':{'economy': server['economy']}})

        await ctx.send(f"Минимальная сумма: {mini}\nМаксимальная сумма: {max}\nУмножение суммы при победе: {percent}" )

    @commands.command(usage = '[reward] [percent]', description = 'Настроить ежедневную награду.', help = 'Настройка экономики')
    async def set_daily(self, ctx, reward:int = 200, reward_percent:float = 1.05):
        global servers
        if funs.roles_check(ctx.author, ctx.guild.id) == False:
            await ctx.send("У вас недостаточно прав для использования этой команды!")
            return

        if reward < 10:
            await ctx.send("Минимальная сумма не может быть меньше 10-ти монет!")
            return

        if reward_percent < 1.0:
            await ctx.send("Процент не может быть меньше 1%!")
            return

        server['economy']['daily_reward'].update({'reward': reward})
        server['economy']['daily_reward'].update({'reward_percent': reward_percent})

        servers.update_one({'server':ctx.guild.id},{'$set':{'economy': server['economy']}})

        await ctx.send(f"Награда: {reward}\nУмножение суммы: {reward_percent}" )

    @commands.command(usage = '(lvl) (money) (items)', description = 'Настроить награду за голосовую активность.', help = 'Награда за активность в войсе')
    async def add_voice_reward(self, ctx, lvl:int, money:int, *, item:int = None):
        global servers
        if funs.roles_check(ctx.author, ctx.guild.id) == False:
            await ctx.send("У вас недостаточно прав для использования этой команды!")
            return
        if lvl < 0:
            await ctx.send("Награда не может выдаваться раньше первых чем за 1-ый уровень!")
            return
        if money < 0:
            await ctx.send("Монеты не могут быть меньше 0-ля!")
            return

        server = servers.find_one({"server": ctx.guild.id})
        a = server['voice_reward']

        if server['premium'] != True:
            mk = 15
            if len(a.keys()) >= 10:
                await ctx.send("Не имея подписки premium, вы не можете назначить больше 10-ти нагрда за войс! ")
                return

        if server['premium'] == True:
            mk = 40

        if server['premium'] != True:
            if len(a.keys()) >= 20:
                await ctx.send("Нельзя добавить больше 20-ти наград! ")
                return

        items = []
        if item == None:
            items = None
        else:
            for i in item:
                try:
                    server['items'][str(i)]
                    items.append(i)
                except:
                    pass

            if len(items) == 0:
                await ctx.send("Не один из предметов не был найден!")
                return
            if len(items) > mk:
                await ctx.send(f"Нельзя выдать больше {mk} предметов за раз!")
                return

        a.update({ str(time): {'items': items, 'money': money} })
        servers.update_one( {"server": ctx.guild.id}, {"$set": {'voice_reward': a}} )
        await ctx.send(f'Награда за {lvl} уровень голосовой активности, была успешно добавленна!')

    @commands.command(usage = '(lvl)', description = 'Удалить награду за сессию в войсе.', help = 'Награда за активность в войсе')
    async def delete_voice_reward(self,ctx, lvl:int):
        global servers
        if funs.roles_check(ctx.author, ctx.guild.id) == False:
            await ctx.send("У вас недостаточно прав для использования этой команды!")
            return

        server = servers.find_one({"server": ctx.guild.id})

        a = server['voice_reward']

        try:
            del a[str(lvl)]
        except KeyError:
            await ctx.send("Награда за это время не найдено!")
            return

        servers.update_one( {"server": ctx.guild.id}, {"$set": {'voice_reward': a}} )
        await ctx.send(f'Награда за {lvl} уровень была удалена!')

    @commands.command(usage = '-', description = 'Список наград за сессию в войсе.', help = 'Награда за активность в войсе')
    async def vr_list(self,ctx):
        global servers
        server = servers.find_one({'server':ctx.guild.id})

        if server['voice_reward'] == {}:
            await ctx.send("Тут пусто! 😯")
            return

        solutions = ['◀', '▶', '❌']
        member = ctx.author
        reaction = 'a'
        numberpage = 1

        keys = []
        for i in list(server['voice_reward'].keys()):
            keys.append(int(i))
        keys = sorted(keys)

        if len(keys) % 6 != 0:
            l = int(len(keys) / 6 + 1)
        else:
            l = int(len(keys) / 6)

        def top_embed(numberpage):
            nonlocal ctx
            nonlocal l

            num1 = 0
            num2 = 0
            page = numberpage
            text = ''

            if numberpage != 1:
                numberpage *= 6
                numberpage -= 6

                if numberpage > 5:
                    numberpage += 1

            if len(keys) <= 6:
                emb = discord.Embed(title = 'Награды за активность в войсе', description = 'Нагрда выдаётся если вы провили в войсе определённое количество врмени, за 1 сеанс',color=server['embed_color'])
                for i in keys:
                    ii = []
                    for n in server['voice_reward'][str(i)]['items']:
                        ii.append(server['items'][str(n)]['name'])

                    mr = server['voice_reward'][str(i)]['money']

                    emb.add_field(name = f"Время в войсе {i}", value = f"Предметы: {', '.join(ii)}\nМонеты: {mr}")

            elif len(keys) > 6:
                emb = discord.Embed(title = 'Награды за активность в войсе', description = 'Нагрда выдаётся если вы провили в войсе определённое количество врмени, за 1 сеанс',color=server['embed_color'])
                for i in keys:
                    num1 += 1
                    if num1 >= numberpage and num2 < 5:
                        num2 += 1

                        ii = []
                        for n in server['voice_reward'][str(i)]['items']:
                            ii.append(server['items'][str(n)]['name'])

                        mr = server['voice_reward'][str(i)]['money']

                        emb.add_field(name = f"Уровень {i}", value = f"Предметы: {', '.join(ii)}\nМонеты: {mr}")


            emb.set_footer(text=f"Страница {page}/{l}")
            return emb

        msg = await ctx.send(embed = top_embed(numberpage))

        def check( reaction, user):
            nonlocal msg
            return user == ctx.author and str(reaction.emoji) in solutions and str(reaction.message) == str(msg)

        async def rr():
            nonlocal reaction
            nonlocal numberpage
            nonlocal l
            if str(reaction.emoji) == '◀':
                await msg.remove_reaction('◀', member)
                numberpage -= 1
                if numberpage < 1:
                    numberpage = 1

                await msg.edit(embed = top_embed(numberpage))


            elif str(reaction.emoji) == '▶':
                await msg.remove_reaction('▶', member)
                numberpage += 1
                if numberpage > l:
                    numberpage = l

                await msg.edit(embed = top_embed(numberpage))


            elif str(reaction.emoji) == '❌':
                await msg.clear_reactions()
                return

        async def reackt():
            nonlocal reaction
            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=30.0, check = check)
            except asyncio.TimeoutError:
                await msg.clear_reactions()
            else:
                await rr(), await reackt()

        if len(keys) > 6:
            for x in solutions:
                await msg.add_reaction(x)
            await reackt()

    @commands.command(usage = '[#channel] [category] [message]', description = 'Настроить систему тикетов.', help = 'Другие системы')
    async def set_tickets(self, ctx, channel:discord.TextChannel = None, category:int = None, *, message = None):
        global servers
        if funs.roles_check(ctx.author, ctx.guild.id) == False:
            await ctx.send("У вас недостаточно прав для использования этой команды!")
            return

        server = servers.find_one({"server": ctx.guild.id})

        if category == None:
            overwrites = {
                    ctx.guild.default_role: discord.PermissionOverwrite(view_channel=False, send_messages=False)
                         }
            cat = await ctx.guild.create_category('Tickets', overwrites = overwrites)
            category = cat.id
            if channel == None:
                channel = await ctx.guild.create_text_channel(name=f"tickets", category=cat)

        c = ctx.guild.get_channel(category)
        if c == None or type(c) != discord.CategoryChannel:
            await ctx.send(f"Требовалось указать id категории, укажите правильный, либо не указывайте этот аргумент. Категория создастся автоматически!")
            return

        if message == None:
            message = "Для создлания тикета, нажмите 💬"
        else:
            if len(message) > 2000:
                await ctx.send(f"Укажите сообщение меньше 2к симовлов!")
                return

        emb = discord.Embed(title = f'', description = f'{message}', color=server['embed_color'] )
        msg = await channel.send(embed = emb)
        await msg.add_reaction('💬')

        await ctx.send(f"Тикеты настроены!")

        server['tickets'].update({'t_message': msg.id})
        server['tickets'].update({'category': category})
        server['tickets'].update({'tick': {} })
        server['tickets'].update({'t_n': 0 })
        servers.update_one({'server':ctx.guild.id},{'$set':{'tickets': server['tickets']}})

    @commands.command(usage = '[mini] [max]', description = 'Настроить игру шанс.', help = 'Настройка экономики')
    async def set_chance(self, ctx, mini:int = 100, max:int = 10000):
        global servers
        if funs.roles_check(ctx.author, ctx.guild.id) == False:
            await ctx.send("У вас недостаточно прав для использования этой команды!")
            return

        server = servers.find_one({"server": ctx.guild.id})

        if mini < 10:
            await ctx.send("Минимальная сумма не может быть меньше 10-ти монет!")
            return

        if max < 20:
            await ctx.send("Максимальная сумма не может быть меньше 20-ти монет!")
            return

        if max < mini:
            await ctx.send("Минимальная сумма не может быть меньше максимальной суммы!")
            return

        server['economy']['games']['chance'].update({'mini': mini})
        server['economy']['games']['chance'].update({'max': max})

        servers.update_one({'server':ctx.guild.id},{'$set':{'economy': server['economy']}})

        await ctx.send(f"Минимальная сумма: {mini}\nМаксимальная сумма: {max}" )

    @commands.command(usage = '(hex color)', description = 'Настроить цвет всех эмбетов.', help = 'Другие системы')
    async def embed_color(self, ctx, color):
        global servers
        if funs.roles_check(ctx.author, ctx.guild.id) == False:
            await ctx.send("У вас недостаточно прав для использования этой команды!")
            return
        try:

            emb = discord.Embed(description = 'Тестовое сообщение',color = int(color, 16) )
            status = True
            msg = await ctx.send(embed = emb)

            try:
                await msg.delete()
            except Exception:
                pass

        except Exception:
            status = False

        if status == True:
            servers.update_one({'server':ctx.guild.id},{'$set':{'embed_color': color}})
            await ctx.send("Цвет установлен!")


        else:
            await ctx.send("Требовалось указать цвет в формате hex, его можно посмотерть например тут https://csscolor.ru/")
            return

    @commands.command(usage = '(hex color\-) (message)', description = 'Написать от имени бота.')
    async def embed(self, ctx, color, *, message = None):
        global servers
        if funs.roles_check(ctx.author, ctx.guild.id) == False:
            await ctx.send("У вас недостаточно прав для использования этой команды!")
            return
        server = servers.find_one({'server':ctx.guild.id})

        if message == None:
            await ctx.send("Укажите сообщение!")
            return

        if color == '-':
            color = server['embed_color']
            status = True

            emb = discord.Embed(description = f"{''.join(message)}", color = color)
            msg = await ctx.send(embed = emb)

        else:
            try:

                emb = discord.Embed(description = 'Тестовое сообщение',color = int(color, 16) )
                status = True

            except Exception:
                status = False

            if status == True:
                emb = discord.Embed(description = f"{''.join(message)}", color = int(color, 16) )
                msg = await ctx.send(embed = emb)

            else:
                await ctx.send("Требовалось указать цвет в формате hex, его можно посмотерть например тут https://csscolor.ru/")
                return

    @commands.command(usage = '(xp)', description = 'Установка максимального опыта за сообщение.', help = 'Настройка экономики')
    async def set_xp(self, ctx, xp:str):
        global servers
        if funs.roles_check(ctx.author, ctx.guild.id) == False:
            await ctx.send("У вас недостаточно прав для использования этой команды!")
            return
        if xp < 1:
            await ctx.send("Опыт за уровень не может быть меньше чем 1!")
            return

        server = servers.find_one({'server':ctx.guild.id})
        a = server['economy'].copy()
        a.update({"lvl_xp": xp})

        servers.update_one({'server':ctx.guild.id},{'$set':{'economy': a}})
        await ctx.send(f"Опыт за уровень установлен!")

    @commands.command(usage = '(amout)', description = 'Установка начальной суммы монет.', help = 'Настройка экономики')
    async def start_money(self, ctx, amout:str):
        global servers
        if funs.roles_check(ctx.author, ctx.guild.id) == False:
            await ctx.send("У вас недостаточно прав для использования этой команды!")
            return
        if amout < 0:
            await ctx.send("Стартовый капитал не может быть меньше 0!")
            return

        server = servers.find_one({'server':ctx.guild.id})
        a = server['economy'].copy()
        a.update({"start_money": amout})

        servers.update_one({'server':ctx.guild.id},{'$set':{'economy': a}})
        await ctx.send(f"Стартовый капитал установлен!")




    # @commands.command(aliases = ['settings', 'sboard', 'sb'])
    # async def info_board(self, ctx):
    #     server = servers.find_one({"server": ctx.guild.id})
    #     emb = discord.Embed(description = '**Информационная панель**', color= server['embed_color'] )
    #
    #     emb.add_field(name = '| Префикс', value = f"{server['prefix']}\n**| Команда настройки**\n{ctx.prefix}it_prefix", inline = True)
    #
    #     if server['voice']['voice_channel'] != None:
    #         v_cat = ctx.guild.get_channel(server['voice']['voice_category'])
    #         emb.add_field(name = '| Приватные-войсы', value = f"Категория: {v_cat.name}\nКанал: <#{server['voice']['voice_channel']}>", inline = True)
    #
    #         emb.add_field(name = '| Команды приватных-войсов', value = f"{ctx.prefix}setvoicechannel\n{ctx.prefix}clearvoicechannel", inline = True)
    #
    #     if server['upsend_sett']['upsend'] != None:
    #         emb.add_field(name = '| Роли за уровень', value = f"Канал: <#{server['upsend_sett']['upsend']}>\nЭмбет: {server['upsend_sett']['emb_st']}\nРоли: 1️⃣".replace('True','<:n:869159450588635196>').replace('False','<:f:869169592201777224>'), inline = True)
    #
    #         if server['upsend_sett']['up_message'] != None:
    #             emb.add_field(name = '| Сообщение за уровень', value = f"`{server['upsend_sett']['up_message']}`", inline = True)
    #
    #         emb.add_field(name = '| Команды ролей за уровень', value = f"{ctx.prefix}setupchannel\n{ctx.prefix}addup", inline = True)
    #
    #         emb.add_field(name = '| ', value = f"{ctx.prefix}upoff\n{ctx.prefix}deleteup", inline = True)
    #
    #
    #     if server['welcome'] != {}:
    #         emb.add_field(name = '| Вход', value = f"Канал: <#{server['send']['joinsend']}>\nИзображение: [Ссылка]({server['send']['avatar_join_url']})\nТип: {server['send']['join_position_avatar']}", inline = True)
    #         emb.add_field(name = '| Изображение входа', value = f"Цвет welcome: {server['welcome']['wel_fill']}\nЦвет имени: {server['welcome']['nam_fill']}\nЦвет рамки: {server['welcome']['el_fill']}\nТекст: `{server['welcome']['wel_text']}`", inline = True)
    #         emb.add_field(name = '| Команды входа', value = f"{ctx.prefix}set_join\n{ctx.prefix}set_join_channel", inline = True)
    #     else:
    #         emb.add_field(name = '| Вход', value = f"Вход не настроен", inline = True)
    #
    #     if server['goodbye'] != {}:
    #         emb.add_field(name = '| Выход', value = f"Канал: <#{server['send']['leavensend']}>\nИзображение: [Ссылка]({server['send']['avatar_leave_url']})\nТип: {server['send']['leave_position_avatar']}", inline = True)
    #         emb.add_field(name = '| Изображение выхода', value = f"Цвет goodbye: {server['goodbye']['wel_fill_l']}\nЦвет имени: {server['goodbye']['nam_fill_l']}\nЦвет рамки: {server['goodbye']['el_fill_l']}\nТекст: `{server['goodbye']['lea_text']}`", inline = True)
    #         emb.add_field(name = '| Команды выхода', value = f"{ctx.prefix}set_leave\n{ctx.prefix}set_leave_channel", inline = True)
    #     else:
    #         emb.add_field(name = '| Выход', value = f"Выход не настроен", inline = True)
    #
    #     if server['emoji']['emoji_channel'] != None:
    #         emb.add_field(name = '| Канал с эмоджи', value = f"Канал: <#{server['emoji']['emoji_channel']}>", inline = True)
    #         emb.add_field(name = '| Эмоджи', value = f"Эмоджи: {' '.join(server['emoji']['emojis'])}>", inline = True)
    #         emb.add_field(name = '| Команды эмоджи-канала', value = f"{ctx.prefix}set_emoji_channel", inline = True)
    #
    #
    #     await ctx.send(embed = emb)


def setup(bot):
    bot.add_cog(settings(bot))
