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

        server = servers.find_one({"server": ctx.guild.id})

        if server['premium'] == True:
            premit = 175
        else:
            premit = 75

        if len(server['items']) > premit:
            await ctx.send(f'Превышен лимит предметов ({premit})')
            return

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
            description = "`eat` - еда, воостанавливает или отнимает у пользователя здоровье при использовании\n`point` - зелья здоровья или маны\n`case` - сундуки с случайным предметом\n`armor` - броня, при использовании устанавливает броню\n`weapon` - оружие, может быть: дальнобойного, ближнего и магического стиля.\n`pet` - питомец\n`material` - материал, его нельзя взять в руки или съесть, но если вам надо создать руду или стрелы, вам сюда.\n`recipe` - рецепт для крафта\n`role` - роль, при использовании выдаёт роль", color=server['embed_color'])
            msg1 = await ctx.send(embed = emb)
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
            if msg.content in ['eat','point','case','armor','weapon','pet',"material",'recipe','role']:
                if server['premium'] == False and msg.content in ['case', 'pet']:
                    await ctx.send("У вашего сервера нету статуса премиум подписки")
                    return

                item.update({ 'type': msg.content})
            else:
                await ctx.send("Вы указали не действительный тип предмета, выберите 1 из (eat, point, case, armor, weapon, pet, material, recipe, role) и повторите создание снова!")
                return

            type = msg.content

        if type == 'eat':

            def embed(type = 'Не указано', name = 'Не указано', act = 'Не указано', image = 'Не указано', quality = 'Не указано', description = 'Не указано', action_m = 'Не указано'):
                nonlocal server

                emb = discord.Embed(title = "Создание предмета", description = "", color=server['embed_color'])
                emb.add_field(name = "Тип предмета", value = f"{type}")
                emb.add_field(name = "Имя предмета", value = f"{name}")
                emb.add_field(name = "Питательность предмета", value = f"{act}")
                if image != 'Не указано' and image != 'none' and image != "Укажите изображение предмета:":
                    emb.set_thumbnail(url = image)
                emb.add_field(name = "Качество предмета", value = f"{quality}")
                emb.add_field(name = "Описание предмета", value = f"{description}")
                emb.add_field(name = "Сообщение при активации", value = f"{action_m}")

                emb.set_footer(text = 'Отправляйте сообщения в чат без использованеи команд, на одно указание у вас 60 сек.')
                return emb

            try:
                await message.edit(embed = embed(type, f'Укажите название предмета: (не более 150 символов)'))
                msg = await self.bot.wait_for('message', timeout=60.0, check=lambda message: message.author == ctx.author and message.channel.id == ctx.channel.id)
            except asyncio.TimeoutError:
                await ctx.send("Время вышло.")
                return
            else:
                try:
                    await msg.delete()
                except Exception:
                    pass
                if len(message.content) > 150:
                    await ctx.send("Название больше 150-ти символов")
                    return
                item.update({ 'name': msg.content})
                name = str(msg.content)

            try:
                await message.edit(embed = embed(type, name, f"Укажите питательность `{name}`"))
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
                    await ctx.send("Требовалось указать __число__!")
                    return

                item.update({ 'act': act})

            try:
                text = "Требуется указать __ссылку__ на изображение или `none`"
                emb = discord.Embed(title = "Изображение:",
                description = text, color=server['embed_color'])
                msg1 = await ctx.send(embed = emb)
                await message.edit(embed = embed(type, name, act, "Укажите изображение предмета:"))
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

                item.update({'image': msg.content})
                image = str(msg.content)
                try:
                    await msg1.delete()
                    await msg2.delete()
                except Exception:
                    pass

            try:
                text = "**Качество предмета влияет на процент его выпадения и крафта**\n`n` - <:normal_q:781531816993620001>(normal) обычное качество, шанс выпадения/крафта 100%\n`u` - <:unusual_q:781531868780691476>(unusual) необычное качество, шанс выпадения/крафта 75%\n`r` - <:rare_q:781531919140651048>(rare) редкое качесвто, шанс выпадения/крафта 50%\n`o` - <:orate_q:781531996866084874>(orate) оратное качество, шанс выпадения/крафта 25%\n`l` - <:legendary_q:781532085130100737>(legendary) легендарное качество, шанс выпадения/крафта 10%"
                emb = discord.Embed(title = "Качества:",
                description = text, color=server['embed_color'])
                msg1 = await ctx.send(embed = emb)
                await message.edit(embed = embed(type, name, act, image, f"Укажите качество предмета: "))
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
                else:
                    await ctx.send("Вы указали не действительное качество предмета, выберите 1 из (n, u, r, o, l) и повторите создание снова!")
                    return

                item.update({ 'quality': quality})

            try:
                await message.edit(embed = embed(type, name, act, image, quality, f'Укажите описание предмета или `none`: (макс 300 символов)'))
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
                    item.update({ 'description': None})
                elif len(description) > 0 and len(description) < 301:
                    item.update({ 'description': msg.content})
                else:
                    await ctx.send("Требовалось указать описание (макс 300 символов) или `none`, повторите настройку ещё раз!")
                    return

            try:
                await message.edit(embed = embed(type, name, act, image, quality, description, f'Укажите описание предмета или `none`: (макс 2000 символов)'))
                msg = await self.bot.wait_for('message', timeout=60.0, check=lambda message: message.author == ctx.author and message.channel.id == ctx.channel.id)
            except asyncio.TimeoutError:
                await ctx.send("Время вышло.")
                return
            else:
                try:
                    await msg.delete()
                except Exception:
                    pass
                action_m = str(msg.content)
                if action_m == 'none':
                    item.update({ 'action_m': None})
                elif len(action_m) > 0 and len(action_m) < 2001:
                    item.update({ 'action_m': msg.content})
                else:
                    await ctx.send("Требовалось указать сообщение (макс 2к символов) или `none`, повторите настройку ещё раз!")
                    return


            await message.edit(embed = embed( type, name, act, image, quality, description, action_m))

        elif type == 'point':

            def embed(type = 'Не указано', name = 'Не указано', act = 'Не указано', style = 'Не указано', image = 'Не указано', quality = 'Не указано', description = 'Не указано', action_m = 'Не указано'):
                nonlocal server

                emb = discord.Embed(title = "Создание предмета", description = "", color=server['embed_color'])
                emb.add_field(name = "Тип предмета", value = f"{type}")
                emb.add_field(name = "Имя предмета", value = f"{name}")
                emb.add_field(name = "Мощность предмета", value = f"{act}")
                emb.add_field(name = "Стиль предмета", value = f"{style}")
                if image != 'Не указано' and image != 'none' and image != "Укажите изображение предмета:":
                    emb.set_thumbnail(url = image)
                emb.add_field(name = "Качество предмета", value = f"{quality}")
                emb.add_field(name = "Описание предмета", value = f"{description}")
                emb.add_field(name = "Сообщение при активации", value = f"{action_m}")
                emb.set_footer(text = 'Отправляйте сообщения в чат без использованеи команд, на одно указание у вас 60 сек.')
                return emb


            try:
                await message.edit(embed = embed(type, f'Укажите название предмета: (не более 150 символов)'))
                msg = await self.bot.wait_for('message', timeout=60.0, check=lambda message: message.author == ctx.author and message.channel.id == ctx.channel.id)
            except asyncio.TimeoutError:
                await ctx.send("Время вышло.")
                return
            else:
                try:
                    await msg.delete()
                except Exception:
                    pass
                if len(message.content) > 150:
                    await ctx.send("Название больше 150-ти символов")
                    return
                item.update({ 'name': msg.content})
                name = str(msg.content)

            try:
                await message.edit(embed = embed(type, name, f"Укажите мощность `{name}`"))
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
                    await ctx.send("Требовалось указать __число__!")
                    return

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

            try:
                text = "Требуется указать __ссылку__ на изображение или `none`"
                emb = discord.Embed(title = "Изображение:",
                description = text, color=server['embed_color'])
                msg1 = await ctx.send(embed = emb)
                await message.edit(embed = embed(type, name, act, style, "Укажите изображение предмета:"))
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

                item.update({'image': msg.content})
                image = str(msg.content)
                try:
                    await msg1.delete()
                    await msg2.delete()
                except Exception:
                    pass

            try:
                text = "**Качество предмета влияет на процент его выпадения и крафта**\n`n` - <:normal_q:781531816993620001>(normal) обычное качество, шанс выпадения/крафта 100%\n`u` - <:unusual_q:781531868780691476>(unusual) необычное качество, шанс выпадения/крафта 75%\n`r` - <:rare_q:781531919140651048>(rare) редкое качесвто, шанс выпадения/крафта 50%\n`o` - <:orate_q:781531996866084874>(orate) оратное качество, шанс выпадения/крафта 25%\n`l` - <:legendary_q:781532085130100737>(legendary) легендарное качество, шанс выпадения/крафта 10%"
                emb = discord.Embed(title = "Качества:",
                description = text, color=server['embed_color'])
                msg1 = await ctx.send(embed = emb)
                await message.edit(embed = embed(type, name, act, style, image, f"Укажите качество предмета: "))
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
                else:
                    await ctx.send("Вы указали не действительное качество предмета, выберите 1 из (n, u, r, o, l) и повторите создание снова!")
                    return

                item.update({ 'quality': quality})

            try:
                await message.edit(embed = embed(type, name, act, style, image, quality, f'Укажите описание предмета или `none`: (макс 300 символов)'))
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
                    item.update({ 'description': None})
                elif len(description) > 0 and len(description) < 301:
                    item.update({ 'description': msg.content})
                else:
                    await ctx.send("Требовалось указать описание (макс 300 символов) или `none`, повторите настройку ещё раз!")
                    return

            try:
                await message.edit(embed = embed(type, name, act, image, quality, description, f'Укажите описание предмета или `none`: (макс 2000 символов)'))
                msg = await self.bot.wait_for('message', timeout=60.0, check=lambda message: message.author == ctx.author and message.channel.id == ctx.channel.id)
            except asyncio.TimeoutError:
                await ctx.send("Время вышло.")
                return
            else:
                try:
                    await msg.delete()
                except Exception:
                    pass
                action_m = str(msg.content)
                if action_m == 'none':
                    item.update({ 'action_m': None})
                elif len(action_m) > 0 and len(action_m) < 2001:
                    item.update({ 'action_m': msg.content})
                else:
                    await ctx.send("Требовалось указать сообщение (макс 2к символов) или `none`, повторите настройку ещё раз!")
                    return

            await message.edit(embed = embed( type, name, act, style, image, quality, description, action_m))

        elif type == 'case':

            def embed(type = 'Не указано', name = 'Не указано', act = 'Не указано', image = 'Не указано', quality = 'Не указано', description = 'Не указано', action_m = 'Не указано'):
                nonlocal server

                emb = discord.Embed(title = "Создание предмета", description = "", color=server['embed_color'])
                emb.add_field(name = "Тип предмета", value = f"{type}")
                emb.add_field(name = "Имя предмета", value = f"{name}")
                emb.add_field(name = "Выпадаемые предметы", value = f"{act}")
                if image != 'Не указано' and image != 'none' and image != "Укажите изображение предмета:":
                    emb.set_thumbnail(url = image)
                emb.add_field(name = "Качество предмета", value = f"{quality}")
                emb.add_field(name = "Описание предмета", value = f"{description}")
                emb.add_field(name = "Сообщение при активации", value = f"{action_m}")
                emb.set_footer(text = 'Отправляйте сообщения в чат без использованеи команд, на одно указание у вас 60 сек.')
                return emb

            try:
                await message.edit(embed = embed(type, f'Укажите название предмета: (не более 150 символов)'))
                msg = await self.bot.wait_for('message', timeout=60.0, check=lambda message: message.author == ctx.author and message.channel.id == ctx.channel.id)
            except asyncio.TimeoutError:
                await ctx.send("Время вышло.")
                return
            else:
                try:
                    await msg.delete()
                except Exception:
                    pass
                if len(message.content) > 150:
                    await ctx.send("Название больше 150-ти символов")
                    return
                item.update({ 'name': msg.content})
                name = str(msg.content)

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

            try:
                text = "Требуется указать __ссылку__ на изображение или `none`"
                emb = discord.Embed(title = "Изображение:",
                description = text, color=server['embed_color'])
                msg1 = await ctx.send(embed = emb)
                await message.edit(embed = embed(type, name, act, "Укажите изображение предмета:"))
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

                item.update({'image': msg.content})
                image = str(msg.content)
                try:
                    await msg1.delete()
                    await msg2.delete()
                except Exception:
                    pass

            try:
                text = "**Качество предмета влияет на процент его выпадения и крафта**\n`n` - <:normal_q:781531816993620001>(normal) обычное качество, шанс выпадения/крафта 100%\n`u` - <:unusual_q:781531868780691476>(unusual) необычное качество, шанс выпадения/крафта 75%\n`r` - <:rare_q:781531919140651048>(rare) редкое качесвто, шанс выпадения/крафта 50%\n`o` - <:orate_q:781531996866084874>(orate) оратное качество, шанс выпадения/крафта 25%\n`l` - <:legendary_q:781532085130100737>(legendary) легендарное качество, шанс выпадения/крафта 10%"
                emb = discord.Embed(title = "Качества:",
                description = text, color=server['embed_color'])
                msg1 = await ctx.send(embed = emb)
                await message.edit(embed = embed(type, name, act, image, f"Укажите качество предмета: "))
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
                else:
                    await ctx.send("Вы указали не действительное качество предмета, выберите 1 из (n, u, r, o, l) и повторите создание снова!")
                    return

                item.update({ 'quality': quality})

            try:
                await message.edit(embed = embed(type, name, act, image, quality, f'Укажите описание предмета или `none`: (макс 300 символов)'))
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
                    item.update({ 'description': None})
                elif len(description) > 0 and len(description) < 301:
                    item.update({ 'description': msg.content})
                else:
                    await ctx.send("Требовалось указать описание (макс 300 символов) или `none`, повторите настройку ещё раз!")
                    return

            await message.edit(embed = embed( type, name, act, image, quality, description, action_m))

        elif type == 'armor':

            def embed(type = 'Не указано', name = 'Не указано', act = 'Не указано', style = 'Не указано', image = 'Не указано', quality = 'Не указано', description = 'Не указано', action_m = 'Не указано'):
                nonlocal server

                emb = discord.Embed(title = "Создание предмета", description = "", color=server['embed_color'])
                emb.add_field(name = "Тип предмета", value = f"{type}")
                emb.add_field(name = "Имя предмета", value = f"{name}")
                emb.add_field(name = "Защита предмета", value = f"{act}")
                emb.add_field(name = "Стиль предмета", value = f"{style}")
                if image != 'Не указано' and image != 'none' and image != "Укажите изображение предмета:":
                    emb.set_thumbnail(url = image)
                emb.add_field(name = "Качество предмета", value = f"{quality}")
                emb.add_field(name = "Описание предмета", value = f"{description}")
                emb.add_field(name = "Сообщение при активации", value = f"{action_m}")
                emb.set_footer(text = 'Отправляйте сообщения в чат без использованеи команд, на одно указание у вас 60 сек.')
                return emb


            try:
                await message.edit(embed = embed(type, f'Укажите название предмета: (не более 150 символов)'))
                msg = await self.bot.wait_for('message', timeout=60.0, check=lambda message: message.author == ctx.author and message.channel.id == ctx.channel.id)
            except asyncio.TimeoutError:
                await ctx.send("Время вышло.")
                return
            else:
                try:
                    await msg.delete()
                except Exception:
                    pass
                if len(message.content) > 150:
                    await ctx.send("Название больше 150-ти символов")
                    return
                item.update({ 'name': msg.content})
                name = str(msg.content)

            try:
                await message.edit(embed = embed(type, name, f"Укажите защиту `{name}`"))
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
                    await ctx.send("Требовалось указать __число__!")
                    return

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

            try:
                text = "Требуется указать __ссылку__ на изображение или `none`"
                emb = discord.Embed(title = "Изображение:",
                description = text, color=server['embed_color'])
                msg1 = await ctx.send(embed = emb)
                await message.edit(embed = embed(type, name, act, style, "Укажите изображение предмета:"))
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

                item.update({'image': msg.content})
                image = str(msg.content)
                try:
                    await msg1.delete()
                    await msg2.delete()
                except Exception:
                    pass

            try:
                text = "**Качество предмета влияет на процент его выпадения и крафта**\n`n` - <:normal_q:781531816993620001>(normal) обычное качество, шанс выпадения/крафта 100%\n`u` - <:unusual_q:781531868780691476>(unusual) необычное качество, шанс выпадения/крафта 75%\n`r` - <:rare_q:781531919140651048>(rare) редкое качесвто, шанс выпадения/крафта 50%\n`o` - <:orate_q:781531996866084874>(orate) оратное качество, шанс выпадения/крафта 25%\n`l` - <:legendary_q:781532085130100737>(legendary) легендарное качество, шанс выпадения/крафта 10%"
                emb = discord.Embed(title = "Качества:",
                description = text, color=server['embed_color'])
                msg1 = await ctx.send(embed = emb)
                await message.edit(embed = embed(type, name, act, style, image, f"Укажите качество предмета: "))
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
                else:
                    await ctx.send("Вы указали не действительное качество предмета, выберите 1 из (n, u, r, o, l) и повторите создание снова!")
                    return

                item.update({ 'quality': quality})

            try:
                await message.edit(embed = embed(type, name, act, style, image, quality, f'Укажите описание предмета или `none`: (макс 300 символов)'))
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
                    item.update({ 'description': None})
                elif len(description) > 0 and len(description) < 301:
                    item.update({ 'description': msg.content})
                else:
                    await ctx.send("Требовалось указать описание (макс 300 символов) или `none`, повторите настройку ещё раз!")
                    return

            await message.edit(embed = embed( type, name, act, style, image, quality, description, action_m))


        elif type == 'weapon':

            def embed(type = 'Не указано', name = 'Не указано', act = 'Не указано', style = 'Не указано', image = 'Не указано', quality = 'Не указано', description = 'Не указано', action_m = 'Не указано'):
                nonlocal server

                emb = discord.Embed(title = "Создание предмета", description = "", color=server['embed_color'])
                emb.add_field(name = "Тип предмета", value = f"{type}")
                emb.add_field(name = "Имя предмета", value = f"{name}")
                emb.add_field(name = "Урон предмета", value = f"{act}")
                emb.add_field(name = "Стиль предмета", value = f"{style}")
                if image != 'Не указано' and image != 'none' and image != "Укажите изображение предмета:":
                    emb.set_thumbnail(url = image)
                emb.add_field(name = "Качество предмета", value = f"{quality}")
                emb.add_field(name = "Описание предмета", value = f"{description}")
                emb.add_field(name = "Сообщение при активации", value = f"{action_m}")
                emb.set_footer(text = 'Отправляйте сообщения в чат без использованеи команд, на одно указание у вас 60 сек.')
                return emb


            try:
                await message.edit(embed = embed(type, f'Укажите название предмета: (не более 150 символов)'))
                msg = await self.bot.wait_for('message', timeout=60.0, check=lambda message: message.author == ctx.author and message.channel.id == ctx.channel.id)
            except asyncio.TimeoutError:
                await ctx.send("Время вышло.")
                return
            else:
                try:
                    await msg.delete()
                except Exception:
                    pass
                if len(message.content) > 150:
                    await ctx.send("Название больше 150-ти символов")
                    return
                item.update({ 'name': msg.content})
                name = str(msg.content)

            try:
                await message.edit(embed = embed(type, name, f"Укажите урон `{name}`"))
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
                    await ctx.send("Требовалось указать __число__!")
                    return

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

            try:
                text = "Требуется указать __ссылку__ на изображение или `none`"
                emb = discord.Embed(title = "Изображение:",
                description = text, color=server['embed_color'])
                msg1 = await ctx.send(embed = emb)
                await message.edit(embed = embed(type, name, act, style, "Укажите изображение предмета:"))
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

                item.update({'image': msg.content})
                image = str(msg.content)
                try:
                    await msg1.delete()
                    await msg2.delete()
                except Exception:
                    pass

            try:
                text = "**Качество предмета влияет на процент его выпадения и крафта**\n`n` - <:normal_q:781531816993620001>(normal) обычное качество, шанс выпадения/крафта 100%\n`u` - <:unusual_q:781531868780691476>(unusual) необычное качество, шанс выпадения/крафта 75%\n`r` - <:rare_q:781531919140651048>(rare) редкое качесвто, шанс выпадения/крафта 50%\n`o` - <:orate_q:781531996866084874>(orate) оратное качество, шанс выпадения/крафта 25%\n`l` - <:legendary_q:781532085130100737>(legendary) легендарное качество, шанс выпадения/крафта 10%"
                emb = discord.Embed(title = "Качества:",
                description = text, color=server['embed_color'])
                msg1 = await ctx.send(embed = emb)
                await message.edit(embed = embed(type, name, act, style, image, f"Укажите качество предмета: "))
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
                else:
                    await ctx.send("Вы указали не действительное качество предмета, выберите 1 из (n, u, r, o, l) и повторите создание снова!")
                    return

                item.update({ 'quality': quality})

            try:
                await message.edit(embed = embed(type, name, act, style, image, quality, f'Укажите описание предмета или `none`: (макс 300 символов)'))
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
                    item.update({ 'description': None})
                elif len(description) > 0 and len(description) < 301:
                    item.update({ 'description': msg.content})
                else:
                    await ctx.send("Требовалось указать описание (макс 300 символов) или `none`, повторите настройку ещё раз!")
                    return

            try:
                await message.edit(embed = embed(type, name, act, image, quality, description, f'Укажите описание предмета или `none`: (макс 2000 символов)'))
                msg = await self.bot.wait_for('message', timeout=60.0, check=lambda message: message.author == ctx.author and message.channel.id == ctx.channel.id)
            except asyncio.TimeoutError:
                await ctx.send("Время вышло.")
                return
            else:
                try:
                    await msg.delete()
                except Exception:
                    pass
                action_m = str(msg.content)
                if action_m == 'none':
                    item.update({ 'action_m': None})
                elif len(action_m) > 0 and len(action_m) < 2001:
                    item.update({ 'action_m': msg.content})
                else:
                    await ctx.send("Требовалось указать сообщение (макс 2к символов) или `none`, повторите настройку ещё раз!")
                    return

            await message.edit(embed = embed( type, name, act, style, image, quality, description, action_m))

        elif type == 'pet':

            def embed(type = 'Не указано', name = 'Не указано', act = 'Не указано', style = 'Не указано', image = 'Не указано', quality = 'Не указано', description = 'Не указано', action_m = 'Не указано'):

                emb = discord.Embed(title = "Создание предмета", description = "", color=server['embed_color'])
                emb.add_field(name = "Тип предмета", value = f"{type}")
                emb.add_field(name = "Имя предмета", value = f"{name}")
                emb.add_field(name = "Урон предмета", value = f"{act}")
                emb.add_field(name = "Стиль предмета", value = f"{style}")
                if image != 'Не указано' and image != 'none' and image != "Укажите изображение предмета:":
                    emb.set_thumbnail(url = image)
                emb.add_field(name = "Качество предмета", value = f"{quality}")
                emb.add_field(name = "Описание предмета", value = f"{description}")
                emb.add_field(name = "Сообщение при активации", value = f"{action_m}")
                emb.set_footer(text = 'Отправляйте сообщения в чат без использованеи команд, на одно указание у вас 60 сек.')
                return emb


            try:
                await message.edit(embed = embed(type, f'Укажите название предмета: (не более 150 символов)'))
                msg = await self.bot.wait_for('message', timeout=60.0, check=lambda message: message.author == ctx.author and message.channel.id == ctx.channel.id)
            except asyncio.TimeoutError:
                await ctx.send("Время вышло.")
                return
            else:
                try:
                    await msg.delete()
                except Exception:
                    pass
                if len(message.content) > 150:
                    await ctx.send("Название больше 150-ти символов")
                    return
                item.update({ 'name': msg.content})
                name = str(msg.content)

            try:
                await message.edit(embed = embed(type, name, f"Укажите эффективность `{name}`"))
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
                    await ctx.send("Требовалось указать __число__!")
                    return

                item.update({ 'act': act})

            text = "`hp+` - бонус к здоровью.\n`mana+` - бонус кмане.\n`damage+` - бонус к урону.\n`armor+` - бонус к защите при активации брони.\n`heal+` - бонус к здоровью при использовании зелья.\n`mn+` - бонус к мане при использовании.\n"

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

                if msg.content in ['hp+', 'mana+', "damage+", "armor+", "heal+", "mn+"]:
                    item.update({ 'style': msg.content})
                else:
                    await ctx.send("Вы указали не действительный стиль предмета, выберите 1 из (hp+, mana+, damage+, armor+, heal+, mn+) и повторите создание снова!")
                    return

                style = msg.content

            try:
                text = "Требуется указать __ссылку__ на изображение или `none`"
                emb = discord.Embed(title = "Изображение:",
                description = text, color=server['embed_color'])
                msg1 = await ctx.send(embed = emb)
                await message.edit(embed = embed(type, name, act, style, "Укажите изображение предмета:"))
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

                item.update({'image': msg.content})
                image = str(msg.content)
                try:
                    await msg1.delete()
                    await msg2.delete()
                except Exception:
                    pass

            try:
                text = "**Качество предмета влияет на процент его выпадения и крафта**\n`n` - <:normal_q:781531816993620001>(normal) обычное качество, шанс выпадения/крафта 100%\n`u` - <:unusual_q:781531868780691476>(unusual) необычное качество, шанс выпадения/крафта 75%\n`r` - <:rare_q:781531919140651048>(rare) редкое качесвто, шанс выпадения/крафта 50%\n`o` - <:orate_q:781531996866084874>(orate) оратное качество, шанс выпадения/крафта 25%\n`l` - <:legendary_q:781532085130100737>(legendary) легендарное качество, шанс выпадения/крафта 10%"
                emb = discord.Embed(title = "Качества:",
                description = text, color=server['embed_color'])
                msg1 = await ctx.send(embed = emb)
                await message.edit(embed = embed(type, name, act, style, image, f"Укажите качество питомца: "))
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
                else:
                    await ctx.send("Вы указали не действительное качество предмета, выберите 1 из (n, u, r, o, l) и повторите создание снова!")
                    return

                item.update({ 'quality': quality})

            try:
                await message.edit(embed = embed(type, name, act, style, image, quality, f'Укажите описание предмета или `none`: (макс 300 символов)'))
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
                    item.update({ 'description': None})
                elif len(description) > 0 and len(description) < 301:
                    item.update({ 'description': msg.content})
                else:
                    await ctx.send("Требовалось указать описание (макс 300 символов) или `none`, повторите настройку ещё раз!")
                    return

            await message.edit(embed = embed( type, name, act, style, image, quality, description))

        elif type == 'material':

            def embed(type = 'Не указано', name = 'Не указано', image = 'Не указано', quality = 'Не указано', description = 'Не указано'):
                nonlocal server

                emb = discord.Embed(title = "Создание предмета", description = "", color=server['embed_color'])
                emb.add_field(name = "Тип предмета", value = f"{type}")
                emb.add_field(name = "Имя предмета", value = f"{name}")
                if image != 'Не указано' and image != 'none' and image != "Укажите изображение предмета:":
                    emb.set_thumbnail(url = image)
                emb.add_field(name = "Качество предмета", value = f"{quality}")
                emb.add_field(name = "Описание предмета", value = f"{description}")
                emb.set_footer(text = 'Отправляйте сообщения в чат без использованеи команд, на одно указание у вас 60 сек.')
                return emb

            try:
                await message.edit(embed = embed(type, f'Укажите название предмета: (не более 150 символов)'))
                msg = await self.bot.wait_for('message', timeout=60.0, check=lambda message: message.author == ctx.author and message.channel.id == ctx.channel.id)
            except asyncio.TimeoutError:
                await ctx.send("Время вышло.")
                return
            else:
                try:
                    await msg.delete()
                except Exception:
                    pass
                if len(message.content) > 150:
                    await ctx.send("Название больше 150-ти символов")
                    return
                item.update({ 'name': msg.content})
                name = str(msg.content)

            try:
                text = "Требуется указать __ссылку__ на изображение или `none`"
                emb = discord.Embed(title = "Изображение:",
                description = text, color=server['embed_color'])
                msg1 = await ctx.send(embed = emb)
                await message.edit(embed = embed(type, name, "Укажите изображение предмета:"))
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

                item.update({'image': msg.content})
                image = str(msg.content)
                try:
                    await msg1.delete()
                    await msg2.delete()
                except Exception:
                    pass

            try:
                text = "**Качество предмета влияет на процент его выпадения и крафта**\n`n` - <:normal_q:781531816993620001>(normal) обычное качество, шанс выпадения/крафта 100%\n`u` - <:unusual_q:781531868780691476>(unusual) необычное качество, шанс выпадения/крафта 75%\n`r` - <:rare_q:781531919140651048>(rare) редкое качесвто, шанс выпадения/крафта 50%\n`o` - <:orate_q:781531996866084874>(orate) оратное качество, шанс выпадения/крафта 25%\n`l` - <:legendary_q:781532085130100737>(legendary) легендарное качество, шанс выпадения/крафта 10%"
                emb = discord.Embed(title = "Качества:",
                description = text, color=server['embed_color'])
                msg1 = await ctx.send(embed = emb)
                await message.edit(embed = embed(type, name, image, f"Укажите качество предмета: "))
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
                else:
                    await ctx.send("Вы указали не действительное качество предмета, выберите 1 из (n, u, r, o, l) и повторите создание снова!")
                    return

                item.update({ 'quality': quality})

            try:
                await message.edit(embed = embed(type, name, image, quality, f'Укажите описание предмета или `none`: (макс 300 символов)'))
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
                    item.update({ 'description': None})
                elif len(description) > 0 and len(description) < 301:
                    item.update({ 'description': msg.content})
                else:
                    await ctx.send("Требовалось указать описание (макс 300 символов) или `none`, повторите настройку ещё раз!")
                    return

            await message.edit(embed = embed( type, name, image, quality, description))

        elif type == 'recipe':

            def embed(type = 'Не указано', name = 'Не указано', act = 'Не указано', ndi = 'Не указано', create = 'Не указано', image = 'Не указано', quality = 'Не указано', description = 'Не указано', action_m = 'Не указано'):
                nonlocal server

                emb = discord.Embed(title = "Создание предмета", description = "", color=server['embed_color'])
                emb.add_field(name = "Тип предмета", value = f"{type}")
                emb.add_field(name = "Имя предмета", value = f"{name}")
                emb.add_field(name = "Используемые предметы", value = f"{act}")
                emb.add_field(name = "Не удаляемые предметы", value = f"{ndi}")
                emb.add_field(name = "Создаваемые предметы", value = f"{create}")
                if image != 'Не указано' and image != 'none' and image != "Укажите изображение предмета:":
                    emb.set_thumbnail(url = image)
                emb.add_field(name = "Качество предмета", value = f"{quality}")
                emb.add_field(name = "Описание предмета", value = f"{description}")
                emb.add_field(name = "Сообщение при активации", value = f"{action_m}")
                emb.set_footer(text = 'Отправляйте сообщения в чат без использованеи команд, на одно указание у вас 60 сек.')
                return emb

            try:
                await message.edit(embed = embed(type, f'Укажите название предмета: (не более 150 символов)'))
                msg = await self.bot.wait_for('message', timeout=60.0, check=lambda message: message.author == ctx.author and message.channel.id == ctx.channel.id)
            except asyncio.TimeoutError:
                await ctx.send("Время вышло.")
                return
            else:
                try:
                    await msg.delete()
                except Exception:
                    pass
                if len(message.content) > 150:
                    await ctx.send("Название больше 150-ти символов")
                    return
                item.update({ 'name': msg.content})
                name = str(msg.content)

            try:
                if server['premium'] == None:
                    b = 10
                else:
                    b = 25

                act = []
                emb = discord.Embed(title = "",
                description = "Укажите id предметов для крафта, формат: 12 12 1 2 2\nЕсли вы хотите увеличить колличество предмета то просто укажите его повторно, пример: 11 11 (будет удалено 2 предмета с id 11)", color=server['embed_color'])
                msg1 = await ctx.send(embed = emb)
                await message.edit(embed = embed(type, name, f"Укажите id предметов для крафта: (максимум {b} предметов)"))
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
                await message.edit(embed = embed(type, name, act, f"Укажите метод рецепта "))
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
                    list = []

                    pr = set(act1) & set(msg.content.split())
                    for i in pr:
                        list.append(i)


                    if list == msg.content.split():
                        ndi = msg.content.split()
                    else:
                        await ctx.send("Требовалось указать предметы из крафта которые не будут удаляться!")
                        return

                    item.update({ 'ndi': ndi})

            try:

                if server['premium'] == None:
                    b = 5
                else:
                    b = 15

                emb = discord.Embed(title = "",
                description = "Укажите id создаваемых предметов, формат: 12 12 1 2 2\nЕсли вы хотите увеличить колличество предмета то просто укажите его повторно, пример: 11 11 (будет создано 2 предмета с id 11)", color=server['embed_color'])
                msg1 = await ctx.send(embed = emb)
                await message.edit(embed = embed(type, name, act, ndi, f"Укажите id  предметов которые будут созданы: (максимум {b} предметов)"))
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
                text = "Требуется указать __ссылку__ на изображение или `none`"
                emb = discord.Embed(title = "Изображение:",
                description = text, color=server['embed_color'])
                msg1 = await ctx.send(embed = emb)
                await message.edit(embed = embed(type, name, act, ndi, create, "Укажите изображение предмета:"))
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

                item.update({'image': msg.content})
                image = str(msg.content)
                try:
                    await msg1.delete()
                    await msg2.delete()
                except Exception:
                    pass

            try:
                text = "**Качество предмета влияет на процент его выпадения и крафта**\n`n` - <:normal_q:781531816993620001>(normal) обычное качество, шанс выпадения/крафта 100%\n`u` - <:unusual_q:781531868780691476>(unusual) необычное качество, шанс выпадения/крафта 75%\n`r` - <:rare_q:781531919140651048>(rare) редкое качесвто, шанс выпадения/крафта 50%\n`o` - <:orate_q:781531996866084874>(orate) оратное качество, шанс выпадения/крафта 25%\n`l` - <:legendary_q:781532085130100737>(legendary) легендарное качество, шанс выпадения/крафта 10%"
                emb = discord.Embed(title = "Качества:",
                description = text, color=server['embed_color'])
                msg1 = await ctx.send(embed = emb)
                await message.edit(embed = embed(type, name, act, ndi, create, image, f"Укажите качество питомца: "))
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
                else:
                    await ctx.send("Вы указали не действительное качество предмета, выберите 1 из (n, u, r, o, l) и повторите создание снова!")
                    return

                item.update({ 'quality': quality})

            try:
                await message.edit(embed = embed(type, name, act, ndi, create, image, quality, f'Укажите описание предмета или `none`: (макс 300 символов)'))
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
                    item.update({ 'description': None})
                elif len(description) > 0 and len(description) < 301:
                    item.update({ 'description': msg.content})
                else:
                    await ctx.send("Требовалось указать описание (макс 300 символов) или `none`, повторите настройку ещё раз!")
                    return

            try:
                await message.edit(embed = embed(type, name, act, image, quality, description, f'Укажите описание предмета или `none`: (макс 2000 символов)'))
                msg = await self.bot.wait_for('message', timeout=60.0, check=lambda message: message.author == ctx.author and message.channel.id == ctx.channel.id)
            except asyncio.TimeoutError:
                await ctx.send("Время вышло.")
                return
            else:
                try:
                    await msg.delete()
                except Exception:
                    pass
                action_m = str(msg.content)
                if action_m == 'none':
                    item.update({ 'action_m': None})
                elif len(action_m) > 0 and len(action_m) < 2001:
                    item.update({ 'action_m': msg.content})
                else:
                    await ctx.send("Требовалось указать сообщение (макс 2к символов) или `none`, повторите настройку ещё раз!")
                    return

            await message.edit(embed = embed( type, name, act, ndi, create, image, quality, description, action_m))

        elif type == 'role':

            def embed(type = 'Не указано', name = 'Не указано', act = 'Не указано', style = 'Не указано', image = 'Не указано', quality = 'Не указано', description = 'Не указано', action_m = 'Не указано'):
                nonlocal server

                emb = discord.Embed(title = "Создание предмета", description = "", color=server['embed_color'])
                emb.add_field(name = "Тип предмета", value = f"{type}")
                emb.add_field(name = "Имя предмета", value = f"{name}")
                if act == 'Не указано' or act == f"Укажите [id](https://support.discord.com/hc/ru/articles/206346498-%D0%93%D0%B4%D0%B5-%D0%BC%D0%BD%D0%B5-%D0%BD%D0%B0%D0%B9%D1%82%D0%B8-ID-%D0%BF%D0%BE%D0%BB%D1%8C%D0%B7%D0%BE%D0%B2%D0%B0%D1%82%D0%B5%D0%BB%D1%8F-%D1%81%D0%B5%D1%80%D0%B2%D0%B5%D1%80%D0%B0-%D1%81%D0%BE%D0%BE%D0%B1%D1%89%D0%B5%D0%BD%D0%B8%D1%8F-) роли `{name}`":
                    emb.add_field(name = "Id роли", value = f"{act}")
                else:
                    emb.add_field(name = "Id роли", value = f"<@&{act}>")
                emb.add_field(name = "Стиль предмета", value = f"{style}")
                if image != 'Не указано' and image != 'none' and image != "Укажите изображение предмета:":
                    emb.set_thumbnail(url = image)
                emb.add_field(name = "Качество предмета", value = f"{quality}")
                emb.add_field(name = "Описание предмета", value = f"{description}")
                emb.add_field(name = "Сообщение при активации", value = f"{action_m}")
                emb.set_footer(text = 'Отправляйте сообщения в чат без использованеи команд, на одно указание у вас 60 сек.')
                return emb


            try:
                await message.edit(embed = embed(type, f'Укажите название предмета: (не более 150 символов)'))
                msg = await self.bot.wait_for('message', timeout=60.0, check=lambda message: message.author == ctx.author and message.channel.id == ctx.channel.id)
            except asyncio.TimeoutError:
                await ctx.send("Время вышло.")
                return
            else:
                try:
                    await msg.delete()
                except Exception:
                    pass
                if len(message.content) > 150:
                    await ctx.send("Название больше 150-ти символов")
                    return
                item.update({ 'name': msg.content})
                name = str(msg.content)

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

            try:
                text = "Требуется указать __ссылку__ на изображение или `none`"
                emb = discord.Embed(title = "Изображение:",
                description = text, color=server['embed_color'])
                msg1 = await ctx.send(embed = emb)
                await message.edit(embed = embed(type, name, act, style, "Укажите изображение предмета:"))
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

                item.update({'image': msg.content})
                image = str(msg.content)
                try:
                    await msg1.delete()
                    await msg2.delete()
                except Exception:
                    pass

            try:
                text = "**Качество предмета влияет на процент его выпадения и крафта**\n`n` - <:normal_q:781531816993620001>(normal) обычное качество, шанс выпадения/крафта 100%\n`u` - <:unusual_q:781531868780691476>(unusual) необычное качество, шанс выпадения/крафта 75%\n`r` - <:rare_q:781531919140651048>(rare) редкое качесвто, шанс выпадения/крафта 50%\n`o` - <:orate_q:781531996866084874>(orate) оратное качество, шанс выпадения/крафта 25%\n`l` - <:legendary_q:781532085130100737>(legendary) легендарное качество, шанс выпадения/крафта 10%"
                emb = discord.Embed(title = "Качества:",
                description = text, color=server['embed_color'])
                msg1 = await ctx.send(embed = emb)
                await message.edit(embed = embed(type, name, act, style, image, f"Укажите качество предмета: "))
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
                else:
                    await ctx.send("Вы указали не действительное качество предмета, выберите 1 из (n, u, r, o, l) и повторите создание снова!")
                    return

                item.update({ 'quality': quality})

            try:
                await message.edit(embed = embed(type, name, act, style, image, quality, f'Укажите описание предмета или `none`: (макс 300 символов)'))
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
                    item.update({ 'description': None})
                elif len(description) > 0 and len(description) < 301:
                    item.update({ 'description': msg.content})
                else:
                    await ctx.send("Требовалось указать описание (макс 300 символов) или `none`, повторите настройку ещё раз!")
                    return

            try:
                await message.edit(embed = embed(type, name, act, image, quality, description, f'Укажите описание предмета или `none`: (макс 2000 символов)'))
                msg = await self.bot.wait_for('message', timeout=60.0, check=lambda message: message.author == ctx.author and message.channel.id == ctx.channel.id)
            except asyncio.TimeoutError:
                await ctx.send("Время вышло.")
                return
            else:
                try:
                    await msg.delete()
                except Exception:
                    pass
                action_m = str(msg.content)
                if action_m == 'none':
                    item.update({ 'action_m': None})
                elif len(action_m) > 0 and len(action_m) < 2001:
                    item.update({ 'action_m': msg.content})
                else:
                    await ctx.send("Требовалось указать сообщение (макс 2к символов) или `none`, повторите настройку ещё раз!")
                    return

            await message.edit(embed = embed( type, name, act, style, image, quality, description, action_m))

        try:
            l = server['items']
            list = []
            for i in l.keys():
                list.append(int(i))
            l = max(list)+1
        except Exception:
            l = 1

        await ctx.send(f"Предмет с id {l} создан!")

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

        print(race)




    # @commands.command(usage = '', description = '') #смээээээээээээээээээээээээээээээээээээрт
    # async def use(self, ctx, iid:int):
    #
    #     user = funs.user_check(ctx.author, ctx.guild)
    #     server = servers.find_one({"server": ctx.guild.id})
    #
    #     try:
    #         await

    @commands.command(usage = '(id)', description = 'Информация о предмете.')
    async def item_info(self, ctx, id:int):

        server = servers.find_one({"server": ctx.guild.id})

        act_title = '-'

        try:
            server['items'][str(id)]
        except Exception:
            await ctx.send(f"Указанный вами предмет не найден!\nПредметы: {', '.join(str(x) for x in list(server['items'].keys()) )} ")
            return

        item = server['items'][str(id)]

        act = server['items'][str(id)]['act']

        style = item['style']

        quality = item['quality']

        type = server['items'][str(id)]['type']
        ttype = type.replace('eat', f'🍖 | Еда')
        ttype = type.replace('point', f'<:mana:780352235246452756> | Зелье')
        ttype = type.replace('case', f'<:chest:827218232783405097> | Сундук сокровищ')
        ttype = type.replace('armor', f'<:armor:827220888130682880> | Броня')
        ttype = type.replace('pet', f'<:pet:780381475207905290> | Питомец')
        ttype = type.replace('material', f'<:leather:783036521099034626> | Материал')
        ttype = type.replace('recipe', f'<:recipe:827221967886745600> | Рецепт')
        ttype = type.replace('role', f'<:icons8pokeball96:779718625459437608> | Роль')
        if type == 'weapon':
            if item['style'] == 'sword':
                type = type.replace('weapon', f'<:katana:827215937677426738> | Оружие ближнего боя')
            if item['style'] == 'staff':
                type = type.replace('weapon', f'<:staff:827215895548919869> | Оружие магического типа')
            if item['style'] == 'bow':
                type = type.replace('weapon', f'<:longrangeweapon:827217317544984607> | Оружие дальнего боя')

        if type == 'eat':
            act_title = 'Питательность'

        if type == 'point':
            if style == 'heal':
                act_title = 'Восстановление здоровья'
            if style == 'mana':
                act_title = 'Восстановление маны'

        if type == 'case':
            act_title = 'Сундук удачи'

        if type == 'armor':
            if style == 'add':
                act_title = 'Добавление брони'
            if style == 'set':
                act_title = 'Установка брони'

        if type == 'weapon':
            act_title = 'Урон'

        if type == 'pet':
            if style == 'hp+':
                act_title = 'Бонус к здоровью'
            if style == 'mana+':
                act_title = 'Бонус к мане'
            if style == 'damage+':
                act_title = 'Бонус к урону'
            if style == 'armor+':
                act_title = 'Бонус к защите'
            if style == 'heal+':
                act_title = 'Бонус восстановления здоровья'
            if style == 'mn+':
                act_title = 'Бонус восстановления маны'

        if type == 'recipe':
            act_title = 'Рецепт'
            ct = act
            act  = f"Материалы: {ct['items']}\nСоздаёт: {server['items'][str(ct['create']['name'])]}"

        if type == 'role':
            act = f'<@&{act}>'
            if style == 'add':
                act_title = 'Добавление роли'
            if style == 'remove':
                act_title = 'Удаление роли'

        if quality == 'n':
            quality = ''


        emb = discord.Embed(title = item['name'], color=server['embed_color'])
        emb.add_field(name='Тип', value= ttype)

        if type != 'material':
            emb.add_field(name=act_title, value= act)



        if item['description'] != None:
            emb.add_field(name='Описание:', value= item['description'])

        await ctx.send(embed = emb)

def setup(bot):
    bot.add_cog(rpg(bot))
