import nextcord as discord
from nextcord.ext import tasks, commands
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


class economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.command(usage = '(met) (@member) (amout) (met2)', description = 'Редактирование пользователя.', help = 'Управление')
    async def edit_user(self,ctx, met:str, member:discord.Member, amout:int, met2:str):
        if funs.roles_check(ctx.author, ctx.guild.id) == False:
            await ctx.send("У вас недостаточно прав для использования этой команды!")
            return
        server = servers.find_one({"server": ctx.guild.id})

        if amout <= 0:
            await ctx.send(f"Возьми одно яблоко и добавь к нему {amout} яблок. Есть тут смысл?")
            return
        if met in ['money', 'lvl', 'xp', 'hp', 'hpmax', 'mana', 'manamax']:
            user = funs.user_check(member, ctx.guild)
            if met2 == 'add' or met2 == 'remove':
                if met2 == 'add':
                    funs.user_update(member.id, ctx.guild, met, user[met] + amout)
                if met2 == 'remove':
                    if user[met] - amout <= 0:
                        funs.user_update(member.id, ctx.guild, met, 0)
                    else:
                        funs.user_update(member.id, ctx.guild, met, user[met] - amout)
            else:
                await ctx.send("Выберите метод add/remove")
                return

            user = funs.user_check(member, ctx.guild)
            emb = discord.Embed(title="Пользователь Обновлён", description=f"Пользователь: {member.mention}\nОбновлено: {met}\nМетод: {met2}\nУ пользователя: {user[met]}",color=server['embed_color'])
            await ctx.send(embed = emb)

        else:
            await ctx.send("Выберите что вы изменятете bank/money/lvl/xp/hp/hpmax/mana/manamax")


    @commands.command(usage = '(@member) (amout)', description = 'Передача монет пользователю.', help = 'Взаимодействие', aliases = ['дать_монеты'])
    async def give_money(self,ctx,member:discord.Member, amout):
        if ctx.author.id == member.id:
            await ctx.send(f"Есть смысл дарить подарок самому себе?")
            return

        if amout != 'all' and int(amout) <= 0:
            await ctx.send(f"Возьми одно яблоко и добавь к нему {amout} яблок. Есть тут смысл?")
            return

        user = funs.user_check(ctx.author, ctx.guild)

        if amout == 'all':
            amout = user['money']

        try:
            amout = int(amout)
        except Exception:
            await ctx.send("Укажите число или all")
            return

        if user['money'] < amout:
            await ctx.send(f"У вас нету столько монет в кошельке!")
            return

        user2 = funs.user_check(member, ctx.guild)

        funs.user_update(ctx.author.id, ctx.guild, "money", user['money'] - amout)
        funs.user_update(member.id, ctx.guild, "money", user2['money'] + amout)

        emb = discord.Embed(description=f"{ctx.author.mention} вы передали {member.mention} {amout} монет!", color=0x450fa8)
        emb.set_author(name = "Магическая транзакция")
        await ctx.send(embed = emb)

    @commands.command(usage = '(@member)', description = 'Сброс монет пользователя.', help = 'Управление')
    async def reset_money(self,ctx, member:discord.Member):
        if funs.roles_check(ctx.author, ctx.guild.id) == False:
            await ctx.send("У вас недостаточно прав для использования этой команды!")
            return
        funs.user_update(member.id, ctx.guild, "money", 0)
        server = servers.find_one({"server": ctx.guild.id})

        emb = discord.Embed(description=f"Все монеты пользователя {member.mention} были сброшены!", color=server['embed_color'])
        await ctx.send(embed = emb)

    @commands.command(usage = '-', description = 'Сброс монет всех пользователей.', help = 'Управление')
    async def reset_economy(self,ctx):
        if funs.roles_check(ctx.author, ctx.guild.id) == False:
            await ctx.send("У вас недостаточно прав для использования этой команды!")
            return
        server = servers.find_one({"server": ctx.guild.id})
        for user in server['users']:
            funs.user_update(user, ctx.guild, "money", 0)

        emb = discord.Embed(description=f"Экономика была полностью сброшена!", color=0x450fa8)
        await ctx.send(embed = emb)

    @commands.command(aliases=['top','лидеры','топ'], usage = '(name) [number_page]', description = 'Лидеры.', help = 'Взаимодействие')
    async def leaderboard(self,ctx, topname:str = 'lvl', numberpage:int = 1):
        if topname not in ['lvl', 'money', 'voice']:
            await ctx.send("Укажите действительный топ! (lvl, money, voice)")
            return

        server = servers.find_one({"server": ctx.guild.id})
        cc = server['economy']['currency']

        solutions = ['◀', '▶', '📱', '❌']
        member = ctx.author
        reaction = 'a'

        met = 'pc'

        if topname == 'lvl':
            top = list(sorted(server['users'].items(),key=lambda x: x[1]['lvl'],reverse=True))
        elif topname == 'money':
            top = list(sorted(server['users'].items(),key=lambda x: x[1]['money'],reverse=True))
        elif topname == 'voice':
            top = list(sorted(server['users'].items(),key=lambda x: x[1]['voice_time'],reverse=True))

        if len(top) % 5 != 0:
            l = int(len(top) / 5 + 1)
        else:
            l = int(len(top) / 5)

        if numberpage > l or numberpage < 1:
            await ctx.send("Такой страницы нет!")
            return

        def top_embed(numberpage):
            nonlocal ctx
            nonlocal cc
            nonlocal l
            nonlocal met

            num1 = 0
            num2 = 0
            page = numberpage
            text = ''

            if numberpage != 1:
                numberpage *= 5
                numberpage -= 5

                if numberpage > 4:
                    numberpage += 1

            if len(top) <= 5:
                if topname == 'lvl':
                    emb = discord.Embed(title = 'Топ лидеров по уровню', description = '',color=0x450fa8)
                    for i in top:
                        num1 += 1
                        user_lvl = i[1]['lvl']
                        user_name = ctx.guild.get_member(int(i[0]))
                        if met == 'tel':
                            text = text + f'{num1}. {user_name}: {user_lvl} lvl\n'
                        if met == 'pc':
                            emb.add_field(name = '```        Место        ```', value = f'```{num1}```')
                            emb.add_field(name = '```             Имя             ```', value = f'```{user_name}```')
                            emb.add_field(name = '```    Уровень    ```', value = f'```{user_lvl}```')

                elif topname == 'money':
                    emb = discord.Embed(title = f'Топ лидеров по наличным {cc}', description = '',color=0x450fa8)
                    for i in top:
                        num1 += 1
                        user_m = i[1]['money']
                        user_name = ctx.guild.get_member(int(i[0]))
                        if met == 'tel':
                            text = text + f'{num1}. {user_name}: {user_m}{cc}\n'
                        if met == 'pc':
                            emb.add_field(name = '```        Место        ```', value = f'```{num1}```')
                            emb.add_field(name = '```             Имя             ```', value = f'```{user_name}```')
                            emb.add_field(name = '```     Монеты     ```', value = f'```{user_m}```')

                elif topname == 'voice':
                    emb = discord.Embed(title = 'Топ лидеров по активности в войсе', description = '',color=0x450fa8)
                    for i in top:
                        num1 += 1
                        user_v = funs.time_end(i[1]['voice_time'])
                        user_name = ctx.guild.get_member(int(i[0]))
                        if met == 'tel':
                            text = text + f'{num1}. {user_name}: {user_v}\n'
                        if met == 'pc':
                            emb.add_field(name = '```        Место        ```', value = f'```{num1}```')
                            emb.add_field(name = '```             Имя             ```', value = f'```{user_name}```')
                            emb.add_field(name = '```     Активность     ```', value = f'```{user_v}```')

            elif len(top) > 5:
                if topname == 'lvl':
                    emb = discord.Embed(title = 'Топ лидеров по уровню', description = '',color=0x450fa8)
                    for i in top:
                        num1 += 1
                        if num1 >= numberpage and num2 < 5:
                            num2 += 1
                            user_lvl = i[1]['lvl']
                            user_name = ctx.guild.get_member(int(i[0]))
                            if met == 'tel':
                                text = text + f'{num1}. {user_name}: {user_lvl} lvl\n'
                            if met == 'pc':
                                emb.add_field(name = '```       Место       ```', value = f'```{num1}```')
                                emb.add_field(name = '```         Имя         ```', value = f'```{user_name}```')
                                emb.add_field(name = '```    Уровень    ```', value = f'```{user_lvl}```')

                elif topname == 'money':
                    emb = discord.Embed(title = 'Топ лидеров по наличным', description = '',color=0x450fa8)
                    for i in top:
                        num1 += 1
                        if num1 >= numberpage and num2 < 5:
                            num2 += 1
                            user_m = i[1]['money']
                            user_name = ctx.guild.get_member(int(i[0]))
                            if met == 'tel':
                                text = text + f'{num1}. {user_name}: {user_m}{cc}\n'
                            if met == 'pc':
                                emb.add_field(name = '```        Место        ```', value = f'```{num1}```')
                                emb.add_field(name = '```             Имя             ```', value = f'```{user_name}```')
                                emb.add_field(name = '```     Монеты     ```', value = f'```{user_m}```')

                elif topname == 'voice':
                    emb = discord.Embed(title = f'Топ лидеров по активости в войсе', description = '',color=0x450fa8)
                    for i in top:
                        num1 += 1
                        if num1 >= numberpage and num2 < 5:
                            num2 += 1
                            user_v = funs.time_end(i[1]['voice_time'])
                            user_name = ctx.guild.get_member(int(i[0]))
                            if met == 'tel':
                                text = text + f'{num1}. {user_name}: {user_v}\n'
                            if met == 'pc':
                                emb.add_field(name = '```        Место        ```', value = f'```{num1}```')
                                emb.add_field(name = '```             Имя             ```', value = f'```{user_name}```')
                                emb.add_field(name = '```     Активность     ```', value = f'```{user_v}```')

            if met == 'tel':
                emb.add_field(name = '_____', value = text)
            emb.set_footer(text=f"Страница {page}/{l}")
            emb.set_thumbnail(url = "https://img.icons8.com/nolan/2x/prize.png")
            return emb


        msg = await ctx.send(embed = top_embed(numberpage))

        def check( reaction, user):
            nonlocal msg
            return user == ctx.author and str(reaction.emoji) in solutions and str(reaction.message) == str(msg)

        async def rr():
            nonlocal reaction
            nonlocal numberpage
            nonlocal l
            nonlocal met
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

            elif str(reaction.emoji) == '📱':
                await msg.remove_reaction('📱', member)
                if met == 'pc':
                    met = 'tel'
                else:
                    met = 'pc'
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

        for x in solutions:
            await msg.add_reaction(x)
        await reackt()

    @commands.command(usage = '-', description = 'Создание продукта в магазин.', help = 'Магазин')
    async def add_product(self,ctx):

        if funs.roles_check(ctx.author, ctx.guild.id) == False:
            await ctx.send("У вас недостаточно прав для использования этой команды!")
            return

        server = servers.find_one({"server": ctx.guild.id})

        if server['premium'] == True:
            premit = 100
        else:
            premit = 50

        if len(server['economy']['gl_shop']) > premit:
            await ctx.send(f'Превышен лимит предметов которые можно добавить в магазин ({premit})')
            return

        product = {}

        def embed(items = 'Не указано', name = 'Не указано', price = 'Не указано', description = 'Не указано', access_role = 'Не указано', access_balance = 'Не указано'):
            nonlocal server

            emb = discord.Embed(description = "**Создание товара**", color=server['embed_color'])

            if items != 'Не указано' and items != "Укажите продаваемые предметы, Пример: 1 23 1":
                emb.add_field(name = "Покупаемые(й) предмет(ы)", value = ', '.join(str(x) for x in items))
            else:
                emb.add_field(name = "Покупаемые(й) предмет(ы)", value = items)

            emb.add_field(name = "Название продукта", value = name)
            emb.add_field(name = "Цена продукта", value = price)
            emb.add_field(name = "Описание продукта", value = description)
            emb.add_field(name = "Требуемая роль для покупки", value = access_role)
            emb.add_field(name = "Требуемый баланс для покупки", value = access_balance)
            emb.set_footer(text = 'Отправляйте сообщения в чат без использованеи команд, на одно указание у вас 60 сек.')

            return emb

        message = await ctx.send(embed = embed())

        try:
            await message.edit(embed = embed( "Укажите продаваемые предметы, Пример: 1 23 1" ))
            ms2 = await ctx.send(embed = discord.Embed(title = "Предметы", description = f"Вам требуется создать предмет с помощью команды {ctx.prefix}create_item\nПосле вы сможете продать предметы.\nЧто бы увеличить количетсво продаваемого предмета, укажите его id повторно.\nПример: 1 1 3 (покупать получет 2 предмета с id 1 и 1 предмет с id 3)", color=server['embed_color']))
            msg = await self.bot.wait_for('message', timeout=60.0, check=lambda message: message.author == ctx.author and message.channel.id == ctx.channel.id)
        except asyncio.TimeoutError:
            await ctx.send("Время вышло.")
            return
        else:
            try:
                await msg.delete()
                await ms2.delete()
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


            product.update({ 'items': act })

        try:
            await message.edit(embed = embed(product['items'], f'Укажите название продукта: (не более 50 символов)'))
            msg = await self.bot.wait_for('message', timeout=60.0, check=lambda message: message.author == ctx.author and message.channel.id == ctx.channel.id)
        except asyncio.TimeoutError:
            await ctx.send("Время вышло.")
            return
        else:
            try:
                await msg.delete()
            except Exception:
                pass
            if len(message.content) > 50:
                await ctx.send("Название больше 50-ти символов")
                return
            product.update({ 'name': msg.content})

        try:
            await message.edit(embed = embed(product['items'], product['name'], f"Укажите стоимость `{product['name']}`"))
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

            product.update({ 'price': act})

        try:
            await message.edit(embed = embed(product['items'], product['name'], f"{server['economy']['currency']}{product['price']}", f'Укажите описание продукта или `none`: (макс 150 символов)'))
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
                product.update({ 'description': None})
            elif len(description) > 0 and len(description) < 151:
                product.update({ 'description': msg.content})
            else:
                await ctx.send("Требовалось указать описание (макс 50 символов) или `none`, повторите настройку ещё раз!")
                return

        try:
            await message.edit(embed = embed(product['items'], product['name'], f"{server['economy']['currency']}{product['price']}", product['description'], f"Укажите [id](https://support.discord.com/hc/ru/articles/206346498-%D0%93%D0%B4%D0%B5-%D0%BC%D0%BD%D0%B5-%D0%BD%D0%B0%D0%B9%D1%82%D0%B8-ID-%D0%BF%D0%BE%D0%BB%D1%8C%D0%B7%D0%BE%D0%B2%D0%B0%D1%82%D0%B5%D0%BB%D1%8F-%D1%81%D0%B5%D1%80%D0%B2%D0%B5%D1%80%D0%B0-%D1%81%D0%BE%D0%BE%D0%B1%D1%89%D0%B5%D0%BD%D0%B8%D1%8F-) роли требуемой для покупки или `none`"))
            msg = await self.bot.wait_for('message', timeout=60.0, check=lambda message: message.author == ctx.author and message.channel.id == ctx.channel.id)
        except asyncio.TimeoutError:
            await ctx.send("Время вышло.")
            return
        else:
            try:
                await msg.delete()
            except Exception:
                pass

            if msg.content == 'none':
                product.update({ 'access_role': None})

            else:
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

                product.update({ 'access_role': act})

        try:
            await message.edit(embed = embed(product['items'], product['name'], f"{server['economy']['currency']}{product['price']}", product['description'], product['access_role'], "Укажите требуемый баланс для покупки или `none`"))
            msg = await self.bot.wait_for('message', timeout=60.0, check=lambda message: message.author == ctx.author and message.channel.id == ctx.channel.id)
        except asyncio.TimeoutError:
            await ctx.send("Время вышло.")
            return
        else:
            try:
                await msg.delete()
            except Exception:
                pass

            if msg.content == 'none':
                product.update({ 'access_balance': None})
            else:
                try:
                    act = int(msg.content)
                except Exception:
                    await ctx.send("Требовалось указать __число__!")
                    return

                product.update({ 'access_balance': act})

        try:
            l = server['economy']['gl_shop']
            list = []
            for i in l.keys():
                list.append(int(i))
            l = max(list)+1
        except Exception:
            l = 1

        await message.edit(embed = embed(product['items'], product['name'], f"{server['economy']['currency']}{product['price']}", product['description'], product['access_role'], product['access_balance']))

        await ctx.send(f"Предмет с id {l} добавлен в магазин!")

        server = servers.find_one({"server": ctx.guild.id})
        il = server['economy']
        il['gl_shop'].update({f'{l}': product})
        servers.update_one({'server':ctx.guild.id},{"$set":{'economy': il}})

    @commands.command(usage = '(id)', description = 'Удаление продукта.', help = 'Магазин')
    async def remove_product(self,ctx, id:int):
        if funs.roles_check(ctx.author, ctx.guild.id) == False:
            await ctx.send("У вас недостаточно прав для использования этой команды!")
            return

        server = servers.find_one({"server": ctx.guild.id})
        il = server['economy']

        try:
            del il['gl_shop'][str(id)]
            servers.update_one({'server':ctx.guild.id},{"$set":{'economy': il}})
            await ctx.send("Продукт с таким id был удалён")
        except KeyError:
            await ctx.send("Продукт с таким id не был найден, проверьте правильность указания id")

    @commands.command(usage = '(id) (key) (args)', description = 'Изменение продукта.', help = 'Магазин')
    async def edit_product(self,ctx, id:int, key, *args):
        if funs.roles_check(ctx.author, ctx.guild.id) == False:
            await ctx.send("У вас недостаточно прав для использования этой команды!")
            return

        server = servers.find_one({"server": ctx.guild.id})
        il = server['economy']
        try:
            il['gl_shop'][str(id)]
        except KeyError:
            await ctx.send("Продукт с таким id не был найден, проверьте правильность указания id")
            return

        if key not in ['items', 'name', 'price', 'description', 'access_role', 'access_balance']:
            await ctx.send("У продукта нету такого параметра, укажите 1 из этого списка: items, name, price, description, access_role, access_balance")
            return


        if key == 'items':

            al = []
            for i in args:
                al.append(i)

            items = []
            for id in al:
                try:
                    server['items'][str(id)]
                    items.append(id)
                except KeyError:
                    pass

            if len(items) != 0:
                il['gl_shop'][str(id)].update({f'{key}': items})
                servers.update_one({'server':ctx.guild.id},{"$set":{'economy': il}})

        elif key == 'name':
            if len(str(args)) > 50:
                await ctx.send("Название больше 150-ти символов!")
                return

            il['gl_shop'][str(id)].update({f'{key}': len(str(args))})
            servers.update_one({'server':ctx.guild.id},{"$set":{'economy': il}})

        elif key == 'price':

            al = []
            for i in args:
                al.append(i)

            try:
                pr = int(al[0])
            except Exception:
                await ctx.send("Требовалось указать цену, число!")
                return

            if pr < 0:
                await ctx.send("Цена не может быть меньше 0!")
                return

            il['gl_shop'][str(id)].update({f'{key}': pr})
            servers.update_one({'server':ctx.guild.id},{"$set":{'economy': il}})


        elif key == 'description':
            if len(str(args)) > 150:
                await ctx.send("Описание не может быть больше 150-ти символов!")
                return

            il['gl_shop'][str(id)].update({f'{key}': len(str(args))})
            servers.update_one({'server':ctx.guild.id},{"$set":{'economy': il}})

        elif key == 'access_role':
            al = []
            for i in args:
                al.append(i)

            try:
                role = ctx.guild.get_role(int(al[0]))
            except Exception:
                await ctx.send("Требовалось указать id существующей роли!")
                return

            il['gl_shop'][str(id)].update({f'{key}': role.id})
            servers.update_one({'server':ctx.guild.id},{"$set":{'economy': il}})

        elif key == 'access_balance':

            al = []
            for i in args:
                al.append(i)

            try:
                pr = int(al[0])
            except Exception:
                await ctx.send("Требовалось указать баланс доступа, число!")
                return

            if pr < 0:
                await ctx.send("Баланс не может быть меньше 0!")
                return

            il['gl_shop'][str(id)].update({f'{key}': pr})
            servers.update_one({'server':ctx.guild.id},{"$set":{'economy': il}})

        await ctx.send("Продукт изменён!")


    @commands.command(usage = '[page]', description = 'Магазин.', help = 'Магазин')
    async def shop(self,ctx, numberpage:int = 1):

        server = servers.find_one({"server": ctx.guild.id})
        cc = server['economy']['currency']
        solutions = ['◀', '▶', '❌']
        member = ctx.author
        reaction = 'a'

        if server['economy']['gl_shop'] == {}:
            await ctx.send("Тут пусто!")
            return

        top = list(sorted(server['economy']['gl_shop'].items(),key=lambda x: x[1]['price'],reverse=True))

        if len(top) % 10 != 0:
            l = int(len(top) / 10 + 1)
        else:
            l = int(len(top) / 10)

        if numberpage > l or numberpage < 1:
            await ctx.send("Такой страницы нет!")
            return

        def embed(numberpage):
            nonlocal cc
            nonlocal l
            nonlocal ctx
            nonlocal server

            num1 = 0
            num2 = 0
            page = numberpage
            text = ''

            if numberpage != 1:
                numberpage *= 10
                numberpage -= 10

                if numberpage > 9:
                    numberpage += 1

            if len(top) <= 10:
                emb = discord.Embed(title = 'Магазин предметов', description = f'Для покупки пропишите `{ctx.prefix}buy (id)`\nДля информации о продукте пропишите `{ctx.prefix}pr_info (id)`\nid указан перед названием продукта.',color=server['embed_color'])
                for i in top:
                    num1 += 1
                    if i[1]['description'] == None:
                        text = f"{cc}{i[1]['price']}"
                    else:
                        text = f"{cc}{i[1]['price']}\n{i[1]['description']}"
                    emb.add_field(name = f"ID {i[0]} | {i[1]['name']}", value = text, inline = True)


            elif len(top) > 10:
                emb = discord.Embed(title = 'Магазин предметов', description = f'Для покупки пропишите `{ctx.prefix}buy (id)`\nДля информации о продукте пропишите `{ctx.prefix}pr_info (id)`\nid указан перед названием продукта.',color=server['embed_color'])
                for i in top:
                    num1 += 1
                    if num1 >= numberpage and num2 < 10:
                        num2 += 1
                        if i[1]['description'] == None:
                            text = f"{cc}{i[1]['price']}"
                        else:
                            text = f"{cc}{i[1]['price']}\n{i[1]['description']}"
                        emb.add_field(name = f"ID {i[0]} | {i[1]['name']}", value = text, inline = True)

            emb.set_footer(text=f"Страница {page}/{l}")

            return emb

        msg = await ctx.send(embed = embed(numberpage))

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

                await msg.edit(embed = embed(numberpage))


            elif str(reaction.emoji) == '▶':
                await msg.remove_reaction('▶', member)
                numberpage += 1
                if numberpage > l:
                    numberpage = l

                await msg.edit(embed = embed(numberpage))

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

        for x in solutions:
            await msg.add_reaction(x)
        await reackt()

    @commands.command(usage = '(id)', description = 'Покупка продукта.', help = 'Магазин', aliases = ['купить'])
    async def buy(self,ctx, id:int):
        server = servers.find_one({"server": ctx.guild.id})
        list_keys = list(server['economy']['gl_shop'].keys())
        if str(id) not in list_keys:
            await ctx.send("Продукта с таким id нет в магазине")
            return

        product = server['economy']['gl_shop'][str(id)]
        items = []
        for i in product['items']:
            items.append(i)
        user = funs.user_check(ctx.author, ctx.guild)

        if user['money'] < product['price']:
            await ctx.send(f"У вас не достаточно {server['economy']['currency']}монет для покупки данного продукта!")
            return

        if product['access_role'] != None:
            role = ctx.guild.get_role(product['access_role'])
            if role not in ctx.author.roles:
                await ctx.send(f"У вас нет роли {role.name} для покупки данного продукта!")
                return

        if product['access_balance'] != None:
            if product['access_balance'] > user['money']:
                await ctx.send(f"Этот продукт можно купить имея баланс >= {server['economy']['currency']}{product['access_balance']}")
                return

        user['money'] = user['money'] - product['price']
        if funs.user_update(ctx.author.id, ctx.guild, 'money', user['money']) == True:
            for i in product['items']:
                user['inv'].append(funs.creat_item(ctx.guild.id, i))

            if funs.user_update(ctx.author.id, ctx.guild, 'inv', user['inv']) == True:
                await ctx.send(f"Продукт был куплен!")

    @commands.command(usage = '(id)', description = 'Просмотр информации о продукте.', help = 'Магазин')
    async def pr_info(self,ctx, id:int):
        server = servers.find_one({"server": ctx.guild.id})
        list_keys = list(server['economy']['gl_shop'].keys())
        if str(id) not in list_keys:
            await ctx.send("Продукта с таким id нет в магазине")
            return

        product = server['economy']['gl_shop'][str(id)]
        user = funs.user_check(ctx.author, ctx.guild)

        if len(product['items']) == 1:

            item = server['items'][str(product['items'][0])]

            ttype = item['type']
            ttype = ttype.replace('eat', f'🍖 | Еда')
            ttype = ttype.replace('point', f'<:mana:780352235246452756> | Зелье')
            ttype = ttype.replace('case', f'<:chest:827218232783405097> | Сундук сокровищ')
            ttype = ttype.replace('armor', f'<:armor:827220888130682880> | Броня')
            ttype = ttype.replace('pet', f'<:pet:780381475207905290> | Питомец')
            ttype = ttype.replace('material', f'<:leather:783036521099034626> | Материал')
            ttype = ttype.replace('recipe', f'<:recipe:827221967886745600> | Рецепт')
            ttype = ttype.replace('role', f'<:icons8pokeball96:779718625459437608> | Роль')

            quality = item['quality']
            if quality == 'n':
                quality = '<:normal_q:781531816993620001>'
            elif quality == 'u':
                quality = '<:unusual_q:781531868780691476>'
            elif quality == 'r':
                quality = '<:rare_q:781531919140651048>'
            elif quality == 'o':
                quality = '<:orate_q:781531996866084874>'
            elif quality == 'l':
                quality = '<:legendary_q:781532085130100737>'

            if item['type']== 'eat':
                act_title = 'Питательность'

            if item['type'] == 'point':
                if item['style'] == 'heal':
                    act_title = 'Восстановление здоровья'
                if item['style'] == 'mana':
                    act_title = 'Восстановление маны'

            if item['type'] == 'case':
                act_title = 'Сундук удачи'

            if item['type'] == 'armor':
                if item['style'] == 'add':
                    act_title = 'Добавление брони'
                if item['style'] == 'set':
                    act_title = 'Установка брони'

            if item['type'] == 'weapon':
                act_title = 'Урон'

            if item['type'] == 'pet':
                style = item['style']
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

            if item['type'] == 'recipe':
                act_title = 'Рецепт'
                act  = f"Материалы: {product['items']}\nСоздаёт: {server['items'][str(product['create']['name'])]}"

            if item['type'] == 'role':
                if item['style'] == 'add':
                    act_title = 'Добавление роли'
                if item['style'] == 'remove':
                    act_title = 'Удаление роли'

            emb = discord.Embed(title = f"Продукт | {product['name']}", description = f"Тип предмета: {ttype}\nНазвание: {item['name']}\nКачество: {quality}\n{act_title}: {item['act']}\nЦена: {product['price']}\nРоль для покупки: <@&{product['access_role']}>\nТребуемый баланс: {product['access_balance']}".replace('<@&None>', '-').replace('None', '0'), color=server['embed_color'])
            if item['image'] != 'none':
                emb.set_thumbnail(url = item['image'])
            if item['description'] != None:
                emb.add_field(name ='Описание', value = item['description'], inline = False)

            await ctx.send(embed = emb)


        if len(product['items']) != 1:
            embeds = {}

            em = discord.Embed(title = f"Продукт | {product['name']}", description = f"Продукт содержит в себе объекты с id: {', '.join(str(i) for i in product['items'])}\nЦена: {product['price']}\nРоль для покупки: <@&{product['access_role']}>\nТребуемый баланс: {server['economy']['currency']}{product['access_balance']}".replace('<@&None>', '-').replace('None', '0'), color=server['embed_color'])

            embeds.update({ '1' : em})

            for i in product['items']:
                print(i)
                item = server['items'][str(i)]

                type = item['type']
                ttype = item['type']
                ttype = ttype.replace('eat', f'🍖 | Еда')
                ttype = ttype.replace('point', f'<:mana:780352235246452756> | Зелье')
                ttype = ttype.replace('case', f'<:chest:827218232783405097> | Сундук сокровищ')
                ttype = ttype.replace('armor', f'<:armor:827220888130682880> | Броня')
                ttype = ttype.replace('pet', f'<:pet:780381475207905290> | Питомец')
                ttype = ttype.replace('material', f'<:leather:783036521099034626> | Материал')
                ttype = ttype.replace('recipe', f'<:recipe:827221967886745600> | Рецепт')
                ttype = ttype.replace('role', f'<:icons8pokeball96:779718625459437608> | Роль')

                quality = item['quality']
                if quality == 'n':
                    quality = '<:normal_q:781531816993620001>'
                elif quality == 'u':
                    quality = '<:unusual_q:781531868780691476>'
                elif quality == 'r':
                    quality = '<:rare_q:781531919140651048>'
                elif quality == 'o':
                    quality = '<:orate_q:781531996866084874>'
                elif quality == 'l':
                    quality = '<:legendary_q:781532085130100737>'

                if item['type']== 'eat':
                    act_title = 'Питательность'

                if item['type'] == 'point':
                    if item['style'] == 'heal':
                        act_title = 'Восстановление здоровья'
                    if item['style'] == 'mana':
                        act_title = 'Восстановление маны'

                if item['type'] == 'case':
                    act_title = 'Сундук удачи'

                if item['type'] == 'armor':
                    if item['style'] == 'add':
                        act_title = 'Добавление брони'
                    if item['style'] == 'set':
                        act_title = 'Установка брони'

                if item['type'] == 'weapon':
                    act_title = 'Урон'

                if item['type'] == 'pet':
                    style = item['style']
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

                if item['type'] == 'recipe':
                    act_title = 'Рецепт'
                    ct = act
                    act  = f"Материалы: {ct['items']}\nСоздаёт: {server['items'][str(ct['create']['name'])]}"

                if item['type'] == 'role':
                    if item['style'] == 'add':
                        act_title = 'Добавление роли'
                    if item['style'] == 'remove':
                        act_title = 'Удаление роли'

                emb = discord.Embed(title = f"Продукт | {product['name']}", description = f"Тип предмета: {ttype}\nНазвание: {item['name']}\nКачество: {quality}\n{act_title}: {item['act']}", color=server['embed_color'])
                if item['image'] != 'none':
                    emb.set_thumbnail(url = item['image'])
                if item['description'] != None:
                    emb.add_field(name ='Описание', value = item['description'], inline = False)



                l = int(max(embeds.keys()))+1

                embeds.update({ str(l) : emb})

            msg = await ctx.send(embed = embeds['1'].set_footer(text = f'1 \ {l} | Покупка 🛒 | Просмотр ◀ ▶'))
            solutions = ['◀', '🛒', '▶', '❌']
            member = ctx.author
            reaction = 'a'
            numberpage = 1

            def check( reaction, user):
                nonlocal msg
                return user == ctx.author and str(reaction.emoji) in solutions and str(reaction.message) == str(msg)

            async def rr(reaction):
                nonlocal numberpage
                nonlocal ctx
                nonlocal server
                nonlocal product
                nonlocal embeds
                if str(reaction.emoji) == '◀':
                    await msg.remove_reaction('◀', member)
                    numberpage -= 1
                    if numberpage < 1:
                        numberpage = int(max(embeds.keys()))

                    await msg.edit(embed = embeds[str(numberpage)].set_footer(text = f'{numberpage} \ {l} | Покупка 🛒 | Просмотр ◀ ▶') )
                    return True


                if str(reaction.emoji) == '▶':
                    await msg.remove_reaction('▶', member)
                    numberpage += 1
                    if numberpage > int(max(embeds.keys())):
                        numberpage = 1

                    await msg.edit(embed = embeds[str(numberpage)].set_footer(text = f'{numberpage} \ {l} | Покупка 🛒 | Просмотр ◀ ▶') )
                    return True

                elif str(reaction.emoji) == '🛒':
                    await msg.remove_reaction('🛒', member)

                    items = []
                    for i in product['items']:
                        items.append(i)
                    user = funs.user_check(ctx.author, ctx.guild)

                    if user['money'] < product['price']:
                        await ctx.send(f"У вас не достаточно {server['economy']['currency']}монет для покупки данного продукта!")
                        return True

                    if product['access_role'] != None:
                        role = ctx.guild.get_role(product['access_role'])
                        if role not in ctx.author.roles:
                            await ctx.send(f"У вас нет роли {role.name} для покупки данного продукта!")
                            return True

                    if product['access_balance'] != None:
                        if product['access_balance'] > user['money']:
                            await ctx.send(f"Этот продукт можно купить имея баланс >= {server['economy']['currency']}{product['access_balance']}")
                            return True

                    user['money'] = user['money'] - product['price']
                    if funs.user_update(ctx.author.id, ctx.guild, 'money', user['money']) == True:
                        for i in product['items']:
                            user['inv'].append(funs.creat_item(ctx.guild.id, i))

                        if funs.user_update(ctx.author.id, ctx.guild, 'inv', user['inv']) == True:
                            await ctx.send(f"Продукт был куплен!")
                            return True


                if str(reaction.emoji) == '❌':
                    await msg.clear_reactions()
                    return False

            async def reackt():
                nonlocal reaction
                try:
                    reaction, user = await self.bot.wait_for('reaction_add', timeout=30.0, check = check)
                except asyncio.TimeoutError:
                    await msg.clear_reactions()
                else:
                    await rr(reaction), await reackt()

            for x in solutions:
                await msg.add_reaction(x)
            await reackt()


    @commands.command(usage = '-', description = 'Ежедневная награда.', help = 'Взаимодействие', aliases = ['ежедневка'])
    async def daily(self,ctx):
        user = funs.user_check(ctx.author, ctx.guild)
        server = servers.find_one({"server": ctx.guild.id})

        if user['cache']['week_act'][1] == None or user['cache']['week_act'][1]+1 == int(time.strftime("%j")):
            if user['cache']['week_act'][0] == 7:
                user['cache'].update({'week_act': [1, int(time.strftime("%j"))] })
                funs.user_update(ctx.author.id, ctx.guild, 'cache', user['cache'])
            else:
                user['cache'].update({'week_act': [user['cache']['week_act'][0]+1, int(time.strftime("%j"))] })
                funs.user_update(ctx.author.id, ctx.guild, 'cache', user['cache'])

        elif user['cache']['week_act'][1]+1 != int(time.strftime("%j")):
            user['cache'].update({'week_act': [1, int(time.strftime("%j"))] })
            funs.user_update(ctx.author.id, ctx.guild, 'cache', user['cache'])

        if len(server['economy']['daily_reward']) == 0:
            reward = 200
            reward_percent = 1.05
        else:
            reward = server['economy']['daily_reward']['reward']
            reward_percent = server['economy']['daily_reward']['reward_percent']

        url = f"https://ic.wampi.ru/2021/08/07/pizza_day_{user['cache']['week_act'][0]}.gif"

        if user['cache']['week_act'][0] == 1:
            u_r = int(reward)
            text = '<:heart:780373079439572993> Используйте Котика каждый день что бы получить бонус к награде!'
        else:
            u_r = int(reward * reward_percent * user['cache']['week_act'][0])
            text = f"<:icons8pokeball96:779718625459437608> Бонус: х{int(reward_percent * user['cache']['week_act'][0])}"

        emb = discord.Embed(title = f"Ежедневный котик", description = f"<:foot:779718609177411635> Ежедневный котик принёс вам: {u_r}{server['economy']['currency']}\n{text}", color=server['embed_color'])
        emb.set_image(url=url)
        emb.set_thumbnail(url= 'https://i.pinimg.com/originals/94/14/3b/94143bc201d8b4942c252a19c0db605c.gif')
        await ctx.send(embed = emb)

        funs.user_update(ctx.author.id, ctx.guild, 'money', user['money'] + u_r)

    @commands.command(aliases = ['21point','21очко'], usage = '(amout) [@member]', description = 'Игра "Собери 21"', help = 'Игры')
    async def blackjack(self,ctx, amout:int, member: discord.Member = None):
        user = funs.user_check(ctx.author, ctx.guild)
        if member != None:
            user2 = funs.user_check(member, ctx.guild)
            if user2['money'] < amout:
                await ctx.send(f'У соперника нету столько монет!')
                return
        server = servers.find_one({"server": ctx.guild.id})

        if amout < server['economy']['games']['blackjack']['mini'] or amout > server['economy']['games']['blackjack']['max']:
            await ctx.send(f"Укажите сумму в периоде с {server['economy']['games']['blackjack']['mini']} до {server['economy']['games']['blackjack']['max']}")
            return

        if user['money'] < amout:
            await ctx.send(f'У вас нет столько монет!')
            return

        if ctx.author == member:
            member = None
        if member != None:
            solutions = ['✅', '❌']
            reaction = 'a'
            msg = await ctx.send(f'{member.mention} вы приглашены сыграть в `собери 21`, нажмите ✅ для начала!')

            def check( reaction, user):
                nonlocal msg
                return user == member and str(reaction.emoji) in solutions and str(reaction.message) == str(msg)

            async def reackt():
                nonlocal reaction
                try:
                    reaction, user = await self.bot.wait_for('reaction_add', timeout=30.0, check = check)
                except asyncio.TimeoutError:
                    await msg.clear_reactions()
                    return False
                else:
                    if str(reaction.emoji) == '✅':
                        await msg.clear_reactions()
                        return True

                    elif str(reaction.emoji) == '❌':
                        await msg.clear_reactions()
                        return False

            for x in solutions:
                await msg.add_reaction(x)

            if await reackt() == True:
                try:
                    await msg.delete()
                except Exception:
                    pass
                pass
            else:
                try:
                    await msg.delete()
                except Exception:
                    pass
                return


        deck = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]*4
        random.shuffle(deck)

        def deal(deck):
            hand = []
            for i in range(2):
                random.shuffle(deck)
                card = deck.pop()
                if card == 11:card = "J"
                if card == 12:card = "Q"
                if card == 13:card = "K"
                if card == 14:card = "A"
                hand.append(card)
            return hand

        mem1_hand = []
        mem2_hand = []
        mem1_hand = deal(deck)
        mem2_hand = deal(deck)

        def total(hand):
            total = 0
            for card in hand:
                if card == "J" or card == "Q" or card == "K":
                    total += 10
                elif card == "A":
                    if total >= 11:
                        total += 1
                    else:
                        total += 11
                else:
                    total += int(card)
            return total

        def hit(hand):
            card = deck.pop()
            if card == 11:card = "J"
            if card == 12:card = "Q"
            if card == 13:card = "K"
            if card == 14:card = "A"
            hand.append(card)
            return hand

        def score(dealer_hand, player_hand):
            if total(player_hand) == 21:
                return 'player 1 win'
            elif total(dealer_hand) == 21:
                return 'player 2 win'
            elif total(player_hand) > 21:
                return 'player 2 win'
            elif total(dealer_hand) > 21:
                return 'player 1 win'
            else:
                return False

        def win_check(dealer_hand, player_hand):
            if total(player_hand) == 21:
                return 'player 1 win'
            elif total(dealer_hand) == 21:
                return 'player 2 win'
            elif total(player_hand) > 21:
                return 'player 2 win'
            elif total(dealer_hand) > 21:
                return 'player 1 win'
            elif total(player_hand) < total(dealer_hand):
                return 'player 2 win'
            elif total(player_hand) > total(dealer_hand):
                return 'player 1 win'
            elif total(player_hand) == total(dealer_hand):
                return 'friendship'
            else:
                return False

        def emb(feet = None):
            nonlocal member, ctx
            nonlocal mem1_hand, mem2_hand
            nonlocal server
            emb = discord.Embed(title = "Собери 21", description = 'Цель собрать 21 очко и обыграть соперника, введите `hit` если хотите взять ещё карту, `stand` если готовы остановится.', color=server['embed_color'])
            if member == None:
                pl2 = 'Бот-Дилер'
            else:
                pl2 = member.name
            h2 = ", ".join(str(i) for i in mem2_hand)
            h1 = ", ".join(str(i) for i in mem1_hand)
            emb.add_field(name = f'Игрок 2: {pl2}', value = f'Карты: {h2}\nОчки: {total(mem2_hand)}')
            emb.add_field(name = f'Игрок 1: {ctx.author.name}', value = f'Карты: {h1}\nОчки: {total(mem1_hand)}')
            if win_check(mem2_hand, mem1_hand) != False:
                if feet == None:
                    if win_check(mem2_hand, mem1_hand) == 'player 1 win':
                        win = ctx.author.mention
                    if win_check(mem2_hand, mem1_hand) == 'player 2 win':
                        win = pl2
                    if win_check(mem2_hand, mem1_hand) == 'friendship':
                        win = 'Дружба'
                    emb.add_field(name = f'Победитель', value = f'{win}')
            if feet != None:
                emb.add_field(name = f'Ход игрока', value = f'{feet}')
            return emb

        message = await ctx.send(embed = emb())

        async def game_bot():
            nonlocal member, ctx
            nonlocal mem1_hand, mem2_hand
            try:
                await message.edit(embed = emb('Игрок 1'))
                msg = await self.bot.wait_for('message', timeout=20.0, check=lambda message: message.author == ctx.author and message.channel.id == ctx.channel.id)
            except asyncio.TimeoutError:
                await ctx.send("Время вышло.")
                pass
            else:

                try:
                    await msg.delete()
                except Exception:
                    pass

                if msg.content == 'hit':
                    mem1_hand = hit(mem1_hand)
                    if score(mem2_hand, mem1_hand) == 'player 1 win' or score(mem2_hand, mem1_hand) == 'player 2 win':
                        return

            await message.edit(embed = emb('Игрок 2'))
            while total(mem2_hand) < total(mem1_hand):
                mem2_hand = hit(mem2_hand)
                if score(mem2_hand, mem1_hand) == 'player 1 win' or score(mem2_hand, mem1_hand) == 'player 2 win':
                    return

        async def game_2_players():
            nonlocal member, ctx
            nonlocal mem1_hand, mem2_hand
            for i in range(2):
                if score(mem2_hand, mem1_hand) == False:
                    try:
                        await message.edit(embed = emb('Игрок 1'))
                        msg = await self.bot.wait_for('message', timeout=20.0, check=lambda message: message.author == ctx.author and message.channel.id == ctx.channel.id)
                    except asyncio.TimeoutError:
                        await ctx.send("Время вышло для игрока 1")
                        pass
                    else:
                        try:
                            await msg.delete()
                        except Exception:
                            pass

                        if msg.content == 'hit':
                            mem1_hand = hit(mem1_hand)
                else:
                    return

                if score(mem2_hand, mem1_hand) == False:
                    try:
                        await message.edit(embed = emb('Игрок 2'))
                        msg = await self.bot.wait_for('message', timeout=20.0, check=lambda message: message.author == member and message.channel.id == ctx.channel.id)
                    except asyncio.TimeoutError:
                        await ctx.send("Время вышло для игрока 2")
                        pass
                    else:
                        try:
                            await msg.delete()
                        except Exception:
                            pass

                        if msg.content == 'hit':
                            mem2_hand = hit(mem2_hand)
                else:
                    return

        if win_check(mem2_hand, mem1_hand) != 'player 1 win' or win_check(mem2_hand, mem1_hand) != 'player 2 win':
            if member == None:
                funs.user_update(ctx.author.id, ctx.guild, 'money', user['money'] - amout )
                await game_bot()
            else:
                funs.user_update(ctx.author.id, ctx.guild, 'money', user['money'] - amout )
                funs.user_update(member.id, ctx.guild, 'money', user2['money'] - amout)
                await game_2_players()

        await message.edit(embed = emb())

        if win_check(mem2_hand, mem1_hand) == 'player 1 win':
            if member == None:
                funs.user_update(ctx.author.id, ctx.guild, 'money', user['money'] + int(amout * server['economy']['games']['blackjack']['percent']))
                await ctx.send(f"Награда {int(amout * server['economy']['games']['blackjack']['percent'])}{server['economy']['currency']}")
            if member != None:
                funs.user_update(ctx.author.id, ctx.guild, 'money', user['money'] + int(amout * server['economy']['games']['blackjack']['percent']))
                await ctx.send(f"Игрок 1 выйграл {int(amout * server['economy']['games']['blackjack']['percent'])}")

        if win_check(mem2_hand, mem1_hand) == 'player 2 win':
            if member == None:
                pass
            if member != None:
                funs.user_update(member.id, ctx.guild, 'money', user2['money'] + int(amout * server['economy']['games']['blackjack']['percent']) )
                await ctx.send(f"Игрок 2 выйграл {int(amout * server['economy']['games']['blackjack']['percent'] )}")

        if win_check(mem2_hand, mem1_hand) == 'friendship':
            pass

    @commands.command(usage = '(amout) [repets]', description = 'Игра в слоты.', help = 'Игры', aliases = ['слоты'])
    async def slots(self,ctx, amout:int, repet:int = 1):
        user = funs.user_check(ctx.author, ctx.guild)
        server = servers.find_one({"server": ctx.guild.id})
        if user['money'] < amout * repet:
            await ctx.send(f'У вас нет столько монет!')
            return

        if amout < server['economy']['games']['blackjack']['mini'] or amout > server['economy']['games']['blackjack']['max']:
            await ctx.send(f"Укажите сумму в периоде с {server['economy']['games']['blackjack']['mini']} до {server['economy']['games']['blackjack']['max']}")
            return

        if repet < 0:
            await ctx.send('Укажите число повторных игр больше 0!')

        def r(list, n1, n2, n3):
            if list[n1] == list[n2] and list[n2] == list[n3]:
                return True
            else:
                return False

        def p_w(list, n1, n2, n3):
            if list[n1] == list[n2] or list[n1] == list[n2] or list[n2] == list[n3]:
                if list[n1] == list[n2] and list[n2] == list[n3]:
                    return False
                else:
                    return True

        slots = ['🍡','🍬','🍧','🍭','🍱','🍫','🍩']*5
        random.shuffle(slots)

        if repet == 1:
            user_slots = []
            for i in range(9):
                user_slots += slots.pop()

            s = user_slots
            win = False
            p_win = False
            if r(user_slots, 3,4,5) == True:
                win = True
            elif r(user_slots, 0,3,6) == True:
                win = True
            elif r(user_slots, 1,4,7) == True:
                win = True
            elif r(user_slots, 2,5,8) == True:
                win = True
            elif r(user_slots, 0,1,2) == True:
                win = True
            elif r(user_slots, 6,7,8) == True:
                win = True
            elif r(user_slots, 0,4,8) == True:
                win = True
            elif r(user_slots, 2,4,6) == True:
                win = True

            elif p_w(user_slots, 0,1,2) == True:
                p_win = True
            elif p_w(user_slots, 3,4,5) == True:
                p_win = True
            elif p_w(user_slots, 6,7,8) == True:
                p_win = True

            text = f'[  |  SLOTS  |  ]\n {s[0]} | {s[1]} | {s[2]} \n\n {s[3]} | {s[4]} | {s[5]} \n\n {s[6]} | {s[7]} | {s[8]} \n| -------------- |\n\n'

            if win == True:
                text += f"Вы сорвали куш! Ваша награда составляет {int(amout * server['economy']['games']['slots']['percent'])}{server['economy']['currency']}"
                funs.user_update(ctx.author.id, ctx.guild, 'money', user['money'] + int(amout * server['economy']['games']['slots']['percent']))
            elif p_win == True:
                text += f'Вы выбили 2 из 3, монеты остаются у вас!'
            else:
                text += 'Вы проиграли!'
                funs.user_update(ctx.author.id, ctx.guild, 'money', user['money'] - amout)

            await ctx.send(text)

        if repet > 1:
            wins = 0
            p_wins = 0
            u_money = amout * repet
            for i in range(repet):
                slots = ['🍡','🍬','🍧','🍭','🍱','🍫','🍩']*5
                random.shuffle(slots)
                user_slots = []
                for i in range(9):
                    user_slots += slots.pop()

                if r(user_slots, 3,4,5) == True:
                    wins += 1
                    u_money += int(amout * server['economy']['games']['slots']['percent'])
                elif r(user_slots, 0,3,6) == True:
                    wins += 1
                    u_money += int(amout * server['economy']['games']['slots']['percent'])
                elif r(user_slots, 1,4,7) == True:
                    wins += 1
                    u_money += int(amout * server['economy']['games']['slots']['percent'])
                elif r(user_slots, 2,5,8) == True:
                    wins += 1
                    u_money += int(amout * server['economy']['games']['slots']['percent'])
                elif r(user_slots, 0,1,2) == True:
                    wins += 1
                    u_money += int(amout * server['economy']['games']['slots']['percent'])
                elif r(user_slots, 6,7,8) == True:
                    wins += 1
                    u_money += int(amout * server['economy']['games']['slots']['percent'])
                elif r(user_slots, 0,4,8) == True:
                    wins += 1
                    u_money += int(amout * server['economy']['games']['slots']['percent'])
                elif r(user_slots, 2,4,6) == True:
                    wins += 1
                    u_money += int(amout * server['economy']['games']['slots']['percent'])

                elif p_w(user_slots, 0,1,2) == True:
                    p_wins += 1
                elif p_w(user_slots, 3,4,5) == True:
                    p_wins += 1
                elif p_w(user_slots, 6,7,8) == True:
                    p_wins += 1
                else:
                    u_money -= amout

            emd = discord.Embed(title = f"Слоты", description = f"Побед: {wins}\nИгры без потерь: {p_wins}\nПроигрыши: {repet - wins - p_wins}\nВозрат монет: {u_money}", color=server['embed_color'])
            await ctx.send(embed = emd)
            funs.user_update(ctx.author.id, ctx.guild, 'money', user['money'] - int(amout * server['economy']['games']['slots']['percent']) * repet)
            funs.user_update(ctx.author.id, ctx.guild, 'money', user['money'] + u_money)

    @commands.command(usage = '(number) (money) (@member)', description = 'Игра в шанс.', help = 'Игры', aliases = ['шанс'])
    async def chance(self, ctx, number:int = None, money:int = None, member:discord.Member = None ):

        kk = self.bot.get_emoji(778533802342875136)
        user = funs.user_check(ctx.author, ctx.guild)
        mem = funs.user_check(member.id, ctx.guild)
        server = servers.find_one({"server": ctx.guild.id})
        if number == None or money == None or member == None:
            emb = discord.Embed(description = f'Правильный ввод команды: \n`{ctx.prefix}duel (число от 1 до 100) (ставка от 10 до 100к) (@пользователь)`', color=server['embed_color'])
            emb.set_author(icon_url = '{}'.format(ctx.author.avatar_url), name = '{}'.format(ctx.author))
            await ctx.send(embed = emb)
            return

        if number > 100 or number < 1:
            emb = discord.Embed(description = f'Укажите число от 1 до 100', color=server['embed_color'])
            emb.set_author(icon_url = '{}'.format(ctx.author.avatar_url), name = '{}'.format(ctx.author))
            await ctx.send(embed = emb)
            return

        if money < server['economy']['games']['chance']['mini'] or money > server['economy']['games']['chance']['max']:
            emb = discord.Embed(description = f"Укажите колличество монет от {server['economy']['games']['chance']['mini']} до {server['economy']['games']['chance']['max']}", color=server['embed_color'])
            emb.set_author(icon_url = '{}'.format(ctx.author.avatar_url), name = '{}'.format(ctx.author))
            await ctx.send(embed = emb)
            return

        if money > user['money']:
            emb = discord.Embed(description = f'У вас нет столько монеток', color=server['embed_color'])
            emb.set_author(icon_url = '{}'.format(ctx.author.avatar_url), name = '{}'.format(ctx.author))
            await ctx.send(embed = emb)
            return

        if money > mem['money']:
            emb = discord.Embed(description = f'У {member.mention} нет столько монеток', color=server['embed_color'])
            emb.set_author(icon_url = '{}'.format(ctx.author.avatar_url), name = '{}'.format(ctx.author))
            await ctx.send(embed = emb)
            return

        if ctx.author == member:
            emb = discord.Embed(description = f'Игра в шанс с самим собой не возможен', color=server['embed_color'])
            emb.set_author(icon_url = '{}'.format(ctx.author.avatar_url), name = '{}'.format(ctx.author))
            await ctx.send(embed = emb)
            return


        solutions = ['✔', '❌']
        reaction = 'a'
        emb2 = discord.Embed(description = f'<@{member.id}> вы готовы принять шанс от <@{ctx.author.id}>?`', color=server['embed_color'])
        emb2.set_author(icon_url = '{}'.format(ctx.author.avatar_url), name = '{}'.format(ctx.author))

        async def text():
            nonlocal mess
            nonlocal number
            nonlocal user
            nonlocal server
            await mess.clear_reactions()
            emb3 = discord.Embed(description = f'<@{member.id}> введите число от `1 до 100`', color=server['embed_color'])
            emb3.set_author(icon_url = '{}'.format(member.avatar_url), name = '{}'.format(member)).set_footer(text='В чат без использования команд')
            await mess.edit(embed = emb3)
            try:
                msg = await self.bot.wait_for('message', timeout=30.0, check=lambda message: message.author == member)
            except asyncio.TimeoutError:
                emb5 = discord.Embed(description = f'Время вышло', color=server['embed_color'])
                await mess.edit(embed = emb5)
                return
            else:
                try:
                    number2 = int(msg.content)
                except Exception:
                    await ctx.send('Укажите __число__!')
                    return

                if number2 < int(101) and number2 > int(0) or number2 != number2:
                    funs.user_update(ctx.author.id, ctx.guild, 'money', user['money'] -money)
                    funs.user_update(member.id, ctx.guild, 'money', mem['money'] -money)

                    r1 = random.randint(1,100)
                    emb4 = discord.Embed(title = 'Шанс', color=server['embed_color']).add_field(name = f'Организатор:', value = f"Имя: <@{ctx.author.id}>\n Число: {number}"
                    ).set_thumbnail(url ="https://thumbs.gfycat.com/PlasticTestyBushbaby-size_restricted.gif")
                    emb4.add_field(name = f'Котик', value = f"Котик выбрал число: {r1}")
                    emb4.add_field(name = f'Дуэлянт:', value = f"Имя: <@{member.id}>\n Число: {msg.content}")

                    if number > r1:
                        number = number - r1
                    else:
                        number = r1 - number

                    if number2 > r1:
                        number2 = number2 - r1
                    else:
                        number2 = r1 - number2

                    if number2 < number:
                        emb4.add_field(name = f"Победитель: ",value = f'<@{member.id}>\n Выйгрыш: {money} монеток{kk}', inline = False)
                        funs.user_update(member.id, ctx.guild, 'money', mem['money'] + money*2)
                    else:
                        emb4.add_field(name = f"Победитель: ",value = f'<@{ctx.author.id}>\n Выйгрыш: {money} монеток{kk}', inline = False)
                        funs.user_update( ctx.author.id, ctx.guild, 'money', mem['money'] + money*2)

                    await mess.edit(embed = emb4)


                else:
                    await ctx.send('Число должно быть больше 0-ля и меньше 100-та, а так же не совпадать с числом противника!')
                    return


        def check( reaction, user):
            nonlocal mess
            return user == member and str(reaction.emoji) in solutions and str(reaction.message) == str(mess)

        async def rr():
            nonlocal reaction
            if str(reaction.emoji) == '✔':
                await mess.remove_reaction('✔', member)
                await text()
                pass

            elif str(reaction.emoji) == '❌':
                await mess.clear_reactions()
                return

        async def reackt():
            nonlocal reaction
            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=30.0, check = check)
            except asyncio.TimeoutError:
                await mess.clear_reactions()
            else:
                await rr()


        mess = await ctx.send(embed = emb2)

        for x in solutions:
            await mess.add_reaction(x)

        await reackt()




def setup(bot):
    bot.add_cog(economy(bot))
