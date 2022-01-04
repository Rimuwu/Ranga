import nextcord as discord
from nextcord.ext import tasks, commands
from PIL import Image, ImageFont, ImageDraw, ImageOps
import io
import sys
import random
from random import choice
import asyncio
import time
import pymongo
from fuzzywuzzy import fuzz
import pprint as pprint

sys.path.append("..")
from ai3 import functions as funs
import config


client = funs.mongo_c()
db = client.bot
backs = db.bs
servers = db.servers


class rpg(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(usage = '-', description = 'Создание предмета.')
    async def create_item(self, ctx):
        if funs.roles_check(ctx.author, ctx.guild.id) == False:
            await ctx.send("У вас недостаточно прав для использования этой команды!")
            return

        async def name_f(message, ctx):
            try:
                msg = await self.bot.wait_for('message', timeout=60.0, check=lambda message: message.author == ctx.author and message.channel.id == ctx.channel.id)
            except asyncio.TimeoutError:
                await ctx.send("Время вышло.")
                return False
            else:
                try:
                    await msg.delete()
                except Exception:
                    pass

                if len(message.content) > 150:
                    await ctx.send("Название больше 150-ти символов")
                    return False
                else:
                    return msg.content

        async def act_f(message, ctx):
            try:
                msg = await self.bot.wait_for('message', timeout=60.0, check=lambda message: message.author == ctx.author and message.channel.id == ctx.channel.id)
            except asyncio.TimeoutError:
                await ctx.send("Время вышло.")
                return False
            else:
                try:
                    await msg.delete()
                except Exception:
                    pass

                try:
                    return int(msg.content)
                except Exception:
                    await ctx.send("Требовалось указать __число__!")
                    return False

        async def image_f(message, ctx):
            try:
                text = "Требуется указать __ссылку__ на изображение или `none`"
                emb = discord.Embed(title = "Изображение:",
                description = text, color=server['embed_color'])
                msg1 = await ctx.send(embed = emb)
                msg = await self.bot.wait_for('message', timeout=60.0, check=lambda message: message.author == ctx.author and message.channel.id == ctx.channel.id)
            except asyncio.TimeoutError:
                await ctx.send("Время вышло.")
                return False
            else:
                try:
                    await msg.delete()
                except Exception:
                    pass

                if msg.content != 'none':
                    try:
                        emb1 = discord.Embed(title = "Изображение", color=server['embed_color'])
                        emb1.set_thumbnail(url = msg.content)
                        msg2 = await ctx.send(embed = emb1)
                        image = msg.content
                    except Exception:
                        await ctx.send("Требовалось указать __ссылку__, повторите настройку ещё раз.")
                        return False
                if msg.content == 'none':
                    image = None
                try:
                    await msg1.delete()
                    await msg2.delete()
                except Exception:
                    pass

                return image

        async def quality_f(message, ctx):
            try:
                text = "**Качество предмета влияет на процент его выпадения и крафта**\n`n` - <:normal_q:781531816993620001>(normal) обычное качество, шанс выпадения/крафта 100%\n`u` - <:unusual_q:781531868780691476>(unusual) необычное качество, шанс выпадения/крафта 75%\n`r` - <:rare_q:781531919140651048>(rare) редкое качесвто, шанс выпадения/крафта 50%\n`o` - <:orate_q:781531996866084874>(orate) оратное качество, шанс выпадения/крафта 25%\n`l` - <:legendary_q:781532085130100737>(legendary) легендарное качество, шанс выпадения/крафта 10%"
                emb = discord.Embed(title = "Качества:",
                description = text, color=server['embed_color'])
                msg1 = await ctx.send(embed = emb)
                msg = await self.bot.wait_for('message', timeout=60.0, check=lambda message: message.author == ctx.author and message.channel.id == ctx.channel.id)
            except asyncio.TimeoutError:
                await ctx.send("Время вышло.")
                return False
            else:
                try:
                    await msg1.delete()
                    await msg.delete()
                except Exception:
                    pass

                if msg.content in ['n', 'normal', 'u', 'unusual', 'r', 'rare', 'o', 'orate', 'l', 'legendary']:
                    if msg.content in ['n', 'normal']:
                        quality = "n"
                    elif msg.content in ['u', 'un normal']:
                        quality = "u"
                    elif msg.content in ['r', 'rare']:
                        quality = "r"
                    elif msg.content in ['o', 'orate',]:
                        quality = "o"
                    elif msg.content in ['l', 'legendary',]:
                        quality = "l"
                    return quality
                else:
                    await ctx.send("Вы указали не действительное качество предмета, выберите 1 из (n, u, r, o, l) и повторите создание снова!")
                    return False

        async def description_f(message, ctx):
            try:
                msg = await self.bot.wait_for('message', timeout=60.0, check=lambda message: message.author == ctx.author and message.channel.id == ctx.channel.id)
            except asyncio.TimeoutError:
                await ctx.send("Время вышло.")
                return False
            else:
                try:
                    await msg.delete()
                except Exception:
                    pass
                description = str(msg.content)
                if description == 'none':
                    return None
                elif len(description) > 0 and len(description) < 501:
                    return msg.content
                else:
                    await ctx.send("Требовалось указать описание (макс 500 символов) или `none`, повторите настройку ещё раз!")
                    return False

        async def action_m_f(message, ctx):
            try:
                msg = await self.bot.wait_for('message', timeout=60.0, check=lambda message: message.author == ctx.author and message.channel.id == ctx.channel.id)
            except asyncio.TimeoutError:
                await ctx.send("Время вышло.")
                return False
            else:
                try:
                    await msg.delete()
                except Exception:
                    pass
                description = str(msg.content)
                if description == 'none':
                    return None
                elif len(description) > 0 and len(description) < 501:
                    return msg.content
                else:
                    await ctx.send("Требовалось указать описание (макс 500 символов) или `none`, повторите настройку ещё раз!")
                    return False

        async def race_u_f(message, ctx, server):
            try:
                msg = await self.bot.wait_for('message', timeout=60.0, check=lambda message: message.author == ctx.author and message.channel.id == ctx.channel.id)
            except asyncio.TimeoutError:
                await ctx.send("Время вышло.")
                return False
            else:
                try:
                    await msg.delete()
                except Exception:
                    pass

                if msg.content == 'all' or msg.content == 'none':
                    return None
                else:
                    races = list(server['races'].keys())
                    c_races = msg.content.split()
                    s = list(set(races) & set(c_races))
                    if s == []:
                        await ctx.send("Не найдено ни одного совпадения с созданными расами!")
                        return False
                    else:
                        return s

        async def element_f(message, ctx):
            try:
                text = "`w` - <:water:888029916287885332>(water) Огонь >`х0.75`> Вода >`х1.25`> Земля\n`a` -  <:air:888029789749919787>(air) Земля >`х0.75`> Воздух >`х1.25`> Огонь\n`f` - <:fire:888029761828425789>(fire) Воздух >`х0.75`> Огонь >`х1.25`> Вода\n`e` - <:earth:888029840945598534>(earth) Вода >`х0.75`> Земля >`х1.25`> Воздух\n\n<:fire:888029761828425789> >`х1.25`> <:water:888029916287885332> >`х1.25`> <:earth:888029840945598534> >`х1.25`> <:air:888029789749919787> >`х1.25`> <:fire:888029761828425789>\n\nУкажите `none` если у предмета нет стихии."
                emb = discord.Embed(title = "Элементы:",
                description = text, color=server['embed_color'])
                msg1 = await ctx.send(embed = emb)
                msg = await self.bot.wait_for('message', timeout=60.0, check=lambda message: message.author == ctx.author and message.channel.id == ctx.channel.id)
            except asyncio.TimeoutError:
                await ctx.send("Время вышло.")
                return False
            else:
                try:
                    await msg1.delete()
                    await msg.delete()
                except Exception:
                    pass

                if msg.content in ['fire', 'water', 'air', 'earth', 'none', 'w', 'a', 'f', 'e']:

                    if msg.content in ['w', 'water']:
                        el = "w"
                    elif msg.content in ['a', 'air']:
                        el = "a"
                    elif msg.content in ['f', 'fire']:
                        el = "f"
                    elif msg.content in ['e', 'earth',]:
                        el = "e"
                    elif msg.content in ['none']:
                        el = None

                    return el

                else:
                    await ctx.send("Требовалось указать 1 из элементов! (w, a, f, e)")
                    return False

        async def emoji_f(message, ctx):
            try:
                msg = await self.bot.wait_for('message', timeout=60.0, check=lambda message: message.author == ctx.author and message.channel.id == ctx.channel.id)
            except asyncio.TimeoutError:
                await ctx.send("Время вышло.")
                return False
            else:
                try:
                    await msg.delete()
                except Exception:
                    pass

                test_msg = await ctx.send("Тестовое сообщение\n Не удаляйте его, оно быдут удалено автоматически при наличии прав у бота")
                list = []

                try:
                    await test_msg.add_reaction(msg.content)
                except Exception:
                    await ctx.send("Требовалось указать :emoji:")
                    return False

                try:
                    await test_msg.delete()
                except Exception:
                    pass

                return msg.content



        server = servers.find_one({"server": ctx.guild.id})

        item = {}

        def embed(type = 'Не указано'):
            nonlocal server

            emb = discord.Embed(description = "**Создание предмета**", color=server['embed_color'])
            emb.add_field(name = "Тип предмета", value = f"{type}")
            emb.set_footer(text = 'Отправляйте сообщения в чат без использованеи команд, на одно указание у вас 60 сек.')
            return emb

        message = await ctx.send(embed = embed())

        try:
            await message.edit(embed = embed(f'Укажите тип предмета: '))
            emb = discord.Embed(title = "Типы:",
            description = "`eat` - еда, воостанавливает или отнимает у пользователя здоровье при использовании\n`point` - зелья здоровья или маны\n`case` - сундуки с случайным предметом\n`armor` - броня, при использовании устанавливает броню\n`weapon` - оружие, может быть: дальнобойного, ближнего и магического стиля.\n`pet` - питомец\n`material` - материал, его нельзя взять в руки или съесть, но если вам надо создать руду или стрелы, вам сюда.\n`recipe` - рецепт для крафта\n`role` - роль, при использовании выдаёт роль\n`prop` - не играбельный предмет, выполняющий функцию декорации", color=server['embed_color'])
            msg1 = await ctx.send(embed = emb)
            msg = await self.bot.wait_for('message', timeout=60.0, check=lambda message: message.author == ctx.author and message.channel.id == ctx.channel.id)
        except asyncio.TimeoutError:
            await ctx.send("Время вышло.")
            return
        else:
            try:
                await msg1.delete()
                await msg.delete()
            except Exception:
                pass
            if msg.content in ['eat','point','case','armor','weapon','pet',"material",'recipe','role','prop']:

                item.update({ 'type': msg.content})

            else:
                await ctx.send("Вы указали не действительный тип предмета, выберите 1 из (eat, point, case, armor, weapon, pet, material, recipe, role, prop) и повторите создание снова!")
                return

            type = msg.content

        if type == 'eat':

            def embed(type = 'Не указано', name = 'Не указано', act = 'Не указано', image = 'Не указано', quality = 'Не указано', description = 'Не указано', action_m = 'Не указано', race_u = 'Не указано', element = 'Не указано', emoji_v = 'Не указано'):
                nonlocal server

                emb = discord.Embed(title = "Создание предмета", description = "", color=server['embed_color'])
                emb.add_field(name = "Тип предмета", value = f"{type}")
                emb.add_field(name = "Имя предмета", value = f"{name}")
                emb.add_field(name = "Питательность предмета", value = f"{act}")
                if image != 'Не указано' and image != 'none' and image != "Укажите изображение предмета:" and image != None:
                    emb.set_thumbnail(url = image)
                emb.add_field(name = "Качество предмета", value = f"{quality}")
                emb.add_field(name = "Описание предмета", value = f"{description}")
                emb.add_field(name = "Сообщение при активации", value = f"{action_m}")

                if race_u != 'Не указано' and race_u != 'Укажите названия рас, которые могут использовать этот предмет или `all`:' and race_u != 'all' and race_u != None:
                    emb.add_field(name = "Расы с возможностью использовать", value = f"{','.join(str(x) for x in race_u)}")
                else:
                    emb.add_field(name = "Расы с возможностью использовать", value = f"{race_u}")

                emb.add_field(name = "Элемент", value = f"{element}")
                emb.add_field(name = "Эмоджи", value = f"{emoji_v}")

                emb.set_footer(text = 'Отправляйте сообщения в чат без использованеи команд, на одно указание у вас 60 сек.')
                return emb

            await message.edit(embed = embed(type, f'Укажите название предмета: (не более 150 символов)'))
            name = await name_f(message, ctx)
            if name == False:
                return
            else:
                item.update({ 'name': name})

            await message.edit(embed = embed(type, name, f"Укажите питательность `{name}`"))
            act = await act_f(message, ctx)
            if act == False:
                return
            else:
                item.update({ 'act': act})

            await message.edit(embed = embed(type, name, act, "Укажите изображение предмета:"))
            image = await image_f(message, ctx)
            if image == False:
                return
            else:
                item.update({'image': image})

            await message.edit(embed = embed(type, name, act, image, f"Укажите качество предмета: "))
            quality = await quality_f(message, ctx)
            if quality == False:
                return
            else:
                item.update({'quality': quality})

            await message.edit(embed = embed(type, name, act, image, quality, f'Укажите описание предмета или `none`: (макс 500 символов)'))
            description = await description_f(message, ctx)
            if description == False:
                return
            else:
                item.update({'description': description})

            await message.edit(embed = embed(type, name, act, image, quality, description, f'Укажите описание предмета или `none`: (макс 2000 символов)'))
            action_m = await action_m_f(message, ctx)
            if action_m == False:
                return
            else:
                item.update({'action_m': action_m})

            await message.edit(embed = embed(type, name, act, image, quality, description, action_m, f'Укажите названия рас, которые могут использовать этот предмет или `all`:'))
            race_u = await race_u_f(message, ctx, server)
            if race_u == False:
                return
            else:
                item.update({'race_u': race_u})

            await message.edit(embed = embed(type, name, act, image, quality, description, action_m, race_u, f'Укажите элеменет или `none`:'))
            element = await element_f(message, ctx)
            if element == False:
                return
            else:
                item.update({'element': element})

            await message.edit(embed = embed(type, name, act, image, quality, description, action_m, race_u, element, f'Укажите эмоджи предмета:'))
            emoji_v = await emoji_f(message, ctx)
            if emoji_v == False:
                return
            else:
                item.update({'emoji': emoji_v})


            await message.edit(embed = embed( type, name, act, image, quality, description, action_m, race_u, element, emoji_v))

        elif type == 'point':

            def embed(type = 'Не указано', name = 'Не указано', act = 'Не указано', style = 'Не указано', image = 'Не указано', quality = 'Не указано', description = 'Не указано', action_m = 'Не указано', race_u = 'Не указано', emoji_v = 'Не указано'):
                nonlocal server

                emb = discord.Embed(title = "Создание предмета", description = "", color=server['embed_color'])
                emb.add_field(name = "Тип предмета", value = f"{type}")
                emb.add_field(name = "Имя предмета", value = f"{name}")
                emb.add_field(name = "Мощность предмета", value = f"{act}")
                emb.add_field(name = "Стиль предмета", value = f"{style}")
                if image != 'Не указано' and image != 'none' and image != "Укажите изображение предмета:" and image != None:
                    emb.set_thumbnail(url = image)
                emb.add_field(name = "Качество предмета", value = f"{quality}")
                emb.add_field(name = "Описание предмета", value = f"{description}")
                emb.add_field(name = "Сообщение при активации", value = f"{action_m}")

                if race_u != 'Не указано' and race_u != 'Укажите названия рас, которые могут использовать этот предмет или `all`:' and race_u != 'all' and race_u != None:
                    emb.add_field(name = "Расы с возможностью использовать", value = f"{','.join(str(x) for x in race_u)}")
                else:
                    emb.add_field(name = "Расы с возможностью использовать", value = f"{race_u}")

                emb.add_field(name = "Эмоджи", value = f"{emoji_v}")

                emb.set_footer(text = 'Отправляйте сообщения в чат без использованеи команд, на одно указание у вас 60 сек.')
                return emb

            await message.edit(embed = embed(type, f'Укажите название предмета: (не более 150 символов)'))
            name = await name_f(message, ctx)
            if name == False:
                return
            else:
                item.update({ 'name': name})

            await message.edit(embed = embed(type, name, f"Укажите мощность `{name}`"))
            act = await act_f(message, ctx)
            if act == False:
                return
            else:
                item.update({ 'act': act})

            text = "`heal` - при использовании зелья, восстановит здоровье пользователя.\n`mana` - при использовании зелья, восстановит ману пользователя."

            try:
                emb = discord.Embed(title = "Стили:",
                description = text, color=server['embed_color'])
                msg1 = await ctx.send(embed = emb)
                await message.edit(embed = embed(type, name, act, f"Укажите стиль `{name}`"))
                msg = await self.bot.wait_for('message', timeout=60.0, check=lambda message: message.author == ctx.author and message.channel.id == ctx.channel.id)
            except asyncio.TimeoutError:
                await ctx.send("Время вышло.")
                return
            else:
                try:
                    await msg.delete()
                    await msg1.delete()
                except Exception:
                    pass

                if msg.content in ['mana', 'heal']:
                    item.update({ 'style': msg.content})
                else:
                    await ctx.send("Вы указали не действительный стиль предмета, выберите 1 из (heal, mana) и повторите создание снова!")
                    return

                style = msg.content

            await message.edit(embed = embed(type, name, act, style, "Укажите изображение предмета:"))
            image = await image_f(message, ctx)
            if image == False:
                return
            else:
                item.update({'image': image})

            await message.edit(embed = embed(type, name, act, style, image, f"Укажите качество предмета: "))
            quality = await quality_f(message, ctx)
            if quality == False:
                return
            else:
                item.update({'quality': quality})

            await message.edit(embed = embed(type, name, act, style, image, quality, f'Укажите описание предмета или `none`: (макс 500 символов)'))
            description = await description_f(message, ctx)
            if description == False:
                return
            else:
                item.update({'description': description})

            await message.edit(embed = embed(type, name, act, style, image, quality, description, f'Укажите описание предмета или `none`: (макс 2000 символов)'))
            action_m = await action_m_f(message, ctx)
            if action_m == False:
                return
            else:
                item.update({'action_m': action_m})

            await message.edit(embed = embed(type, name, act, style, image, quality, description, action_m, f'Укажите названия рас, которые могут использовать этот предмет или `all`:'))
            race_u = await race_u_f(message, ctx, server)
            if race_u == False:
                return
            else:
                item.update({'race_u': race_u})

            await message.edit(embed = embed(type, name, act, style, image, quality, description, action_m, race_u, f'Укажите эмоджи предмета:'))
            emoji_v = await emoji_f(message, ctx)
            if emoji_v == False:
                return
            else:
                item.update({'emoji': emoji_v})

            await message.edit(embed = embed( type, name, act, style, image, quality, description, action_m, race_u, emoji_v))

        elif type == 'case':

            def embed(type = 'Не указано', name = 'Не указано', act = 'Не указано', image = 'Не указано', quality = 'Не указано', description = 'Не указано', action_m = 'Не указано', race_u = 'Не указано', emoji_v = 'Не указано'):
                nonlocal server

                emb = discord.Embed(title = "Создание предмета", description = "", color=server['embed_color'])
                emb.add_field(name = "Тип предмета", value = f"{type}")
                emb.add_field(name = "Имя предмета", value = f"{name}")

                if act != 'Не указано' and act != f"Укажите id предметов выпадаемые из `{name}`\nПример: 16 52 13" and act != None:
                    emb.add_field(name = "Выпадаемые предметы", value = f"{','.join(str(x) for x in act)}")
                else:
                    emb.add_field(name = "Выпадаемые предметы", value = f"{act}")

                if image != 'Не указано' and image != 'none' and image != "Укажите изображение предмета:" and image != None:
                    emb.set_thumbnail(url = image)
                emb.add_field(name = "Качество предмета", value = f"{quality}")
                emb.add_field(name = "Описание предмета", value = f"{description}")
                emb.add_field(name = "Сообщение при активации", value = f"{action_m}")

                if race_u != 'Не указано' and race_u != 'Укажите названия рас, которые могут использовать этот предмет или `all`:' and race_u != 'all' and race_u != None:
                    emb.add_field(name = "Расы с возможностью использовать", value = f"{','.join(str(x) for x in race_u)}")
                else:
                    emb.add_field(name = "Расы с возможностью использовать", value = f"{race_u}")

                emb.add_field(name = "Эмоджи", value = f"{emoji_v}")

                emb.set_footer(text = 'Отправляйте сообщения в чат без использованеи команд, на одно указание у вас 60 сек.')
                return emb

            await message.edit(embed = embed(type, f'Укажите название предмета: (не более 150 символов)'))
            name = await name_f(message, ctx)
            if name == False:
                return
            else:
                item.update({ 'name': name})

            try:
                await message.edit(embed = embed(type, name, f"Укажите id предметов выпадаемые из `{name}`\nПример: 16 52 13"))
                msg = await self.bot.wait_for('message', timeout=60.0, check=lambda message: message.author == ctx.author and message.channel.id == ctx.channel.id)
            except asyncio.TimeoutError:
                await ctx.send("Время вышло.")
                return
            else:
                try:
                    await msg.delete()
                except Exception:
                    pass

                act = []
                try:
                    try:
                        act1 = msg.content.split()
                        for i in act1:
                            act.append(int(i))
                    except Exception:
                        await ctx.send("Требовалось указать __число__, повторите настройку ещё раз.")
                        return
                    for i in act:
                        server['items'][str(i)]
                except Exception:
                    await ctx.send("Требовалось указать __id__ (число) существующего предмета, повторите настройку ещё раз.")
                    return


                item.update({ 'act': act })

            await message.edit(embed = embed(type, name, act, "Укажите изображение предмета:"))
            image = await image_f(message, ctx)
            if image == False:
                return
            else:
                item.update({'image': image})

            await message.edit(embed = embed(type, name, act, image, f"Укажите качество предмета: "))
            quality = await quality_f(message, ctx)
            if quality == False:
                return
            else:
                item.update({'quality': quality})

            await message.edit(embed = embed(type, name, act, image, quality, f'Укажите описание предмета или `none`: (макс 500 символов)'))
            description = await description_f(message, ctx)
            if description == False:
                return
            else:
                item.update({'description': description})

            await message.edit(embed = embed(type, name, act, image, quality, description, f'Укажите описание предмета или `none`: (макс 2000 символов)'))
            action_m = await action_m_f(message, ctx)
            if action_m == False:
                return
            else:
                item.update({'action_m': action_m})

            await message.edit(embed = embed(type, name, act, image, quality, description, action_m, f'Укажите названия рас, которые могут использовать этот предмет или `all`:'))
            race_u = await race_u_f(message, ctx, server)
            if race_u == False:
                return
            else:
                item.update({'race_u': race_u})

            await message.edit(embed = embed(type, name, act, image, quality, description, action_m, race_u, f'Укажите эмоджи предмета:'))
            emoji_v = await emoji_f(message, ctx)
            if emoji_v == False:
                return
            else:
                item.update({'emoji': emoji_v})

            await message.edit(embed = embed( type, name, act, image, quality, description, action_m, race_u, emoji_v))

        elif type == 'armor':

            def embed(type = 'Не указано', name = 'Не указано', act = 'Не указано', style = 'Не указано', image = 'Не указано', quality = 'Не указано', description = 'Не указано', action_m = 'Не указано', race_u = 'Не указано', element = 'Не указано', emoji_v = 'Не указано'):
                nonlocal server

                emb = discord.Embed(title = "Создание предмета", description = "", color=server['embed_color'])
                emb.add_field(name = "Тип предмета", value = f"{type}")
                emb.add_field(name = "Имя предмета", value = f"{name}")
                emb.add_field(name = "Защита предмета", value = f"{act}")
                emb.add_field(name = "Стиль предмета", value = f"{style}")
                if image != 'Не указано' and image != 'none' and image != "Укажите изображение предмета:" and image != None:
                    emb.set_thumbnail(url = image)
                emb.add_field(name = "Качество предмета", value = f"{quality}")
                emb.add_field(name = "Описание предмета", value = f"{description}")
                emb.add_field(name = "Сообщение при активации", value = f"{action_m}")

                if race_u != 'Не указано' and race_u != 'Укажите названия рас, которые могут использовать этот предмет или `all`:' and race_u != 'all' and race_u != None:
                    emb.add_field(name = "Расы с возможностью использовать", value = f"{','.join(str(x) for x in race_u)}")
                else:
                    emb.add_field(name = "Расы с возможностью использовать", value = f"{race_u}")

                emb.add_field(name = "Элемент", value = f"{element}")
                emb.add_field(name = "Эмоджи", value = f"{emoji_v}")
                emb.set_footer(text = 'Отправляйте сообщения в чат без использованеи команд, на одно указание у вас 60 сек.')
                return emb


            await message.edit(embed = embed(type, f'Укажите название предмета: (не более 150 символов)'))
            name = await name_f(message, ctx)
            if name == False:
                return
            else:
                item.update({ 'name': name})

            await message.edit(embed = embed(type, name, f"Укажите защиту `{name}`"))
            act = await act_f(message, ctx)
            if act == False:
                return
            else:
                item.update({ 'act': act})

            text = "`add` - при использовании добавляет броню.\n`set` - при использовании устанавливает броню."

            try:
                emb = discord.Embed(title = "Стили:",
                description = text, color=server['embed_color'])
                msg1 = await ctx.send(embed = emb)
                await message.edit(embed = embed(type, name, act, f"Укажите стиль `{name}`"))
                msg = await self.bot.wait_for('message', timeout=60.0, check=lambda message: message.author == ctx.author and message.channel.id == ctx.channel.id)
            except asyncio.TimeoutError:
                await ctx.send("Время вышло.")
                return
            else:
                try:
                    await msg.delete()
                    await msg1.delete()
                except Exception:
                    pass

                if msg.content in ['add', 'set']:
                    item.update({ 'style': msg.content})
                else:
                    await ctx.send("Вы указали не действительный стиль предмета, выберите 1 из (add, set) и повторите создание снова!")
                    return

                style = msg.content

            await message.edit(embed = embed(type, name, act, style, "Укажите изображение предмета:"))
            image = await image_f(message, ctx)
            if image == False:
                return
            else:
                item.update({'image': image})

            await message.edit(embed = embed(type, name, act, style, image, f"Укажите качество предмета: "))
            quality = await quality_f(message, ctx)
            if quality == False:
                return
            else:
                item.update({'quality': quality})

            await message.edit(embed = embed(type, name, act, style, image, quality, f'Укажите описание предмета или `none`: (макс 500 символов)'))
            description = await description_f(message, ctx)
            if description == False:
                return
            else:
                item.update({'description': description})

            await message.edit(embed = embed(type, name, act, style, image, quality, description, f'Укажите описание предмета или `none`: (макс 2000 символов)'))
            action_m = await action_m_f(message, ctx)
            if action_m == False:
                return
            else:
                item.update({'action_m': action_m})

            await message.edit(embed = embed(type, name, act, style, image, quality, description, action_m, f'Укажите названия рас, которые могут использовать этот предмет или `all`:'))
            race_u = await race_u_f(message, ctx, server)
            if race_u == False:
                return
            else:
                item.update({'race_u': race_u})

            await message.edit(embed = embed(type, name, act, style, image, quality, description, action_m, race_u, f'Укажите элеменет или `none`:'))
            element = await element_f(message, ctx)
            if element == False:
                return
            else:
                item.update({'element': element})

            await message.edit(embed = embed(type, name, act, style, image, quality, description, action_m, race_u, element, f'Укажите эмоджи предмета:'))
            emoji_v = await emoji_f(message, ctx)
            if emoji_v == False:
                return
            else:
                item.update({'emoji': emoji_v})

            await message.edit(embed = embed( type, name, act, style, image, quality, description, action_m, race_u, element, emoji_v))


        elif type == 'weapon':

            def embed(type = 'Не указано', name = 'Не указано', act = 'Не указано', style = 'Не указано', image = 'Не указано', quality = 'Не указано', description = 'Не указано', action_m = 'Не указано', race_u = 'Не указано', element = 'Не указано', emoji_v = 'Не указано'):
                nonlocal server

                emb = discord.Embed(title = "Создание предмета", description = "", color=server['embed_color'])
                emb.add_field(name = "Тип предмета", value = f"{type}")
                emb.add_field(name = "Имя предмета", value = f"{name}")
                emb.add_field(name = "Урон предмета", value = f"{act}")
                emb.add_field(name = "Стиль предмета", value = f"{style}")
                if image != 'Не указано' and image != 'none' and image != "Укажите изображение предмета:" and image != None:
                    emb.set_thumbnail(url = image)
                emb.add_field(name = "Качество предмета", value = f"{quality}")
                emb.add_field(name = "Описание предмета", value = f"{description}")
                emb.add_field(name = "Сообщение при активации", value = f"{action_m}")

                if race_u != 'Не указано' and race_u != 'Укажите названия рас, которые могут использовать этот предмет или `all`:' and race_u != 'all' and race_u != None:
                    emb.add_field(name = "Расы с возможностью использовать", value = f"{','.join(str(x) for x in race_u)}")
                else:
                    emb.add_field(name = "Расы с возможностью использовать", value = f"{race_u}")

                emb.add_field(name = "Элемент", value = f"{element}")
                emb.add_field(name = "Эмоджи", value = f"{emoji_v}")

                emb.set_footer(text = 'Отправляйте сообщения в чат без использованеи команд, на одно указание у вас 60 сек.')
                return emb


            await message.edit(embed = embed(type, f'Укажите название предмета: (не более 150 символов)'))
            name = await name_f(message, ctx)
            if name == False:
                return
            else:
                item.update({ 'name': name})

            await message.edit(embed = embed(type, name, f"Укажите урон `{name}`"))
            act = await act_f(message, ctx)
            if act == False:
                return
            else:
                item.update({ 'act': act})

            text = "`sword` - меч\n`staff` - посох (условно, может быть чем угодно), тратит ману при использовании\n`bow` - лук (условно, может быть автоматом или чем угодно) тратит указанный предмет из инвентаря при использовании."

            try:
                emb = discord.Embed(title = "Стили:",
                description = text, color=server['embed_color'])
                msg1 = await ctx.send(embed = emb)
                await message.edit(embed = embed(type, name, act, f"Укажите стиль `{name}`"))
                msg = await self.bot.wait_for('message', timeout=60.0, check=lambda message: message.author == ctx.author and message.channel.id == ctx.channel.id)
            except asyncio.TimeoutError:
                await ctx.send("Время вышло.")
                return
            else:
                try:
                    await msg.delete()
                    await msg1.delete()
                except Exception:
                    pass

                if msg.content in ['sword', 'staff', 'bow']:
                    item.update({ 'style': msg.content})
                else:
                    await ctx.send("Вы указали не действительный стиль предмета, выберите 1 из (sword, staff, bow) и повторите создание снова!")
                    return

                style = msg.content

            if style == 'bow':
                try:
                    mmsg = await ctx.send("Укажите используемый для стрельбы предмет (id):")
                    msg = await self.bot.wait_for('message', timeout=60.0, check=lambda message: message.author == ctx.author and message.channel.id == ctx.channel.id)
                except asyncio.TimeoutError:
                    await ctx.send("Время вышло.")
                    return
                else:
                    try:
                        await msg.delete()
                    except Exception:
                        pass

                    try:
                        iddd = int(msg.content)
                    except:
                        await ctx.send("Требовалось указать число!")
                        return

                    try:
                        server['items'][str(iddd)]
                    except:
                        await ctx.send("Требовалось id существующего предмета!!")
                        return

                    item['bow_item'] = iddd

                    try:
                        await mmsg.edit(content = f'Укажите используемый для стрельбы предмет (id): {iddd}')
                    except:
                        pass

            if style == 'staff':
                try:
                    mmsg = await ctx.send("Укажите количество используемой маны:")
                    msg = await self.bot.wait_for('message', timeout=60.0, check=lambda message: message.author == ctx.author and message.channel.id == ctx.channel.id)
                except asyncio.TimeoutError:
                    await ctx.send("Время вышло.")
                    return
                else:
                    try:
                        await msg.delete()
                    except Exception:
                        pass

                    try:
                        ni = int(msg.content)
                    except:
                        await ctx.send("Требовалось указать число!")
                        return

                    if ni < 0:
                        await ctx.send("Укажите число больше или равное нулю!")
                        return

                    item['mana_use'] = ni

                    try:
                        await mmsg.edit(content = f'Укажите количество используемой маны: {ni}')
                    except:
                        pass

            if style == 'sword':
                try:
                    mmsg = await ctx.send("Укажите прочность (0 - бесконечная прочность):")
                    msg = await self.bot.wait_for('message', timeout=60.0, check=lambda message: message.author == ctx.author and message.channel.id == ctx.channel.id)
                except asyncio.TimeoutError:
                    await ctx.send("Время вышло.")
                    return
                else:
                    try:
                        await msg.delete()
                    except Exception:
                        pass

                    try:
                        ni = int(msg.content)
                    except:
                        await ctx.send("Требовалось указать число!")
                        return

                    if ni < 0:
                        await ctx.send("Укажите число больше или равное нулю!")
                        return


                    item['stabl'] = ni

                    try:
                        await mmsg.edit(content = f'Укажите прочность (0 - бесконечная прочность): {ni}')
                    except:
                        pass


            await message.edit(embed = embed(type, name, act, style, "Укажите изображение предмета:"))
            image = await image_f(message, ctx)
            if image == False:
                return
            else:
                item.update({'image': image})

            await message.edit(embed = embed(type, name, act, style, image, f"Укажите качество предмета: "))
            quality = await quality_f(message, ctx)
            if quality == False:
                return
            else:
                item.update({'quality': quality})

            await message.edit(embed = embed(type, name, act, style, image, quality, f'Укажите описание предмета или `none`: (макс 500 символов)'))
            description = await description_f(message, ctx)
            if description == False:
                return
            else:
                item.update({'description': description})

            await message.edit(embed = embed(type, name, act, style, image, quality, description, f'Укажите описание предмета или `none`: (макс 2000 символов)'))
            action_m = await action_m_f(message, ctx)
            if action_m == False:
                return
            else:
                item.update({'action_m': action_m})

            await message.edit(embed = embed(type, name, act, style, image, quality, description, action_m, f'Укажите названия рас, которые могут использовать этот предмет или `all`:'))
            race_u = await race_u_f(message, ctx, server)
            if race_u == False:
                return
            else:
                item.update({'race_u': race_u})

            await message.edit(embed = embed(type, name, act, style, image, quality, description, action_m, race_u, f'Укажите элеменет или `none`:'))
            element = await element_f(message, ctx)
            if element == False:
                return
            else:
                item.update({'element': element})

            await message.edit(embed = embed(type, name, act, style, image, quality, description, action_m, race_u, element, f'Укажите эмоджи предмета:'))
            emoji_v = await emoji_f(message, ctx)
            if emoji_v == False:
                return
            else:
                item.update({'emoji': emoji_v})

            await message.edit(embed = embed( type, name, act, style, image, quality, description, action_m, race_u, element, emoji_v))

        elif type == 'pet':

            def embed(type = 'Не указано', name = 'Не указано', style = 'Не указано', act = 'Не указано', image = 'Не указано', chance = 'Не указано', damage = 'Не указано', quality = 'Не указано', description = 'Не указано', action_m = 'Не указано', race_u = 'Не указано', element = 'Не указано', emoji_v = 'Не указано'):

                emb = discord.Embed(title = "Создание предмета", description = "", color=server['embed_color'])
                emb.add_field(name = "Тип", value = f"{type}")
                emb.add_field(name = "Имя питомца", value = f"{name}")
                emb.add_field(name = "Стиль питомца", value = f"{style}")
                emb.add_field(name = "Процент улучшения", value = f"{act}")
                if image != 'Не указано' and image != 'none' and image != "Укажите изображение питомца:" and image != None:
                    emb.set_thumbnail(url = image)

                emb.add_field(name = "Шанс атаки", value = f"{chance}")
                emb.add_field(name = "Урон", value = f"{damage}")

                emb.add_field(name = "Редкость питомца", value = f"{quality}")
                emb.add_field(name = "Описание предмета", value = f"{description}")
                emb.add_field(name = "Сообщение при активации", value = f"{action_m}")

                if race_u != 'Не указано' and race_u != 'Укажите названия рас, которые могут использовать этот предмет или `all`:' and race_u != 'all' and race_u != None:
                    emb.add_field(name = "Расы с возможностью использовать", value = f"{','.join(str(x) for x in race_u)}")
                else:
                    emb.add_field(name = "Расы с возможностью использовать", value = f"{race_u}")

                emb.add_field(name = "Элемент", value = f"{element}")
                emb.add_field(name = "Эмоджи", value = f"{emoji_v}")

                emb.set_footer(text = 'Отправляйте сообщения в чат без использованеи команд, на одно указание у вас 60 сек.')
                return emb


            await message.edit(embed = embed(type, f'Укажите название предмета: (не более 150 символов)'))
            name = await name_f(message, ctx)
            if name == False:
                return
            else:
                item.update({ 'name': name})

            text = "`hp+` - бонус к здоровью.\n`mana+` - бонус к мане.\n`damage+` - бонус к урону.\n`armor+` - бонус к защите.\n`mana-` - уменьшение использования маны"

            try:
                emb = discord.Embed(title = "Стили:",
                description = text, color=server['embed_color'])
                msg1 = await ctx.send(embed = emb)
                await message.edit(embed = embed(type, name, f"Укажите стиль `{name}`"))
                msg = await self.bot.wait_for('message', timeout=60.0, check=lambda message: message.author == ctx.author and message.channel.id == ctx.channel.id)
            except asyncio.TimeoutError:
                await ctx.send("Время вышло.")
                return
            else:
                try:
                    await msg.delete()
                    await msg1.delete()
                except Exception:
                    pass

                if msg.content in ["hp+", "mana+", "damage+", "armor+", "mana-"]:
                    item.update({ 'style': msg.content})
                else:
                    await ctx.send(f'Вы указали не действительный стиль предмета, выберите 1 из ({", ".join(["hp+", "mana+", "damage+", "armor+", "mana-"])}) и повторите создание снова!')
                    return

                style = msg.content

            try:
                await message.edit(embed = embed(type, name, style, f"Укажите процент увелечения `{style}`"))
                msg = await self.bot.wait_for('message', timeout=60.0, check=lambda message: message.author == ctx.author and message.channel.id == ctx.channel.id)
            except asyncio.TimeoutError:
                await ctx.send("Время вышло.")
                return
            else:
                try:
                    await msg.delete()
                except Exception:
                    pass

                try:
                    act = float(msg.content)
                except Exception:
                    await ctx.send("Требовалось указать __число__!")
                    return

                item.update({ 'act': act})

            await message.edit(embed = embed(type, name, style, act, "Укажите изображение питомца:"))
            image = await image_f(message, ctx)
            if image == False:
                return
            else:
                item.update({'image': image})

            await message.edit(embed = embed(type, name, style, act, image, f"Укажите процент атаки `{name}`"))
            try:
                msg = await self.bot.wait_for('message', timeout=60.0, check=lambda message: message.author == ctx.author and message.channel.id == ctx.channel.id)
            except asyncio.TimeoutError:
                await ctx.send("Время вышло.")
                return
            else:
                try:
                    await msg.delete()
                except Exception:
                    pass

                try:
                    chance = int(msg.content)
                except Exception:
                    await ctx.send("Требовалось указать __число__!")
                    return

                if chance < 1 or chance > 100:
                    await ctx.send(f"Требовалось указать число от 1 до 100!")
                    return
                else:
                    item.update({ 'chance': chance})

            await message.edit(embed = embed(type, name, style, act, image, chance, f"Укажите урон `{name}`"))
            try:
                msg = await self.bot.wait_for('message', timeout=60.0, check=lambda message: message.author == ctx.author and message.channel.id == ctx.channel.id)
            except asyncio.TimeoutError:
                await ctx.send("Время вышло.")
                return
            else:
                try:
                    await msg.delete()
                except Exception:
                    pass

                try:
                    damage = int(msg.content)
                except Exception:
                    await ctx.send("Требовалось указать __число__!")
                    return

                item.update({ 'damage': damage})


            await message.edit(embed = embed(type, name, style, act, image, chance, damage, f"Укажите качество питомца: "))
            quality = await quality_f(message, ctx)
            if quality == False:
                return
            else:
                item.update({'quality': quality})

            await message.edit(embed = embed(type, name, style, act, image, chance, damage, quality, f'Укажите описание предмета или `none`: (макс 300 символов)'))
            description = await description_f(message, ctx)
            if description == False:
                return
            else:
                item.update({'description': description})

            await message.edit(embed = embed( type, name, style, act, image, chance, damage, quality, description, f'Укажите описание предмета или `none`: (макс 2000 символов)'))
            action_m = await action_m_f(message, ctx)
            if action_m == False:
                return
            else:
                item.update({'action_m': action_m})

            await message.edit(embed = embed(type, name, style, act, image, chance, damage, quality, description, action_m, f'Укажите названия рас, которые могут использовать этот предмет или `all`:'))
            race_u = await race_u_f(message, ctx, server)
            if race_u == False:
                return
            else:
                item.update({'race_u': race_u})

            await message.edit(embed = embed(type, name, style, act, image, chance, damage, quality, description, action_m, race_u, f'Укажите элеменет или `none`:'))
            element = await element_f(message, ctx)
            if element == False:
                return
            else:
                item.update({'element': element})

            await message.edit(embed = embed(type, name, style, act, image, chance, damage, quality, description, action_m, race_u, element, f'Укажите эмоджи предмета:'))
            emoji_v = await emoji_f(message, ctx)
            if emoji_v == False:
                return
            else:
                item.update({'emoji': emoji_v})

            await message.edit(embed = embed( type, name, style, act, image, chance, damage, quality, description, action_m, race_u, element, emoji_v))

        elif type == 'material':

            def embed(type = 'Не указано', name = 'Не указано', image = 'Не указано', quality = 'Не указано', description = 'Не указано', race_u = 'Не указано', emoji_v = 'Не указано'):
                nonlocal server

                emb = discord.Embed(title = "Создание предмета", description = "", color=server['embed_color'])
                emb.add_field(name = "Тип предмета", value = f"{type}")
                emb.add_field(name = "Имя предмета", value = f"{name}")
                if image != 'Не указано' and image != 'none' and image != "Укажите изображение предмета:" and image != None:
                    emb.set_thumbnail(url = image)
                emb.add_field(name = "Качество предмета", value = f"{quality}")
                emb.add_field(name = "Описание предмета", value = f"{description}")

                if race_u != 'Не указано' and race_u != 'Укажите названия рас, которые могут использовать этот предмет или `all`:' and race_u != 'all' and race_u != None:
                    emb.add_field(name = "Расы с возможностью использовать", value = f"{','.join(str(x) for x in race_u)}")
                else:
                    emb.add_field(name = "Расы с возможностью использовать", value = f"{race_u}")

                emb.add_field(name = "Эмоджи", value = f"{emoji_v}")

                emb.set_footer(text = 'Отправляйте сообщения в чат без использованеи команд, на одно указание у вас 60 сек.')
                return emb

            await message.edit(embed = embed(type, f'Укажите название предмета: (не более 150 символов)'))
            name = await name_f(message, ctx)
            if name == False:
                return
            else:
                item.update({ 'name': name})

            await message.edit(embed = embed(type, name, "Укажите изображение предмета:"))
            image = await image_f(message, ctx)
            if image == False:
                return
            else:
                item.update({'image': image})

            await message.edit(embed = embed(type, name, image, f"Укажите качество предмета: "))
            quality = await quality_f(message, ctx)
            if quality == False:
                return
            else:
                item.update({'quality': quality})

            await message.edit(embed = embed(type, name, image, quality, f'Укажите описание предмета или `none`: (макс 500 символов)'))
            description = await description_f(message, ctx)
            if description == False:
                return
            else:
                item.update({'description': description})

            await message.edit(embed = embed(type, name, image, quality, description, f'Укажите названия рас, которые могут использовать этот предмет или `all`:'))
            race_u = await race_u_f(message, ctx, server)
            if race_u == False:
                return
            else:
                item.update({'race_u': race_u})

            await message.edit(embed = embed(type, name, image, quality, description, race_u, f'Укажите эмоджи предмета:'))
            emoji_v = await emoji_f(message, ctx)
            if emoji_v == False:
                return
            else:
                item.update({'emoji': emoji_v})

            await message.edit(embed = embed( type, name, image, quality, description, race_u, emoji_v))

        elif type == 'recipe':

            def embed(type = 'Не указано', name = 'Не указано', act = 'Не указано', ndi = 'Не указано', create = 'Не указано', uses = 'Не указано', image = 'Не указано', quality = 'Не указано', description = 'Не указано', action_m = 'Не указано', race_u = 'Не указано', emoji_v = 'Не указано'):
                nonlocal server

                emb = discord.Embed(title = "Создание предмета", description = "", color=server['embed_color'])
                emb.add_field(name = "Тип предмета", value = f"{type}")
                emb.add_field(name = "Имя предмета", value = f"{name}")
                if act != 'Не указано' and act != 'Укажите id предметов для крафта: (максимум 500 предметов)':
                    emb.add_field(name = "Используемые предметы", value = f"{', '.join(str(x) for x in act)}")
                else:
                    emb.add_field(name = "Используемые предметы", value = f"{act}")

                if ndi != 'Не указано' and ndi != 'Укажите не удаляемые предметы' and ndi != None:
                    emb.add_field(name = "Не удаляемые предметы", value = f"{', '.join(str(x) for x in ndi)}")
                else:
                    emb.add_field(name = "Не удаляемые предметы", value = f"{ndi}")

                if create != 'Не указано' and create != 'Укажите id  предметов которые будут созданы: (максимум 500 предметов)':
                    emb.add_field(name = "Создаваемые предметы", value = f"{', '.join(str(x) for x in create)}")
                else:
                    emb.add_field(name = "Создаваемые предметы", value = f"{create}")

                if image != 'Не указано' and image != 'none' and image != "Укажите изображение предмета:" and image != None:
                    emb.set_thumbnail(url = image)

                emb.add_field(name = "Использований", value = f"{uses}")
                emb.add_field(name = "Качество предмета", value = f"{quality}")
                emb.add_field(name = "Описание предмета", value = f"{description}")
                emb.add_field(name = "Сообщение при активации", value = f"{action_m}")

                if race_u != 'Не указано' and race_u != 'Укажите названия рас, которые могут использовать этот предмет или `all`:' and race_u != 'all' and race_u != None:
                    emb.add_field(name = "Расы с возможностью использовать", value = f"{', '.join(str(x) for x in race_u)}")
                else:
                    emb.add_field(name = "Расы с возможностью использовать", value = f"{race_u}")

                emb.add_field(name = "Эмоджи", value = f"{emoji_v}")

                emb.set_footer(text = 'Отправляйте сообщения в чат без использованеи команд, на одно указание у вас 60 сек.')
                return emb

            await message.edit(embed = embed(type, f'Укажите название предмета: (не более 150 символов)'))
            name = await name_f(message, ctx)
            if name == False:
                return
            else:
                item.update({ 'name': name})

            try:
                b = 500

                act = []
                emb = discord.Embed(title = "",
                description = "Укажите id предметов для крафта, формат: 12 12 1 2 2\nЕсли вы хотите увеличить колличество предмета то просто укажите его повторно, пример: 11 11 (будет удалено 2 предмета с id 11)", color=server['embed_color'])
                msg1 = await ctx.send(embed = emb)
                await message.edit(embed = embed(type, name, f"Укажите id предметов для крафта: (максимум 500 предметов)"))
                msg = await self.bot.wait_for('message', timeout=60.0, check=lambda message: message.author == ctx.author and message.channel.id == ctx.channel.id)
            except asyncio.TimeoutError:
                await ctx.send("Время вышло.")
                return
            else:
                try:
                    await msg.delete()
                    await msg1.delete()
                except Exception:
                    pass

                try:
                    try:
                        act1 = msg.content.split()
                        a = 0
                        for i in act1:
                            if a > b:
                                await ctx.send(f"Вы указали количество предметов для крафта больше допустимого ({b})")
                                return
                            a += 1
                            act.append(int(i))
                    except Exception:
                        await ctx.send("Требовалось указать __число__, повторите настройку ещё раз.")
                        return
                    for i in act:
                        server['items'][str(i)]
                except Exception:
                    await ctx.send("Требовалось указать __id__ (число) существующего предмета, повторите настройку ещё раз.")
                    return

                item.update({'act': act})

            try:
                emb = discord.Embed(title = "Укажите предметы (id) которые не будут удаляться: (Пример: 1 2 8)",
                description = "`none` - при крафте все предметы удаляться из инвенторя\n", color=server['embed_color'])
                msg1 = await ctx.send(embed = emb)
                await message.edit(embed = embed(type, name, act, f"Укажите не удаляемые предметы"))
                msg = await self.bot.wait_for('message', timeout=60.0, check=lambda message: message.author == ctx.author and message.channel.id == ctx.channel.id)
            except asyncio.TimeoutError:
                await ctx.send("Время вышло.")
                return
            else:
                try:
                    await msg.delete()
                    await msg1.delete()
                except Exception:
                    pass

                if msg.content == 'none':
                    item.update({ 'ndi': None})
                    ndi = None

                else:
                    ms_c_i = list(int(x) for x in msg.content.split())

                    l = set(act) & set(ms_c_i)

                    if dict(set(l) & set(msg.content.split())) == {}:
                        ndi = list(int(x) for x in msg.content.split())
                    else:
                        await ctx.send("Требовалось указать предметы (число) из крафта которые не будут удаляться!")
                        return

                    item.update({ 'ndi': ndi})


            try:
                b = 500

                emb = discord.Embed(title = "",
                description = "Укажите id создаваемых предметов, формат: 12 12 1 2 2\nЕсли вы хотите увеличить колличество предмета то просто укажите его повторно, пример: 11 11 (будет создано 2 предмета с id 11)", color=server['embed_color'])
                msg1 = await ctx.send(embed = emb)
                await message.edit(embed = embed(type, name, act, ndi, f"Укажите id  предметов которые будут созданы: (максимум 500 предметов)"))
                msg = await self.bot.wait_for('message', timeout=60.0, check=lambda message: message.author == ctx.author and message.channel.id == ctx.channel.id)
            except asyncio.TimeoutError:
                await ctx.send("Время вышло.")
                return
            else:
                try:
                    await msg.delete()
                    await msg1.delete()
                except Exception:
                    pass

                try:
                    try:
                        cr = []
                        cr1 = msg.content.split()
                        a = 0
                        for i in cr1:
                            if a > b:
                                await ctx.send(f"Вы указали количество предметов для крафта больше допустимого ({b})")
                                return
                            a += 1
                            cr.append(int(i))
                    except Exception:
                        await ctx.send("Требовалось указать __число__, повторите настройку ещё раз.")
                        return
                    for i in cr:
                        server['items'][str(i)]
                except Exception:
                    await ctx.send("Требовалось указать __id__ (число) существующего предмета, повторите настройку ещё раз.")
                    return

                create = cr
                item.update({'create': cr})

            try:
                await message.edit(embed = embed(type, name, act, ndi, create, "Укажите сколько раз можно использовать предмет (0 - бесконечность):"))
                msg = await self.bot.wait_for('message', timeout=60.0, check=lambda message: message.author == ctx.author and message.channel.id == ctx.channel.id)
            except asyncio.TimeoutError:
                await ctx.send("Время вышло.")
                return
            else:
                try:
                    await msg.delete()
                except Exception:
                    pass

                try:
                    uses = int(msg.content)
                except:
                    await ctx.send("Требовалось указать число!")
                    return

                if uses < 0:
                    await ctx.send("Укажите число больше или равное нулю!")
                    return

            item.update({'uses': uses})

            await message.edit(embed = embed(type, name, act, ndi, create, uses, "Укажите изображение предмета:"))
            image = await image_f(message, ctx)
            if image == False:
                return
            else:
                item.update({'image': image})

            await message.edit(embed = embed(type, name, act, ndi, create, uses, image, f"Укажите качество предмета: "))
            quality = await quality_f(message, ctx)
            if quality == False:
                return
            else:
                item.update({'quality': quality})

            await message.edit(embed = embed(type, name, act, ndi, create, uses, image, quality, f'Укажите описание предмета или `none`: (макс 300 символов)'))
            description = await description_f(message, ctx)
            if description == False:
                return
            else:
                item.update({'description': description})

            await message.edit(embed = embed(type, name, act, ndi, create, uses, image, quality, description, f'Укажите описание предмета или `none`: (макс 2000 символов)'))
            action_m = await action_m_f(message, ctx)
            if action_m == False:
                return
            else:
                item.update({'action_m': action_m})

            await message.edit(embed = embed(type, name, act, ndi, create, uses, image, quality, description, action_m, f'Укажите названия рас, которые могут использовать этот предмет или `all`:'))
            race_u = await race_u_f(message, ctx, server)
            if race_u == False:
                return
            else:
                item.update({'race_u': race_u})

            await message.edit(embed = embed(type, name, act, ndi, create, uses, image, quality, description, action_m, race_u, f'Укажите эмоджи предмета:'))
            emoji_v = await emoji_f(message, ctx)
            if emoji_v == False:
                return
            else:
                item.update({'emoji': emoji_v})

            await message.edit(embed = embed( type, name, act, ndi, create, uses, image, quality, description, action_m, race_u, emoji_v))

        elif type == 'role':

            def embed(type = 'Не указано', name = 'Не указано', act = 'Не указано', style = 'Не указано', image = 'Не указано', quality = 'Не указано', description = 'Не указано', action_m = 'Не указано', race_u = 'Не указано', emoji_v = 'Не указано'):
                nonlocal server

                emb = discord.Embed(title = "Создание предмета", description = "", color=server['embed_color'])
                emb.add_field(name = "Тип предмета", value = f"{type}")
                emb.add_field(name = "Имя предмета", value = f"{name}")

                if act == 'Не указано' or act == f"Укажите [id](https://support.discord.com/hc/ru/articles/206346498-%D0%93%D0%B4%D0%B5-%D0%BC%D0%BD%D0%B5-%D0%BD%D0%B0%D0%B9%D1%82%D0%B8-ID-%D0%BF%D0%BE%D0%BB%D1%8C%D0%B7%D0%BE%D0%B2%D0%B0%D1%82%D0%B5%D0%BB%D1%8F-%D1%81%D0%B5%D1%80%D0%B2%D0%B5%D1%80%D0%B0-%D1%81%D0%BE%D0%BE%D0%B1%D1%89%D0%B5%D0%BD%D0%B8%D1%8F-) роли `{name}`":
                    emb.add_field(name = "Id роли", value = f"{act}")
                else:
                    emb.add_field(name = "Id роли", value = f"<@&{act}>")

                emb.add_field(name = "Стиль предмета", value = f"{style}")
                if image != 'Не указано' and image != 'none' and image != "Укажите изображение предмета:" and image != None:
                    emb.set_thumbnail(url = image)
                emb.add_field(name = "Качество предмета", value = f"{quality}")
                emb.add_field(name = "Описание предмета", value = f"{description}")
                emb.add_field(name = "Сообщение при активации", value = f"{action_m}")
                if race_u != 'Не указано' and race_u != 'Укажите названия рас, которые могут использовать этот предмет или `all`:' and race_u != 'all' and race_u != None:
                    emb.add_field(name = "Расы с возможностью использовать", value = f"{','.join(str(x) for x in race_u)}")
                else:
                    emb.add_field(name = "Расы с возможностью использовать", value = f"{race_u}")

                emb.add_field(name = "Эмоджи", value = f"{emoji_v}")
                emb.set_footer(text = 'Отправляйте сообщения в чат без использованеи команд, на одно указание у вас 60 сек.')
                return emb


            await message.edit(embed = embed(type, f'Укажите название предмета: (не более 150 символов)'))
            name = await name_f(message, ctx)
            if name == False:
                return
            else:
                item.update({ 'name': name})


            try:
                await message.edit(embed = embed(type, name, f"Укажите [id](https://support.discord.com/hc/ru/articles/206346498-%D0%93%D0%B4%D0%B5-%D0%BC%D0%BD%D0%B5-%D0%BD%D0%B0%D0%B9%D1%82%D0%B8-ID-%D0%BF%D0%BE%D0%BB%D1%8C%D0%B7%D0%BE%D0%B2%D0%B0%D1%82%D0%B5%D0%BB%D1%8F-%D1%81%D0%B5%D1%80%D0%B2%D0%B5%D1%80%D0%B0-%D1%81%D0%BE%D0%BE%D0%B1%D1%89%D0%B5%D0%BD%D0%B8%D1%8F-) роли `{name}`"))
                msg = await self.bot.wait_for('message', timeout=60.0, check=lambda message: message.author == ctx.author and message.channel.id == ctx.channel.id)
            except asyncio.TimeoutError:
                await ctx.send("Время вышло.")
                return
            else:
                try:
                    await msg.delete()
                except Exception:
                    pass

                try:
                    act = int(msg.content)
                except Exception:
                    await ctx.send("Требовалось указать id роли, повторите настройку ещё раз.")
                    return
                role = ctx.guild.get_role(act)
                try:
                    act = role.id
                except Exception:
                    await ctx.send("Требовалось указать id существующей роли, повторите настройку ещё раз.")
                    return

                item.update({ 'act': act})

            text = "`add` - добавляет роль при использовании.\n`remove` - удаляет роль при использовании.\n"

            try:
                emb = discord.Embed(title = "Стили:",
                description = text, color=server['embed_color'])
                msg1 = await ctx.send(embed = emb)
                await message.edit(embed = embed(type, name, act, f"Укажите стиль `{name}`"))
                msg = await self.bot.wait_for('message', timeout=60.0, check=lambda message: message.author == ctx.author and message.channel.id == ctx.channel.id)
            except asyncio.TimeoutError:
                await ctx.send("Время вышло.")
                return
            else:
                try:
                    await msg.delete()
                    await msg1.delete()
                except Exception:
                    pass

                if msg.content in ['add', 'remore']:
                    item.update({ 'style': msg.content})
                else:
                    await ctx.send("Вы указали не действительный стиль предмета, выберите 1 из (add, remore) и повторите создание снова!")
                    return

                style = msg.content

            await message.edit(embed = embed(type, name, act, style, "Укажите изображение предмета:"))
            image = await image_f(message, ctx)
            if image == False:
                return
            else:
                item.update({'image': image})


            await message.edit(embed = embed(type, name, act, style, image, f"Укажите качество предмета: "))
            quality = await quality_f(message, ctx)
            if quality == False:
                return
            else:
                item.update({'quality': quality})

            await message.edit(embed = embed(type, name, act, style, image, quality, f'Укажите описание предмета или `none`: (макс 300 символов)'))
            description = await description_f(message, ctx)
            if description == False:
                return
            else:
                item.update({'description': description})

            await message.edit(embed = embed(type, name, act, style, image, quality, description, f'Укажите описание предмета или `none`: (макс 2000 символов)'))
            action_m = await action_m_f(message, ctx)
            if action_m == False:
                return
            else:
                item.update({'action_m': action_m})

            await message.edit(embed = embed(type, name, act, style, image, quality, description, action_m, f'Укажите названия рас, которые могут использовать этот предмет или `all`:'))
            race_u = await race_u_f(message, ctx, server)
            if race_u == False:
                return
            else:
                item.update({'race_u': race_u})


            await message.edit(embed = embed(type, name, act, style, image, quality, description, action_m, race_u, f'Укажите эмоджи предмета:'))
            emoji_v = await emoji_f(message, ctx)
            if emoji_v == False:
                return
            else:
                item.update({'emoji': emoji_v})

            await message.edit(embed = embed( type, name, act, style, image, quality, description, action_m, race_u, emoji_v))

        if type == 'prop':

            def embed(type = 'Не указано', name = 'Не указано',  image = 'Не указано', description = 'Не указано', action_m = 'Не указано', emoji_v = 'Не указано'):
                nonlocal server

                emb = discord.Embed(title = "Создание предмета", description = "", color=server['embed_color'])
                emb.add_field(name = "Тип предмета", value = f"{type}")
                emb.add_field(name = "Имя предмета", value = f"{name}")
                if image != 'Не указано' and image != 'none' and image != "Укажите изображение предмета:" and image != None:
                    emb.set_thumbnail(url = image)

                emb.add_field(name = "Описание предмета", value = f"{description}")
                emb.add_field(name = "Сообщение при активации", value = f"{action_m}")
                emb.add_field(name = "Эмоджи", value = f"{emoji_v}")

                emb.set_footer(text = 'Отправляйте сообщения в чат без использованеи команд, на одно указание у вас 60 сек.')
                return emb

            await message.edit(embed = embed(type, f'Укажите название предмета: (не более 150 символов)'))
            name = await name_f(message, ctx)
            if name == False:
                return
            else:
                item.update({ 'name': name})

            await message.edit(embed = embed(type, name, "Укажите изображение предмета:"))
            image = await image_f(message, ctx)
            if image == False:
                return
            else:
                item.update({'image': image})

            await message.edit(embed = embed(type, name, image, f'Укажите описание предмета или `none`: (макс 500 символов)'))
            description = await description_f(message, ctx)
            if description == False:
                return
            else:
                item.update({'description': description})

            await message.edit(embed = embed(type, name, image, description, f'Укажите описание предмета или `none`: (макс 2000 символов)'))
            action_m = await action_m_f(message, ctx)
            if action_m == False:
                return
            else:
                item.update({'action_m': action_m})

            await message.edit(embed = embed(type, name, image, description, action_m, f'Укажите эмоджи предмета:'))
            emoji_v = await emoji_f(message, ctx)
            if emoji_v == False:
                return
            else:
                item.update({'emoji': emoji_v})


            await message.edit(embed = embed( type, name, image, description, action_m, emoji_v))

        try:
            l = server['items']
            lst = []
            for i in l.keys():
                lst.append(int(i))
            l = max(lst)+1
        except Exception:
            l = 1

        await ctx.send(f"Предмет с id {l} создан!\n{item}")

        server = servers.find_one({"server": ctx.guild.id})
        il = server['items']
        il.update({f'{l}': item})
        servers.update_one({'server':ctx.guild.id},{"$set":{'items': il}})

    @commands.command(usage = '-', description = 'Создание расы.')
    async def create_race(self, ctx):
        global servers
        if funs.roles_check(ctx.author, ctx.guild.id) == False:
            await ctx.send("У вас недостаточно прав для использования этой команды!")
            return

        server = servers.find_one({'server':ctx.guild.id})
        race = {}

        def embed(name, hp = "не указано", mana = "не указано", items = "не указано", description = "не указано", image = 'Не указано'):
            nonlocal server
            emb = discord.Embed(title = "Создание расы", description = "", color=server['embed_color'])
            emb.add_field(name = "Название:", value = f"{name}")
            emb.add_field(name = "Максимальное здоровье:", value = f"{hp}")
            emb.add_field(name = "Максимальная мана:", value = f"{mana}")
            emb.add_field(name = "Начальные предметы:", value = f"{items}")
            emb.add_field(name = "Описание:", value = f"{description}")
            if image != 'Не указано' and image != 'none' and image != "Укажите изображение расы:":
                emb.set_thumbnail(url = image)
            return emb


        message = await ctx.send(embed = embed("не указано"))

        try:
            await message.edit(embed = embed('Укажите название расы (не более 100-та символов)'))
            msg = await self.bot.wait_for('message', timeout=120.0, check=lambda message: message.author == ctx.author and message.channel.id == ctx.channel.id)
        except asyncio.TimeoutError:
            await ctx.send("Время вышло.")
            return
        else:

            try:
                await msg.delete()
            except Exception:
                pass

            if len(msg.content) > 100:
                await ctx.send('Название больше 100-та символов!')
                return
            else:
                name = msg.content

        try:
            await message.edit(embed = embed(name, 'Укажите максимальное здоровье для расы'))
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
                hp = int(msg.content)
                race.update({'hp': int(msg.content)})
            except Exception:
                await ctx.send('Укажите число!')
                return

        try:
            await message.edit(embed = embed(name, hp, 'Укажите максимальную ману для расы'))
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
                mana = int(msg.content)
                race.update({'mana': int(msg.content)})
            except Exception:
                await ctx.send('Укажите число!')
                return

        try:
            if server['premium'] == None:
                b = 20
            else:
                b = 50

            act = []
            emb = discord.Embed(title = "",
            description = "Укажите id предметов для расы, формат: 12 12 1 2 2\nЕсли вы хотите увеличить колличество предмета то просто укажите его повторно, пример: 11 11 (будет добавлено 2 предмета с id 11)", color=server['embed_color'])
            msg1 = await ctx.send(embed = emb)
            await message.edit(embed = embed(name, hp, mana, f"Укажите id предметов для расы или `none`: (максимум {b} предметов)"))
            msg = await self.bot.wait_for('message', timeout=60.0, check=lambda message: message.author == ctx.author and message.channel.id == ctx.channel.id)
        except asyncio.TimeoutError:
            await ctx.send("Время вышло.")
            return
        else:
            try:
                await msg.delete()
                await msg1.delete()
            except Exception:
                pass

            if msg.content == 'none':
                act = None
            else:
                try:
                    try:
                        act1 = msg.content.split()
                        a = 0
                        for i in act1:
                            if a > b:
                                await ctx.send(f"Вы указали количество предметов больше допустимого ({b})")
                                return
                            a += 1
                            act.append(int(i))
                    except Exception:
                        await ctx.send("Требовалось указать __число__, повторите настройку ещё раз.")
                        return
                    for i in act:
                        server['items'][str(i)]
                except Exception:
                    await ctx.send("Требовалось указать __id__ (число) существующего предмета, повторите настройку ещё раз.")
                    return

            items = act
            race.update({'items': act})

        try:
            await message.edit(embed = embed(name, hp, mana, items, f'Укажите описание расы или `none`: (макс 300 символов)'))
            msg = await self.bot.wait_for('message', timeout=60.0, check=lambda message: message.author == ctx.author and message.channel.id == ctx.channel.id)
        except asyncio.TimeoutError:
            await ctx.send("Время вышло.")
            return
        else:
            try:
                await msg.delete()
            except Exception:
                pass
            description = str(msg.content)
            if description == 'none':
                race.update({ 'description': None})
                description = None
            elif len(description) > 0 and len(description) < 301:
                race.update({ 'description': msg.content})
                description = msg.content
            else:
                await ctx.send("Требовалось указать описание (макс 300 символов) или `none`, повторите настройку ещё раз!")
                return

        try:
            text = "Требуется указать __ссылку__ на изображение или `none`"
            emb = discord.Embed(title = "Изображение:",
            description = text, color=server['embed_color'])
            msg1 = await ctx.send(embed = emb)
            await message.edit(embed = embed(name, hp, mana, items, description, "Укажите изображение расы:"))
            msg = await self.bot.wait_for('message', timeout=60.0, check=lambda message: message.author == ctx.author and message.channel.id == ctx.channel.id)
        except asyncio.TimeoutError:
            await ctx.send("Время вышло.")
            return
        else:
            try:
                await msg.delete()
            except Exception:
                pass

            if msg.content != 'none':
                try:
                    emb1 = discord.Embed(title = "Изображение", color=server['embed_color'])
                    emb1.set_thumbnail(url = msg.content)
                    msg2 = await ctx.send(embed = emb1)
                except Exception:
                    await ctx.send("Требовалось указать __ссылку__, повторите настройку ещё раз.")
                    return

            race.update({'image': msg.content})
            image = str(msg.content)
            try:
                await msg1.delete()
                await msg2.delete()
            except Exception:
                pass


        await message.edit(embed = embed(name, hp, mana, items, description, image))

        server = servers.find_one({"server": ctx.guild.id})
        il = server['races']
        il.update({f'{name}': race})
        servers.update_one({'server':ctx.guild.id},{"$set":{'races': il}})




    @commands.command(usage = '(item_name)', description = 'Использовать предмет из инвентаря.')
    async def use(self, ctx, *, i_name:str):

        user = funs.user_check(ctx.author, ctx.guild)
        server = servers.find_one({"server": ctx.guild.id})

        s_i = []

        for i in user['inv']:
            print(i['name'])
            print(fuzz.token_sort_ratio(i_name, i['name']), fuzz.ratio(i_name,i['name']), i_name == i['name'])
            if fuzz.token_sort_ratio(i_name, i['name']) > 80 or fuzz.ratio(i_name,i['name']) > 80 or i_name == i['name']:
                s_i.append(i)

        if len(s_i) == 1:
            emb = discord.Embed(description = f'Вы хотите использовать **{s_i[0]["name"]}** ?', title = '<:inventory_b:886909340550823936> | Инвентарь', color=server['embed_color'])
            msg = await ctx.send(embed= emb)
            r = await funs.reactions_check( ["✅", "❌"], ctx.author, msg, True)
            if r != 'Timeout':
                if str(r.emoji) == "✅":
                    print('Использование')
                else:
                    print('Отмена')
            else:
                await ctx.send('Время вышло')

        if len(s_i) == 0:
            emb = discord.Embed(title = '<:inventory_b:886909340550823936> | Инвентарь', description = f'В вашем инвентаре не было найдено такого предмета!\nПопробуйте указать более точное название или осмотрите свой инвентарь более подробно!', color=server['embed_color'])
            msg = await ctx.send(embed= emb)

        if len(s_i) > 1:
            inv = {}

            items = []
            for i in server['items'].keys():
                items.append(server['items'][i])

            for i in s_i:
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


            class Dropdown(discord.ui.Select):
                def __init__(self, inv, ctx, msg, emb):
                    options = []
                    for k in inv:
                        options.append(discord.SelectOption(label=f'{k}'))

                    super().__init__(placeholder='Выберите используемый предмет...', min_values=1, max_values=1, options=options)

                async def callback(self, interaction: discord.Interaction):
                    if ctx.author.id == interaction.user.id:
                        await interaction.response.send_message(f'{self.values[0]}', ephemeral = True)
                        self.view.stop()

                    else:
                        await interaction.response.send_message(f'Откройте свой инвентарь!', ephemeral = True)


            class DropdownView(discord.ui.View):
                def __init__(self, inv, ctx, msg, emb):
                    super().__init__()
                    self.add_item(Dropdown(inv, ctx, msg, emb))

            text = ''
            n = 0
            for k in inv:
                i = inv[k]
                n += 1
                text += f'{n}# {k} x{i["count"]}\n'

            emb = discord.Embed(title = '<:inventory_b:886909340550823936> | Инвентарь', description = f'В инвентаре найдено несколько совпадений:\n{text}', color=server['embed_color'])
            msg = await ctx.send(embed = emb)
            await msg.edit(embed = emb, view=DropdownView(inv, ctx, msg, emb))



    @commands.command(usage = '(item_name)', description = 'Информация о предмете.')
    async def item_info(self, ctx, *, i_name:str):

        user = funs.user_check(ctx.author, ctx.guild)
        server = servers.find_one({"server": ctx.guild.id})

        async def inf(item, msg):
            nonlocal ctx
            nonlocal server
            i = funs.item_info(item, ctx.guild.id)

            emb = discord.Embed(description = f"**{i['emoji']} | {i['name']}**", color=server['embed_color'])
            emb.add_field( name = f'Данные', value= f"Тип: {i['type']}\n\n{i['act_title']}\n\nРедкость: {i['quality']}\nЭлемент: {i['element']}\n{i['race_u']}", inline = True  )

            emb.add_field( name = f'Описание', value= f"{i['description']}", inline = True  )

            if i['image'] != None:
                emb.set_thumbnail(url = i['image'])

            await msg.edit(embed = emb, view = None)

        s_i = []

        for i in user['inv']:
            if fuzz.token_sort_ratio(i_name, i['name']) > 80 or fuzz.ratio(i_name,i['name']) > 80 or i_name == i['name']:
                s_i.append(i)

        inv = {}

        items = []
        for i in server['items'].keys():
            items.append(server['items'][i])

        for i in s_i:
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



        if len(inv) == 1:
            emb = discord.Embed(description = f'Вы хотите узнать информацию о **{s_i[0]["name"]}** ?', title = '<:inventory_b:886909340550823936> | Инвентарь', color=server['embed_color'])
            msg = await ctx.send(embed = emb)
            r = await funs.reactions_check( ["✅", "❌"], ctx.author, msg, True)
            if r != 'Timeout':
                if str(r.emoji) == "✅":
                    await inf(s_i[0], msg)
                else:
                    return
            else:
                await ctx.send('Время вышло')

        if len(inv) == 0:
            emb = discord.Embed(title = '<:inventory_b:886909340550823936> | Инвентарь', description = f'В вашем инвентаре не было найдено такого предмета!\nПопробуйте указать более точное название или осмотрите свой инвентарь более подробно!', color=server['embed_color'])
            msg = await ctx.send(embed= emb)

        if len(inv) > 1:

            class Dropdown(discord.ui.Select):
                def __init__(self, inv, ctx, msg, emb):
                    options = []
                    for k in inv:
                        options.append(discord.SelectOption(label=f'{k}'))

                    super().__init__(placeholder='Выберите используемый предмет...', min_values=1, max_values=1, options=options)

                async def callback(self, interaction: discord.Interaction):
                    if ctx.author.id == interaction.user.id:

                        await inf(inv[self.values[0]]['it'], msg)
                        self.view.stop()

                    else:
                        await interaction.response.send_message(f'Откройте свой инвентарь!', ephemeral = True)


            class DropdownView(discord.ui.View):
                def __init__(self, inv, ctx, msg, emb):
                    super().__init__()
                    self.add_item(Dropdown(inv, ctx, msg, emb))

            text = ''
            n = 0
            for k in inv:
                i = inv[k]
                n += 1
                text += f'{n}# {k} x{i["count"]}\n'

            emb = discord.Embed(title = '<:inventory_b:886909340550823936> | Инвентарь', description = f'В инвентаре найдено несколько совпадений:\n{text}', color=server['embed_color'])
            msg = await ctx.send(embed = emb)
            await msg.edit(embed = emb, view=DropdownView(inv, ctx, msg, emb))



    @commands.command(usage = '(id) [member]', description = 'Выдать предмет.')
    async def item_add(self, ctx, id:int, rp:int, member:discord.Member = None):
        if member == None:
            member = ctx.author

        if funs.roles_check(ctx.author, ctx.guild.id) == False:
            await ctx.send("У вас недостаточно прав для использования этой команды!")
            return

        server = servers.find_one({"server": ctx.guild.id})
        user = funs.user_check(member, ctx.guild)

        act_title = '-'

        try:
            server['items'][str(id)]
        except Exception:
            await ctx.send(f"Указанный вами предмет не найден!\nПредметы: {', '.join(str(x) for x in list(server['items'].keys()) )} ")
            return

        item = server['items'][str(id)]
        while rp != 0:
            user['inv'].append(funs.creat_item(ctx.guild.id, id))
            rp -= 1

        funs.user_update(member.id, ctx.guild, 'inv', user['inv'])

        await ctx.send('Предмет(ы) добавлен(ы)!')

    @commands.command(usage = '-', description = 'Создание локации.')
    async def create_mob(self, ctx):
        if funs.roles_check(ctx.author, ctx.guild.id) == False:
            await ctx.send("У вас недостаточно прав для использования этой команды!")
            return

        server = servers.find_one({"server": ctx.guild.id})

        mob = {}

        async def name_f(message, ctx):
            try:
                msg = await self.bot.wait_for('message', timeout=60.0, check=lambda message: message.author == ctx.author and message.channel.id == ctx.channel.id)
            except asyncio.TimeoutError:
                await ctx.send("Время вышло.")
                return False
            else:
                try:
                    await msg.delete()
                except Exception:
                    pass

                if len(message.content) > 150:
                    await ctx.send("Название больше 150-ти символов")
                    return False
                else:
                    return msg.content

        async def damage_f(message, ctx):
            try:
                msg = await self.bot.wait_for('message', timeout=60.0, check=lambda message: message.author == ctx.author and message.channel.id == ctx.channel.id)
            except asyncio.TimeoutError:
                await ctx.send("Время вышло.")
                return False
            else:
                try:
                    await msg.delete()
                except Exception:
                    pass

                try:
                    return int(msg.content)
                except Exception:
                    await ctx.send("Требовалось указать __число__!")
                    return False

        async def heal_f(message, ctx):
            try:
                msg = await self.bot.wait_for('message', timeout=60.0, check=lambda message: message.author == ctx.author and message.channel.id == ctx.channel.id)
            except asyncio.TimeoutError:
                await ctx.send("Время вышло.")
                return False
            else:
                try:
                    await msg.delete()
                except Exception:
                    pass

                try:
                    return int(msg.content)
                except Exception:
                    await ctx.send("Требовалось указать __число__!")
                    return False

        async def armor_f(message, ctx):
            try:
                msg = await self.bot.wait_for('message', timeout=60.0, check=lambda message: message.author == ctx.author and message.channel.id == ctx.channel.id)
            except asyncio.TimeoutError:
                await ctx.send("Время вышло.")
                return False
            else:
                try:
                    await msg.delete()
                except Exception:
                    pass

                try:
                    return int(msg.content)
                except Exception:
                    await ctx.send("Требовалось указать __число__!")
                    return False

        async def image_f(message, ctx):
            try:
                text = "Требуется указать __ссылку__ на изображение или `none`"
                emb = discord.Embed(title = "Изображение:",
                description = text, color=server['embed_color'])
                msg1 = await ctx.send(embed = emb)
                msg = await self.bot.wait_for('message', timeout=60.0, check=lambda message: message.author == ctx.author and message.channel.id == ctx.channel.id)
            except asyncio.TimeoutError:
                await ctx.send("Время вышло.")
                return False
            else:
                try:
                    await msg.delete()
                except Exception:
                    pass

                if msg.content != 'none':
                    try:
                        emb1 = discord.Embed(title = "Изображение", color=server['embed_color'])
                        emb1.set_thumbnail(url = msg.content)
                        msg2 = await ctx.send(embed = emb1)
                        image = msg.content
                    except Exception:
                        await ctx.send("Требовалось указать __ссылку__, повторите настройку ещё раз.")
                        return False
                if msg.content == 'none':
                    image = None
                try:
                    await msg1.delete()
                    await msg2.delete()
                except Exception:
                    pass

                return image

        async def description_f(message, ctx):
            try:
                msg = await self.bot.wait_for('message', timeout=60.0, check=lambda message: message.author == ctx.author and message.channel.id == ctx.channel.id)
            except asyncio.TimeoutError:
                await ctx.send("Время вышло.")
                return False
            else:
                try:
                    await msg.delete()
                except Exception:
                    pass
                description = str(msg.content)
                if description == 'none':
                    return None
                elif len(description) > 0 and len(description) < 501:
                    return msg.content
                else:
                    await ctx.send("Требовалось указать описание (макс 500 символов) или `none`, повторите настройку ещё раз!")
                    return False

        async def drop_f(message, ctx):
            try:
                msg = await self.bot.wait_for('message', timeout=60.0, check=lambda message: message.author == ctx.author and message.channel.id == ctx.channel.id)
            except asyncio.TimeoutError:
                await ctx.send("Время вышло.")
                return False
            else:
                try:
                    await msg.delete()
                except Exception:
                    pass

                act = []
                try:
                    try:
                        act1 = msg.content.split()
                        for i in act1:
                            act.append(int(i))
                    except Exception:
                        await ctx.send("Требовалось указать __число__, повторите настройку ещё раз.")
                        return
                    for i in act:
                        server['items'][str(i)]
                except Exception:
                    await ctx.send("Требовалось указать __id__ (число) существующего предмета, повторите настройку ещё раз.")
                    return



        async def element_f(message, ctx):
            try:
                text = "`w` - <:water:888029916287885332>(water) Огонь >`х0.75`> Вода >`х1.25`> Земля\n`a` -  <:air:888029789749919787>(air) Земля >`х0.75`> Воздух >`х1.25`> Огонь\n`f` - <:fire:888029761828425789>(fire) Воздух >`х0.75`> Огонь >`х1.25`> Вода\n`e` - <:earth:888029840945598534>(earth) Вода >`х0.75`> Земля >`х1.25`> Воздух\n\n<:fire:888029761828425789> >`х1.25`> <:water:888029916287885332> >`х1.25`> <:earth:888029840945598534> >`х1.25`> <:air:888029789749919787> >`х1.25`> <:fire:888029761828425789>\n\nУкажите `none` если у предмета нет стихии."
                emb = discord.Embed(title = "Элементы:",
                description = text, color=server['embed_color'])
                msg1 = await ctx.send(embed = emb)
                msg = await self.bot.wait_for('message', timeout=60.0, check=lambda message: message.author == ctx.author and message.channel.id == ctx.channel.id)
            except asyncio.TimeoutError:
                await ctx.send("Время вышло.")
                return False
            else:
                try:
                    await msg1.delete()
                    await msg.delete()
                except Exception:
                    pass

                if msg.content in ['fire', 'water', 'air', 'earth', 'none', 'w', 'a', 'f', 'e']:

                    if msg.content in ['w', 'water']:
                        el = "w"
                    elif msg.content in ['a', 'air']:
                        el = "a"
                    elif msg.content in ['f', 'fire']:
                        el = "f"
                    elif msg.content in ['e', 'earth',]:
                        el = "e"
                    elif msg.content in ['none']:
                        el = None

                    return el

                else:
                    await ctx.send("Требовалось указать 1 из элементов! (w, a, f, e)")
                    return False

        def embed(type = 'Не указано', name = 'Не указано', act = 'Не указано', image = 'Не указано', quality = 'Не указано', description = 'Не указано', action_m = 'Не указано', race_u = 'Не указано', element = 'Не указано', emoji_v = 'Не указано'):
            nonlocal server

            emb = discord.Embed(title = "Создание предмета", description = "", color=server['embed_color'])
            emb.add_field(name = "Тип предмета", value = f"{type}")
            emb.add_field(name = "Имя предмета", value = f"{name}")
            emb.add_field(name = "Питательность предмета", value = f"{act}")
            if image != 'Не указано' and image != 'none' and image != "Укажите изображение предмета:" and image != None:
                emb.set_thumbnail(url = image)
            emb.add_field(name = "Качество предмета", value = f"{quality}")
            emb.add_field(name = "Описание предмета", value = f"{description}")
            emb.add_field(name = "Сообщение при активации", value = f"{action_m}")

            if race_u != 'Не указано' and race_u != 'Укажите названия рас, которые могут использовать этот предмет или `all`:' and race_u != 'all' and race_u != None:
                emb.add_field(name = "Расы с возможностью использовать", value = f"{','.join(str(x) for x in race_u)}")
            else:
                emb.add_field(name = "Расы с возможностью использовать", value = f"{race_u}")

            emb.add_field(name = "Элемент", value = f"{element}")
            emb.add_field(name = "Эмоджи", value = f"{emoji_v}")

            emb.set_footer(text = 'Отправляйте сообщения в чат без использованеи команд, на одно указание у вас 60 сек.')
            return emb





    @commands.command(usage = '-', description = 'Создание локации.')
    async def create_location(self, ctx):
        if funs.roles_check(ctx.author, ctx.guild.id) == False:
            await ctx.send("У вас недостаточно прав для использования этой команды!")
            return

        async def name_f(message, ctx):
            try:
                msg = await self.bot.wait_for('message', timeout=60.0, check=lambda message: message.author == ctx.author and message.channel.id == ctx.channel.id)
            except asyncio.TimeoutError:
                await ctx.send("Время вышло.")
                return False
            else:
                try:
                    await msg.delete()
                except Exception:
                    pass

                if len(message.content) > 150:
                    await ctx.send("Название больше 150-ти символов")
                    return False
                else:
                    return msg.content

        async def image_f(message, ctx):
            try:
                text = "Требуется указать __ссылку__ на изображение или `none`"
                emb = discord.Embed(title = "Изображение:",
                description = text, color=server['embed_color'])
                msg1 = await ctx.send(embed = emb)
                msg = await self.bot.wait_for('message', timeout=60.0, check=lambda message: message.author == ctx.author and message.channel.id == ctx.channel.id)
            except asyncio.TimeoutError:
                await ctx.send("Время вышло.")
                return False
            else:
                try:
                    await msg.delete()
                except Exception:
                    pass

                if msg.content != 'none':
                    try:
                        emb1 = discord.Embed(title = "Изображение", color=server['embed_color'])
                        emb1.set_thumbnail(url = msg.content)
                        msg2 = await ctx.send(embed = emb1)
                        image = msg.content
                    except Exception:
                        await ctx.send("Требовалось указать __ссылку__, повторите настройку ещё раз.")
                        return False
                if msg.content == 'none':
                    image = None
                try:
                    await msg1.delete()
                    await msg2.delete()
                except Exception:
                    pass

                return image

        async def description_f(message, ctx):
            try:
                msg = await self.bot.wait_for('message', timeout=60.0, check=lambda message: message.author == ctx.author and message.channel.id == ctx.channel.id)
            except asyncio.TimeoutError:
                await ctx.send("Время вышло.")
                return False
            else:
                try:
                    await msg.delete()
                except Exception:
                    pass
                description = str(msg.content)
                if description == 'none':
                    return None
                elif len(description) > 0 and len(description) < 501:
                    return msg.content
                else:
                    await ctx.send("Требовалось указать описание (макс 500 символов) или `none`, повторите настройку ещё раз!")
                    return False

        async def element_f(message, ctx):
            try:
                text = "`w` - <:water:888029916287885332>(water) Огонь >`х0.75`> Вода >`х1.25`> Земля\n`a` -  <:air:888029789749919787>(air) Земля >`х0.75`> Воздух >`х1.25`> Огонь\n`f` - <:fire:888029761828425789>(fire) Воздух >`х0.75`> Огонь >`х1.25`> Вода\n`e` - <:earth:888029840945598534>(earth) Вода >`х0.75`> Земля >`х1.25`> Воздух\n\n<:fire:888029761828425789> >`х1.25`> <:water:888029916287885332> >`х1.25`> <:earth:888029840945598534> >`х1.25`> <:air:888029789749919787> >`х1.25`> <:fire:888029761828425789>\n\nУкажите `none` если у предмета нет стихии."
                emb = discord.Embed(title = "Элементы:",
                description = text, color=server['embed_color'])
                msg1 = await ctx.send(embed = emb)
                msg = await self.bot.wait_for('message', timeout=60.0, check=lambda message: message.author == ctx.author and message.channel.id == ctx.channel.id)
            except asyncio.TimeoutError:
                await ctx.send("Время вышло.")
                return False
            else:
                try:
                    await msg1.delete()
                    await msg.delete()
                except Exception:
                    pass

                if msg.content in ['fire', 'water', 'air', 'earth', 'none', 'w', 'a', 'f', 'e']:

                    if msg.content in ['w', 'water']:
                        el = "w"
                    elif msg.content in ['a', 'air']:
                        el = "a"
                    elif msg.content in ['f', 'fire']:
                        el = "f"
                    elif msg.content in ['e', 'earth',]:
                        el = "e"
                    elif msg.content in ['none']:
                        el = None

                    return el

                else:
                    await ctx.send("Требовалось указать 1 из элементов! (w, a, f, e)")
                    return False

def setup(bot):
    bot.add_cog(rpg(bot))
