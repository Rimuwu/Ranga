import nextcord as discord
from nextcord.ext import tasks, commands
import sys
import random
from random import choice
import asyncio
import time
import pymongo
import pprint


sys.path.append("..")
from ai3 import functions as funs
import config

client = funs.mongo_c()
db = client.bot
users = db.users
backs = db.bs
servers = db.servers
clubs = db.db.clubs


class clubs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.command(usage = '[tag/name] [club_name]', description = 'Информация о клубе', aliases = ['клуб_инфо'])
    async def club_info(self, ctx, arg = None, *, name = None):
        global users
        if users.find_one({"userid": ctx.author.id}) == None:
            await ctx.send(f'У данного пользователя не создан аккаунт, пропишите {ctx.prefix}help для создания!')
            return
        lname = ['name','имя', "название", "Name", "n"]
        ltag = ["tag", "тег","Tag", "t"]

        user = users.find_one({"userid": ctx.author.id})
        pprint.pprint(db.db.db.clubs.find_one())


        if name is None or arg == None:
            name = user['guild']
            dom = db.clubs.find_one({"name": name})

        else:
            if arg in lname:
                dom = db.clubs.find_one({"name": name})
            elif arg in ltag:
                dom = db.clubs.find_one({"tag": name})
                name = dom['name']
            else:
                await ctx.send(f"Поиск по {arg} не доступен")
                return


        if dom != None:
            members = dom['members']
            data = dom['created']
            ls = dom['members']
            ad = dom['admins']
            text = len(ls)
            clvl = dom['lvl']
            lvl_enter = dom['lvl_enter']
            index_page = 1

            solutions = ['📜', '👥', '🎴', '👑', '🛒', '❌']

            sola0 = ['📜', '👥', '❌']
            sola5 = ['📜', '👥', '🎴', '❌']
            sola10 = ['📜', '👥', '🎴', '👑', '❌']
            sola15 = ['📜', '👥', '🎴', '👑', '❌']
            sola20 = ['📜', '👥', '🎴', '👑', '🛒', '❌']

            solutions2 = ['📜', '👥', '📢', '👑', '🛒', '❌']

            solb0 = ['📜', '👥', '❌']
            solb5 = ['📜', '👥', '❌']
            solb10 = ['📜', '👥', '👑', '❌']
            solb15 = ['📜', '👥', '👑', '❌']
            solb20 = ['📜', '👥', '👑', '🛒', '❌']

            arrows = ["📑", "🔼", "🔽", '❌']
            shop = ["📑", "1️⃣", '❌']

            member = ctx.author
            reaction = 'a'

            if dom['global_club'] == False:
                st = "Закрытый"
            else:
                st = f"Открытый\nУровень входа: {lvl_enter}"

            if dom['flag'] == None:
                expnc = 5 * dom['lvl'] * dom['lvl'] + 50 * dom['lvl'] + 100

                emb1 = nextcord.Embed(color=0xf03e65).add_field(name = 'Описание:', value = f'{dom["bio"]}', inline = True
                ).add_field(name = 'Уровень клуба:', value = f'LvL: {dom["lvl"]}\nExp: {dom["exp"]} |  {expnc}').add_field(name = 'Владелец:', value = f'<@{dom["owner"]}>'
                ).add_field(name = 'Дата создания:', value = f'{data}').add_field(name = 'Статус клуба:', value = f'{st}'
                ).add_field(name = 'Участников:', value = f'{text}'
                ).add_field(name = 'Тег:', value = f'[{dom["tag"]}]').set_author(name = f'ClubInfo | {dom["name"]}').add_field(name = 'Банк:', value = f'Монетки: {dom["bank"]}')

                emb2 = discord.Embed(color=0xf03e65).set_author( name = f'ClubUsers 1 | {dom["name"]}')
                embu2 = discord.Embed(color=0xf03e65).set_author(name = f'ClubUsers 2 | {dom["name"]}')
                embu3 = discord.Embed(color=0xf03e65).set_author( name = f'ClubUsers 3 | {dom["name"]}')
                embu3 = discord.Embed(color=0xf03e65).set_author( name = f'ClubUsers 4 | {dom["name"]}')

                emb4 = discord.Embed(color=0xf03e65).set_author(name = f'ClubAnnouncements | {dom["name"]}')

                emb5 = discord.Embed(color=0xf03e65).set_author(name = f'ClubTop | {dom["name"]}')

                emb6 = discord.Embed(color=0xf03e65).set_author( name = f'db.clubshop | {dom["name"]}').add_field(name = 'Банк:',
                value = f'Монетки: {dom["bank"]}', inline = False).add_field(name = ':one:', value = f'+5 слотов для пользователей\n`Цена: 2.000 монет\nСлотов: {dom["max_users"]}`')

                emb6er1 = discord.Embed(color=0xf03e65).set_author(name = f'db.clubshop | {dom["name"]}').add_field(name = 'Банк:',
                value = f'Монетки: {dom["bank"]}', inline = False).add_field(name = ':one: - слоты для пользователей', value = f'+5 слотов для пользователей\n`Не хватает монет`')



            if dom['flag'] != None:
                expnc = 5 * dom['lvl'] * dom['lvl'] + 50 * dom['lvl'] + 100

                emb1 = discord.Embed(color=0xf03e65).add_field(name = 'Описание:', value = f'{dom["bio"]}', inline = True
                ).add_field(name = 'Уровень клуба:', value = f'LvL: {dom["lvl"]}\nExp: {dom["exp"]} |  {expnc}').add_field(name = 'Владелец:', value = f'<@{dom["owner"]}>'
                ).add_field(name = 'Дата создания:', value = f'{data}').add_field(name = 'Статус клуба:', value = f'{st}'
                ).add_field(name = 'Участников:', value = f'{text}'
                ).add_field(name = 'Тег:', value = f'[{dom["tag"]}]').add_field(name = 'Банк:', value = f'Монетки: {dom["bank"]}')

                emb2 = discord.Embed(color=0xf03e65).set_author(icon_url = '{}'.format(dom["flag"]), name = f'ClubUsers 1 | {dom["name"]}')
                embu2 = discord.Embed(color=0xf03e65).set_author(icon_url = '{}'.format(dom["flag"]), name = f'ClubUsers 2 | {dom["name"]}')
                embu3 = discord.Embed(color=0xf03e65).set_author(icon_url = '{}'.format(dom["flag"]), name = f'ClubUsers 3 | {dom["name"]}')
                embu3 = discord.Embed(color=0xf03e65).set_author(icon_url = '{}'.format(dom["flag"]), name = f'ClubUsers 4 | {dom["name"]}')

                emb4 = discord.Embed(color=0xf03e65).set_author(icon_url = '{}'.format(dom["flag"]), name = f'ClubAnnouncements | {dom["name"]}')

                emb1.set_thumbnail(url = dom["flag"]).set_author(name = f'ClubInfo | {dom["name"]}', icon_url = '{}'.format(dom["flag"]))
                emb2.set_thumbnail(url = dom["flag"])
                emb3 = discord.Embed(color=0xf03e65).set_image(url = dom["flag"]).set_author(name = f'ClubBanner | {dom["name"]}')
                emb4.set_thumbnail(url = dom["flag"])

                emb5 = discord.Embed(color=0xf03e65).set_author(icon_url = '{}'.format(dom["flag"]), name = f'ClubTop | {dom["name"]}')

                emb6 = discord.Embed(color=0xf03e65).set_author(icon_url = '{}'.format(dom["flag"]), name = f'db.clubshop | {dom["name"]}').add_field(name = 'Банк:',
                value = f'Монетки: {dom["bank"]}', inline = False).add_field(name = ':one: - слоты для пользователей', value = f'+5 слотов для пользователей\n`Цена: 2.000 монет\nСлотов: {dom["max_users"]}`')

                emb6er1 = discord.Embed(color=0xf03e65).set_author(icon_url = '{}'.format(dom["flag"]), name = f'db.clubshop | {dom["name"]}').add_field(name = 'Банк:',
                value = f'Монетки: {dom["bank"]}', inline = False).add_field(name = ':one:', value = f'+5 слотов для пользователей\n`Не хватает монет`')

            c = 0
            ul = len(ls)
            while True:
                for i in ls:
                    if c < 25:

                        if i == dom['owner']:
                            user2 = users.find_one({"userid": int(i)})
                            emb2.add_field(name = f"{user2['username']}", value = f"Роль: Глава")
                            ls.remove(int(i))
                            c = c + 1

                        elif i in ad:
                            user2 = users.find_one({"userid": int(i)})
                            emb2.add_field(name = f"{user2['username']}", value = f"Роль: Админ")
                            ls.remove(int(i))
                            c = c + 1

                        else:
                            user2 = users.find_one({"userid": int(i)})
                            emb2.add_field(name = f"{user2['username']}", value = f"Роль: Участник")
                            ls.remove(int(i))
                            c = c + 1

                    elif c < 50 and c > 25:

                        if i == dom['owner']:
                            user2 = users.find_one({"userid": int(i)})
                            embu2.add_field(name = f"{user2['username']}", value = f"Роль: Глава")
                            ls.remove(int(i))
                            c = c + 1

                        elif i in ad:
                            user2 = users.find_one({"userid": int(i)})
                            embu2.add_field(name = f"{user2['username']}", value = f"Роль: Админ")
                            ls.remove(int(i))
                            c = c + 1

                        else:
                            user2 = users.find_one({"userid": int(i)})
                            embu2.add_field(name = f"{user2['username']}", value = f"Роль: Участник")
                            ls.remove(int(i))
                            c = c + 1

                    elif c < 75 and c > 50:

                        if i == dom['owner']:
                            user2 = users.find_one({"userid": int(i)})
                            embu3.add_field(name = f"{user2['username']}", value = f"Роль: Глава")
                            ls.remove(int(i))
                            c = c + 1

                        elif i in ad:
                            user2 = users.find_one({"userid": int(i)})
                            embu3.add_field(name = f"{user2['username']}", value = f"Роль: Админ")
                            ls.remove(int(i))
                            c = c + 1

                        else:
                            user2 = users.find_one({"userid": int(i)})
                            embu3.add_field(name = f"{user2['username']}", value = f"Роль: Участник")
                            ls.remove(int(i))
                            c = c + 1

                    elif c < 100 and c > 75:

                        if i == dom['owner']:
                            user2 = users.find_one({"userid": int(i)})
                            embu4.add_field(name = f"{user2['username']}", value = f"Роль: Глава")
                            ls.remove(int(i))
                            c = c + 1

                        elif i in ad:
                            user2 = users.find_one({"userid": int(i)})
                            embu4.add_field(name = f"{user2['username']}", value = f"Роль: Админ")
                            ls.remove(int(i))
                            c = c + 1

                        else:
                            user2 = users.find_one({"userid": int(i)})
                            embu4.add_field(name = f"{user2['username']}", value = f"Роль: Участник")
                            ls.remove(int(i))
                            c = c + 1

                if ls == []:
                    break

            m = 0
            l = 0
            r = 0
            tex1 = "-"
            tex2 = "-"
            tex3 = "-"
            d = db.clubs.find_one({"name": name})
            tp = d['members']
            while True:
                for i in tp:
                    u = users.find_one({"userid": i})
                    tp.remove(i)
                    if u['money'] > m:
                        m = u['money']
                        tex1 = f"Имя: <@{i}>\nМонетки: {u['money']}"

                    if u['lvl'] > l:
                        l = u['lvl']
                        tex2 = f"Имя: <@{i}>\nУровень: {u['lvl']}"

                    if u['+rep'] > r:
                        r = u['+rep']
                        tex3 = f"Имя: <@{i}>\nРепутация: {u['+rep']}"



                if tp == []:
                    emb5.add_field(name = "Топ по монеткам", value = tex1)
                    emb5.add_field(name = "Топ по уровню", value = tex2)
                    emb5.add_field(name = "Топ по репутации", value = tex3)
                    break

            msg = await ctx.send(embed = emb1)

            def check( reaction, user):
                nonlocal msg
                if dom['flag'] == None:
                    if clvl < 5:
                        return user == ctx.author and str(reaction.emoji) in solb0 and str(reaction.message) == str(msg)
                    elif clvl < 10 and clvl >= 5:
                        return user == ctx.author and str(reaction.emoji) in solb5 and str(reaction.message) == str(msg)
                    elif clvl < 15 and clvl >= 10:
                        return user == ctx.author and str(reaction.emoji) in solb10 and str(reaction.message) == str(msg)
                    elif clvl < 20 and clvl >= 15:
                        return user == ctx.author and str(reaction.emoji) in solb15 and str(reaction.message) == str(msg)
                    elif clvl >= 20:
                        return user == ctx.author and str(reaction.emoji) in solb20 and str(reaction.message) == str(msg)
                else:
                    if clvl < 5:
                        return user == ctx.author and str(reaction.emoji) in sola0 and str(reaction.message) == str(msg)
                    elif clvl < 10 and clvl >= 5:
                        return user == ctx.author and str(reaction.emoji) in sola5 and str(reaction.message) == str(msg)
                    elif clvl < 15 and clvl >= 10:
                        return user == ctx.author and str(reaction.emoji) in sola10 and str(reaction.message) == str(msg)
                    elif clvl < 20 and clvl >= 15:
                        return user == ctx.author and str(reaction.emoji) in sola15 and str(reaction.message) == str(msg)
                    elif clvl >= 20:
                        return user == ctx.author and str(reaction.emoji) in sola20 and str(reaction.message) == str(msg)


            def check2( reaction, user):
                nonlocal msg
                return user == ctx.author and str(reaction.emoji) in arrows and str(reaction.message) == str(msg)

            def check3( reaction, user):
                nonlocal msg
                return user == ctx.author and str(reaction.emoji) in shop and str(reaction.message) == str(msg)

            async def rr2():
                nonlocal reaction
                nonlocal index_page
                nonlocal clvl
                nonlocal dom
                if str(reaction.emoji) == '🔼':
                    await msg.remove_reaction('🔼', member)
                    if index_page == 1:
                        pass
                    elif index_page == 2:
                        await msg.edit(embed = emb2)
                        index_page = index_page - 1
                    elif index_page == 3:
                        await msg.edit(embed = embu2)
                        index_page = index_page - 1
                    pass
                elif str(reaction.emoji) == '🔽':
                    await msg.remove_reaction('🔽', member)
                    if index_page == 1:
                        await msg.edit(embed = embu2)
                        index_page = index_page + 1
                    elif index_page == 2:
                        await msg.edit(embed = embu3)
                        index_page = index_page + 1
                    elif index_page == 3:
                        pass
                    pass

                elif str(reaction.emoji) == '📑':
                    await msg.remove_reaction('📑', member)
                    await msg.clear_reactions()

                    if dom['flag'] == None:

                        if clvl < 5:
                            for x in solb0:
                                await msg.add_reaction(x)

                        elif clvl < 10 and clvl >= 5:
                            for x in solb5:
                                await msg.add_reaction(x)

                        elif clvl < 15 and clvl >= 10:
                            for x in solb10:
                                await msg.add_reaction(x)

                        elif clvl < 20 and clvl >= 15:
                            for x in solb15:
                                await msg.add_reaction(x)

                        elif clvl >= 20:
                            for x in solb20:
                                await msg.add_reaction(x)

                    else:
                        if clvl < 5:
                            for x in sola0:
                                await msg.add_reaction(x)

                        elif clvl < 10 and clvl >= 5:
                            for x in sola5:
                                await msg.add_reaction(x)

                        elif clvl < 15 and clvl >= 10:
                            for x in sola10:
                                await msg.add_reaction(x)

                        elif clvl < 20 and clvl >= 15:
                            for x in sola15:
                                await msg.add_reaction(x)

                        elif clvl >= 20:
                            for x in sola20:
                                await msg.add_reaction(x)

                    await reackt()

                elif str(reaction.emoji) == '❌':
                    await msg.clear_reactions()

            async def rr3():
                nonlocal reaction
                nonlocal dom
                if str(reaction.emoji) == '1️⃣':
                    await msg.remove_reaction('1️⃣', member)


                    emb6 = discord.Embed(color=0xf03e65).set_author(icon_url = '{}'.format(dom["flag"]), name = f'db.clubshop | {dom["name"]}'
                    ).add_field(name = 'Банк:',value = f'Монетки: {dom["bank"]}', inline = False
                    ).add_field(name = ':one: - слоты для пользователей', value = f'+5 слотов для пользователей\n`Цена: 2.000 монет\nСлотов: {dom["max_users"]}`')
                    if dom['max_users'] == 100:
                        await ctx.send('В клубе может быть до 100 человек')
                    else:
                        if dom['bank'] >= 2000:
                            db.clubs.update_one( {"name": dom['name']}, {"$inc":{"max_users": 5}} )
                            db.clubs.update_one( {"name": dom['name']}, {"$inc":{"bank": -2000}} )
                            dom = db.clubs.find_one({"name": name})
                            await msg.edit(embed = emb6)

                        else:
                            await msg.edit(embed = emb6er1)
                            await asyncio.sleep(4)
                            await msg.edit(embed = emb6)



                    pass

                elif str(reaction.emoji) == '📑':
                    await msg.remove_reaction('📑', member)
                    await msg.clear_reactions()
                    await msg.edit(embed = emb1)

                    if dom['flag'] == None:

                        if clvl < 5:
                            for x in solb0:
                                await msg.add_reaction(x)

                        elif clvl < 10 and clvl >= 5:
                            for x in solb5:
                                await msg.add_reaction(x)

                        elif clvl < 15 and clvl >= 10:
                            for x in solb10:
                                await msg.add_reaction(x)

                        elif clvl < 20 and clvl >= 15:
                            for x in solb15:
                                await msg.add_reaction(x)

                        elif clvl >= 20:
                            for x in solb20:
                                await msg.add_reaction(x)

                    else:
                        if clvl < 5:
                            for x in sola0:
                                await msg.add_reaction(x)

                        elif clvl < 10 and clvl >= 5:
                            for x in sola5:
                                await msg.add_reaction(x)

                        elif clvl < 15 and clvl >= 10:
                            for x in sola10:
                                await msg.add_reaction(x)

                        elif clvl < 20 and clvl >= 15:
                            for x in sola15:
                                await msg.add_reaction(x)

                        elif clvl >= 20:
                            for x in sola20:
                                await msg.add_reaction(x)

                    await reackt()

                elif str(reaction.emoji) == '❌':
                    await msg.clear_reactions()


            async def reackt2():
                nonlocal reaction
                try:
                    reaction, user = await self.bot.wait_for('reaction_add', timeout=30.0, check = check2)
                except asyncio.TimeoutError:
                    await msg.clear_reactions()
                else:
                    await rr2(), await reackt2()

            async def reackt3():
                nonlocal reaction
                try:
                    reaction, user = await self.bot.wait_for('reaction_add', timeout=30.0, check = check3)
                except asyncio.TimeoutError:
                    await msg.clear_reactions()
                else:
                    await rr3(), await reackt3()


            async def rr():
                nonlocal reaction
                nonlocal dom
                nonlocal arrows
                dom = db.clubs.find_one({"name": name})
                if str(reaction.emoji) == '📜':
                    await msg.remove_reaction('📜', member)
                    await msg.edit(embed = emb1)
                    pass

                elif str(reaction.emoji) == '👥':
                    await msg.remove_reaction('👥', member)
                    await msg.edit(embed = emb2)
                    if dom['max_users'] > 25 and ul > 25:
                        await msg.clear_reactions()
                        for x in arrows:
                            await msg.add_reaction(x)
                        await reackt2()
                    pass

                elif str(reaction.emoji) == '🎴':
                    await msg.remove_reaction('🎴', member)
                    await msg.edit(embed = emb3)
                    pass


                elif str(reaction.emoji) == '👑':
                    await msg.remove_reaction('👑', member)
                    await msg.edit(embed = emb5)
                    pass


                elif str(reaction.emoji) == '🛒':
                    await msg.remove_reaction('🛒', member)
                    if ctx.author.id in dom['members']:
                        await msg.edit(embed = emb6)
                        if user in dom['admins']:
                            await msg.clear_reactions()
                            for x in shop:
                                await msg.add_reaction(x)
                            await reackt3()
                    pass

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



            if dom['flag'] == None:

                if clvl < 5:
                    for x in solb0:
                        await msg.add_reaction(x)

                elif clvl < 10 and clvl >= 5:
                    for x in solb5:
                        await msg.add_reaction(x)

                elif clvl < 15 and clvl >= 10:
                    for x in solb10:
                        await msg.add_reaction(x)

                elif clvl < 20 and clvl >= 15:
                    for x in solb15:
                        await msg.add_reaction(x)

                elif clvl >= 20:
                    for x in solb20:
                        await msg.add_reaction(x)

            else:
                if clvl < 5:
                    for x in sola0:
                        await msg.add_reaction(x)

                elif clvl < 10 and clvl >= 5:
                    for x in sola5:
                        await msg.add_reaction(x)

                elif clvl < 15 and clvl >= 10:
                    for x in sola10:
                        await msg.add_reaction(x)

                elif clvl < 20 and clvl >= 15:
                    for x in sola15:
                        await msg.add_reaction(x)

                elif clvl >= 20:
                    for x in sola20:
                        await msg.add_reaction(x)

            await reackt()

        else:
            emb = discord.Embed(description = 'Такого клуба не существует!', color=0xf03e65)
            emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
            await ctx.send(embed = emb)



    @commands.command(usage = '(tag <= 4 characters) (name <= 25 characters)', description = 'Создание клуба.',aliases = ['создать_клуб'])
    async def club_create(self, ctx, tag = None, *, name = None):
        global users
        if users.find_one({"userid": ctx.author.id}) == None:
            await ctx.send(f'У данного пользователя не создан аккаунт, пропишите {ctx.prefix}help для создания!')
            return

        player = users.find_one({"userid": ctx.author.id})
        balance = player['money']
        ship = player['guild']


        if tag is None:
            emb = discord.Embed(description = 'Введите тег клуба!',color=0xf03e65)
            emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
            await ctx.send(embed = emb)

        elif len(tag) > 4:
            emb = discord.Embed(description = 'Тег клуба слишком длиный! (максимум 4 символа) ',color=0xf03e65)
            emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
            await ctx.send(embed = emb)

        elif name is None:
            emb = discord.Embed(description = 'Введите название клуба!',color=0xf03e65)
            emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
            await ctx.send(embed = emb)

        elif len(name) > 25:
            emb = discord.Embed(description = 'Имя клуба слишком длиное! (максимум 25 символов) ',color=0xf03e65)
            emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
            await ctx.send(embed = emb)

        else:
            if balance < 5000:
                emb = discord.Embed(description = 'Недостаточно монет! (требуется 5.000 монет)',color=0xf03e65)
                emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
                await ctx.send(embed = emb)

            else:
                if db.clubs.count_documents({"name": name}):
                    emb = discord.Embed(description = 'Такой клуб уже существует!',color=0xf03e65)
                    emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
                    await ctx.send(embed = emb)

                if db.clubs.count_documents({"tag": tag}):
                    emb = discord.Embed(description = 'Такой тег уже существует!',color=0xf03e65)
                    emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
                    await ctx.send(embed = emb)
                else:
                    if ship != None:
                        emb = discord.Embed(description = f'Вы уже в в клубе',color=0xf03e65)
                        emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
                        await ctx.send(embed = emb)
                    else:
                        emb = discord.Embed(description = 'Вы успешно создали клуб!',color=0xf03e65)
                        emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
                        await ctx.send(embed = emb)
                        db.clubs.insert_one({"owner": ctx.author.id, "name": name, 'tag': tag, "bio": 'Пусто',
                        "flag": None, "lvl": 1, "exp": 0, "created": time.strftime('%X, %d %B, %Y'),
                        "members": [ctx.author.id], 'admins': [], 'global_club': False, 'lvl_enter': 0, 'max_users': 25, 'bank': 0})
                        m = balance - 5000
                        users.update_one({"userid": ctx.author.id}, {"$set": {"money": m}})
                        users.update_one({"userid": ctx.author.id}, {"$set": {"guild": name}})





    @commands.command(usage = '(url)', description = 'Установка баннера клуба. Стоимость 1к', aliases = ['баннер_клуба'])
    async def club_banner(self, ctx, link = None):
        global users
        if users.find_one({"userid": ctx.author.id}) == None:
            await ctx.send(f'У данного пользователя не создан аккаунт, пропишите {ctx.prefix}help для создания!')
            return
        user = users.find_one({"userid": ctx.author.id})


        if link is None:
            emb = discord.Embed(description = 'Укажите ссылку на баннер для клуба!', color=0xf03e65)
            emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
            await ctx.send(embed = emb)
            return

        else:
            if user['guild'] != None:
                guild = db.clubs.find_one({"name": user['guild']})
                if guild['owner'] == ctx.author.id or ctx.author.id in guild["admins"]:
                    if user['money'] > 999:
                        try:
                            emb = discord.Embed(description = 'Вы поменяли баннер клуба!', color=0xf03e65)
                            emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
                            emb.set_image(url = link)

                            await ctx.send(embed = emb)
                            await ctx.message.delete()

                            name = guild['name']

                            db.clubs.update_one({"name": name}, {"$set": {"flag": link}})

                            newcash = user['money'] - 1000
                            users.update_one({"userid": ctx.author.id}, {"$set": {"money": newcash}})

                        except Exception:
                            emb = discord.Embed(description = 'Укажите ссылку на изображение', color=0xf03e65)
                            emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
                            await ctx.send(embed = emb)
                    else:
                        emb = discord.Embed(description = 'Недостаточно монет(требуется 1.000 монет)!', color=0xf03e65)
                        emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
                        await ctx.send(embed = emb)
                else:
                    emb = discord.Embed(description = 'Только глава/админ может поменять баннер клуба!', color=0xf03e65)
                    emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
                    await ctx.send(embed = emb)

                    await ctx.message.delete()
            else:
                emb = discord.Embed(description = 'Вы не состоите в клубе', color=0xf03e65)
                emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
                await ctx.send(embed = emb)

                await ctx.message.delete()


    @commands.command(usage = '(bio)', description = 'Установка информации о клубе. Стоимость 200.', aliases = ['био_клуба'])
    async def club_bio(self, ctx, *, bio = None):
        global users

        if users.find_one({"userid": ctx.author.id}) == None:
            await ctx.send(f'У данного пользователя не создан аккаунт, пропишите {ctx.prefix}help для создания!')
            return
        user = users.find_one({"userid": ctx.author.id})
        if user['guild'] != None:
            guild = db.clubs.find_one({"name": user['guild']})
            if guild['owner'] == ctx.author.id or ctx.author.id in guild["admins"]:

                if bio is None:
                    emb = discord.Embed(description = 'Укажите описание!', color=0xf03e65)
                    emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
                    await ctx.send(embed = emb)

                elif len(bio) > 200:
                    emb = discord.Embed(description = 'Слишком много символов(макс: 200)', color=0xf03e65)
                    emb.set_author(icon_url = '{}'.format(ctx.author.avatar.url), name = '{}'.format(ctx.author))
                    await ctx.send(embed = emb)

                if user['money'] > 199:

                    emb = discord.Embed(description = f'Вы поменяли описание вашей клуба на:\n```fix\n{bio}```', color=0xf03e65)
                    emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
                    await ctx.send(embed = emb)

                    name = guild['name']
                    newcash = user['money'] - 200
                    users.update_one({"userid": ctx.author.id}, {"$set": {"money": newcash}})
                    db.clubs.update_one({"name": name}, {"$set": {"bio": bio}})

                else:
                    emb = discord.Embed(description = 'Не достаточно монет (требуется 200)!', color=0xf03e65)
                    emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
                    await ctx.send(embed = emb)

            else:
                emb = discord.Embed(description = 'Только глава/админ может поменять описание клуба!', color=0xf03e65)
                emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
                await ctx.send(embed = emb)
        else:
            emb = discord.Embed(description = 'Вы не состоите в клубе', color=0xf03e65)
            emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
            await ctx.send(embed = emb)
            await ctx.message.delete()


    @commands.command(usage = '(@member)', description = 'Приглашение в свой клуб.', aliases = ['пригласить'])
    async def club_invite(self, ctx, member: discord.Member = None):
        global users

        if users.find_one({"userid": ctx.author.id}) == None:
            await ctx.send(f'У данного пользователя не создан аккаунт, пропишите {ctx.prefix}help для создания!')
            return
        mem = users.find_one({"userid": member.id})
        user = users.find_one({"userid": ctx.author.id})

        if member is None:
            emb = discord.Embed(description = 'Укажите пользователя!', color=0xf03e65)
            emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
            await ctx.send(embed = emb)

        if user['guild'] != None:
            guild = db.clubs.find_one({"name": user['guild']})
            if guild['owner'] == ctx.author.id or ctx.author.id in guild["admins"]:
                if mem['guild'] == None:
                    name = guild['name']
                    if len(guild['members']) < guild['max_users']:


                        solutions = ['✅', '❌']
                        emb = discord.Embed(title = f'Клуб {guild["name"]}', description = f'**{member}** хотите ли вы вступить в клуб **{name}?**', color=0xf03e65)

                        message = await ctx.send(embed = emb)

                        for x in solutions:
                            await message.add_reaction(x)

                        try:
                            react, user = await self.bot.wait_for('reaction_add', timeout= 60.0, check= lambda react, user: user == member and react.message.channel == ctx.channel and react.emoji in solutions)
                        except asyncio.TimeoutError:
                            emb = discord.Embed(description = 'Время на ответ вышло', color=0xf03e65)
                            emb.set_author(icon_url = '{}'.format(ctx.author.avatar.url), name = '{}'.format(ctx.author))

                            await message.edit(embed = emb)
                            await message.clear_reactions()
                        else:
                            if str(react.emoji) == '✅':
                                await message.clear_reactions()

                                emb = discord.Embed(title = f'Приглашения', description = f'**{member}** вступил в клуб **{name}!**', color=0xf03e65)
                                await message.edit(embed = emb)

                                users.update_one({'userid': member.id}, {"$set": {'guild': name}})

                                members = guild['members']
                                members.append(member.id)

                                db.clubs.update_one({"name": name}, {"$set": {"members": members}})

                            elif str(react.emoji) == '❌':
                                await message.clear_reactions()

                                emb = discord.Embed(title = f'Приглашения', description = f'**{member}** отказался от приглашения!', color=0xf03e65)

                                await message.edit(embed = emb)
                    else:
                        emb = discord.Embed(description = 'В клубе максимальное колличество пользователей', color=0xf03e65)
                        emb.set_author(icon_url = '{}'.format(ctx.author.avatar.url), name = '{}'.format(ctx.author))
                        await ctx.send(embed = emb)
                else:
                    emb = discord.Embed(description = 'Пользователь уже в клубе!', color=0xf03e65)
                    emb.set_author(icon_url = '{}'.format(ctx.author.avatar.url), name = '{}'.format(ctx.author))
                    await ctx.send(embed = emb)
            else:
                emb = discord.Embed(description = 'Только глава/админ может приглашать людей!', color=0xf03e65)
                emb.set_author(icon_url = '{}'.format(ctx.author.avatar.url), name = '{}'.format(ctx.author))
                await ctx.send(embed = emb)
        else:
            emb = discord.Embed(description = 'Вы не состоите в клубе', color=0xf03e65)
            emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
            await ctx.send(embed = emb)
            await ctx.message.delete()

    @commands.command(usage = '(@member)', description = 'Передача прав на клуб.', aliases = ['передать_создателя'])
    async def club_owner(self, ctx, member: discord.Member = None):
        global users

        if users.find_one({"userid": ctx.author.id}) == None:
            await ctx.send(f'У данного пользователя не создан аккаунт, пропишите {ctx.prefix}help для создания!')
            return
        mem = users.find_one({"userid": member.id})
        user = users.find_one({"userid": ctx.author.id})
        guild = db.clubs.find_one({"name": user['guild']})

        if member == None:

            emb = discord.Embed(description = 'Укажите пользователя!', color=0xf03e65)
            emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
            await ctx.send(embed = emb)
            return

        else:
            if user['guild'] == None:
                emb = discord.Embed(description = 'Вы не в клубе!', color=0xf03e65)
                emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
                await ctx.send(embed = emb)
                return

            elif mem['guild'] == None:
                emb = discord.Embed(description = 'Пользователь не в вашем клубе!', color=0xf03e65)
                emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
                await ctx.send(embed = emb)
                return

            elif member == ctx.author:
                emb = discord.Embed(description = 'Вы и так овнер!', color=0xf03e65)
                emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
                await ctx.send(embed = emb)
                return


            elif guild['owner'] != ctx.author.id:
                emb = discord.Embed(description = 'Только глава может отдать клуб!', color=0xf03e65)
                emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
                await ctx.send(embed = emb)
                return

            else:
                clanName = user['guild']
                clanNameTwo = mem['guild']

                if clanName == clanNameTwo:
                    emb = discord.Embed(description = f'Вы успешно передали лидерство **{member}**', color=0xf03e65)
                    emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
                    await ctx.send(embed = emb)

                    db.clubs.update_one({"name": clanName}, {"$set": {"owner": member.id}})

                else:
                    emb = discord.Embed(description = 'Пользователь в другой клубе!', color=0xf03e65)
                    emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
                    await ctx.send(embed = emb)
                    return



    @commands.command(usage = '-', description = 'Покинулть клуб.', aliases = ['покинуть_клуб'])
    async def club_leave(self, ctx):
        global users

        if users.find_one({"userid": ctx.author.id}) == None:
            await ctx.send(f'У данного пользователя не создан аккаунт, пропишите {ctx.prefix}help для создания!')
            return

        user = users.find_one({"userid": ctx.author.id})
        guild = db.clubs.find_one({"name": user['guild']})

        if user['guild'] == None:
            emb = discord.Embed(description = 'Вы не в клуба!', color=0xf03e65)
            emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
            await ctx.send(embed = emb)

        else:

            if ctx.author.id != guild['owner']:
                name = user['guild']

                emb = discord.Embed(description = f'Вы покинули клуб {name}!', color=0xf03e65)
                emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
                await ctx.send(embed = emb)

                users.update_one({"userid": ctx.author.id}, {"$set": {"guild": None}})

                ad = guild['admins']
                if ctx.author.id in ad:
                    ad.remove(ctx.author.id)
                    db.clubs.update_one({"name": user['guild']}, {"$set": {"admins": ad}})

                members = guild['members']
                members.remove(ctx.author.id)
                db.clubs.update_one({"name": name}, {"$set": {"members": members}})

            else:
                emb = discord.Embed(description = 'Глава не может покинуть клуба!', color=0xf03e65)
                emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
                await ctx.send(embed = emb)

    @commands.command(usage = '(@member)', description = 'Кикнуть пользователя из клуба.', aliases = ['пнуть_из_клуба'])
    async def club_kick(self, ctx, member: discord.Member = None):
        global users

        if users.find_one({"userid": ctx.author.id}) == None:
            await ctx.send(f'У данного пользователя не создан аккаунт, пропишите {ctx.prefix}help для создания!')
            return

        user = users.find_one({"userid": ctx.author.id})
        guild = db.clubs.find_one({"name": user['guild']})
        mem = users.find_one({"userid": member.id})

        if member is None:
            emb = discord.Embed(description = 'Укажите пользователя', color=0xf03e65)
            emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
            await ctx.send(embed = emb)

        elif member == ctx.author:
            emb = discord.Embed(description = 'Самого себя кикнуть нельзя!', color=0xf03e65)
            emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
            await ctx.send(embed = emb)

        else:
            if user['guild'] == None:
                emb = discord.Embed(description = 'Вы не в клубе!', color=0xf03e65)
                emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
                await ctx.send(embed = emb)

            elif mem['guild'] == None:

                emb = discord.Embed(description = 'Пользователь не в клубе!', color=0xf03e65)
                emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
                await ctx.send(embed = emb)

            else:
                if guild['owner'] == ctx.author.id or ctx.author.id in guild["admins"]:

                    emb = discord.Embed(description = 'Только глава/админ может кикнуть участника из клуба!', color=0xf03e65)
                    emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
                    await ctx.send(embed = emb)

                else:
                    clanName1 = user['guild']
                    clanName2 = mem['guild']

                    if clanName1 == clanName2:
                        emb = discord.Embed(description = 'Вы успешно кикнули участника из клуба!', color=0xf03e65)
                        emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
                        await ctx.send(embed = emb)

                        members = guild['members']
                        ad = guild['admins']
                        if member.id in ad:
                            ad.remove(member.id)
                            db.clubs.update_one({"name": user['guild']}, {"$set": {"admins": ad}})
                        members.remove(member.id)
                        db.clubs.update_one({"name": user['guild']}, {"$set": {"members": members}})
                        users.update_one({"userid": member.id}, {"$set": {"guild": None}})

                    else:
                        emb = discord.Embed(description = 'Данный человек находится в другом клубе!', color=0xf03e65)
                        emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
                        await ctx.send(embed = emb)


    @commands.command(usage = '(new_name)', description = 'Изменить название клуба. Стимость 2к', aliases = ['переименовать_клуб'])
    async def club_rename(self, ctx, *, name = None):
        global users

        if users.find_one({"userid": ctx.author.id}) == None:
            await ctx.send(f'У данного пользователя не создан аккаунт, пропишите {ctx.prefix}help для создания!')
            return

        user = users.find_one({"userid": ctx.author.id})
        guild = db.clubs.find_one({"name": user['guild']})

        if name is None:
            emb = discord.Embed(description = 'Введите название клуба!', color=0xf03e65)
            emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
            await ctx.send(embed = emb)

        elif len(name) > 25:
            emb = discord.Embed(description = 'Имя клуба слишком длиное!', color=0xf03e65)
            emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
            await ctx.send(embed = emb)

        else:

            if user['guild'] == None:
                emb = discord.Embed(description = 'Вы не в клубе!', color=0xf03e65)
                emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
                await ctx.send(embed = emb)
            else:
                if guild['owner'] != ctx.author.id:
                    emb = discord.Embed(description = 'Только глава может изменить имя клана!', color=0xf03e65)
                    emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
                    await ctx.send(embed = emb)

                else:
                    if db.clubs.count_documents({"name": name}):
                        emb = discord.Embed(description = 'Такой клуб уже существует!', color=0xf03e65)
                        emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
                        await ctx.send(embed = emb)
                    else:
                        result = user['money']
                        if result > 1999:
                            emb = discord.Embed(description = f'Вы изменили имя клуба на **{name}**', color=0xf03e65)
                            emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
                            await ctx.send(embed = emb)

                            names = guild['name']
                            members = guild['members']
                            db.clubs.update_one({"name": names}, {"$set": {"name": name}})

                            for i in members:
                                users.update_one({'userid': i}, {'$set': {'guild': name}})

                            newcash2 = user['money'] - 2000
                            users.update_one({"userid": ctx.author.id}, {"$set": {"money": newcash2}})

                        else:
                            emb = discord.Embed(description = 'Недостаточно монет (требуется 2.000 монет)!', color=0xf03e65)
                            emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
                            await ctx.send(embed = emb)

    @commands.command(usage = '(new_tag <= 4 characters)', description = 'Изменение тэга клуба.', aliases = ['сменить_тег_клуба'])
    async def tag_rename(self, ctx, *, tag = None):
        global users

        if users.find_one({"userid": ctx.author.id}) == None:
            await ctx.send(f'У данного пользователя не создан аккаунт, пропишите {ctx.prefix}help для создания!')
            return

        user = users.find_one({"userid": ctx.author.id})
        guild = db.clubs.find_one({"name": user['guild']})

        if tag is None:
            emb = discord.Embed(description = 'Введите название клуба!', color=0xf03e65)
            emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
            await ctx.send(embed = emb)

        elif len(tag) > 4:
            emb = discord.Embed(description = 'Имя клуба слишком длиное!', color=0xf03e65)
            emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
            await ctx.send(embed = emb)

        else:

            if user['guild'] == None:
                emb = discord.Embed(description = 'Вы не в клубе!', color=0xf03e65)
                emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
                await ctx.send(embed = emb)
            else:
                if guild['owner'] != ctx.author.id:
                    emb = discord.Embed(description = 'Только глава может изменить тег!', color=0xf03e65)
                    emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
                    await ctx.send(embed = emb)

                else:
                    if db.clubs.count_documents({"tag": tag}):
                        emb = discord.Embed(description = 'Такой тег уже существует!', color=0xf03e65)
                        emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
                        await ctx.send(embed = emb)
                    else:
                        result = user['money']
                        if result > 3999:
                            emb = discord.Embed(description = f'Вы изменили тег на **{tag}**', color=0xf03e65)
                            emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
                            await ctx.send(embed = emb)

                            db.clubs.update_one({"name": guild['name']}, {"$set": {"tag": tag}})


                            users.update_one({"userid": ctx.author.id}, {"$set": {"money": user['money'] - 400}})

                        else:
                            emb = discord.Embed(description = 'Недостаточно монет (требуется 4.000)!', color=0xf03e65)
                            emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
                            await ctx.send(embed = emb)

    @commands.command(usage = '-', description = 'Удаление своего клуба.', aliases = ['удалить_клуб'])
    async def club_delete(self, ctx):
        global users

        if users.find_one({"userid": ctx.author.id}) == None:
            await ctx.send(f'У данного пользователя не создан аккаунт, пропишите {ctx.prefix}help для создания!')
            return

        user = users.find_one({"userid": ctx.author.id})
        guild = db.clubs.find_one({"name": user['guild']})

        if user['guild'] == None:
            emb = discord.Embed(description = 'Вы не в клубе!', color=0xf03e65)
            emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
            await ctx.send(embed = emb)


        else:
            if guild['owner'] != ctx.author.id:

                emb = discord.Embed(description = 'Только глава может удалить клуб!', color=0xf03e65)
                emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
                await ctx.send(embed = emb)

            else:
                emb = discord.Embed(description = 'Вы успешно удалили клуб!', color=0xf03e65)
                emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
                await ctx.send(embed = emb)

                name = guild['name']
                members = guild['members']

                for i in members:
                    users.update_one({'userid': i}, {'$set': {'guild': None}})


                db.clubs.delete_one({"name": name})




    @commands.command(usage = '(@member)', description = 'Назначение админа клуба.', aliases = ['добавить_админа_клуба'])
    async def club_admin_add(self, ctx, member: discord.Member = None):
        global users

        if users.find_one({"userid": ctx.author.id}) == None:
            await ctx.send(f'У данного пользователя не создан аккаунт, пропишите {ctx.prefix}help для создания!')
            return

        mem = users.find_one({"userid": member.id})
        user = users.find_one({"userid": ctx.author.id})

        if member is None:
            emb = discord.Embed(description = 'Укажите пользователя!', color=0xf03e65)
            emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
            await ctx.send(embed = emb)
            return

        if user['guild'] != None:
            guild = db.clubs.find_one({"name": user['guild']})
            if guild['owner'] == ctx.author.id:
                if mem['guild'] == user['guild']:
                    ad = guild['admins']
                    ad.append(member.id)
                    db.clubs.update_one({'name': user['guild']}, {'$set': {'admins': ad}})
                    emb = discord.Embed(description = f'Теперь <@{member.id}> админ в вашем клубе!', color=0xf03e65)
                    emb.set_author(icon_url = '{}'.format(ctx.author.avatar.url), name = '{}'.format(ctx.author))
                    await ctx.send(embed = emb)
                else:
                    emb = discord.Embed(description = 'Пользователь не в вашем клубе!', color=0xf03e65)
                    emb.set_author(icon_url = '{}'.format(ctx.author.avatar.url), name = '{}'.format(ctx.author))
                    await ctx.send(embed = emb)
            else:
                emb = discord.Embed(description = 'Только глава может назначать админов клуба!', color=0xf03e65)
                emb.set_author(icon_url = '{}'.format(ctx.author.avatar.url), name = '{}'.format(ctx.author))
                await ctx.send(embed = emb)
        else:
            emb = discord.Embed(description = 'Вы не состоите в клубе', color=0xf03e65)
            emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
            await ctx.send(embed = emb)
            await ctx.message.delete()

    @commands.command(aliases = ['club_admin_delete', "удалить_админа_клуба"], usage = '(@member)', description = 'Удаление админа клуба.')
    async def club_admin_remove(self, ctx, member: discord.Member = None):
        global users

        if users.find_one({"userid": ctx.author.id}) == None:
            await ctx.send(f'У данного пользователя не создан аккаунт, пропишите {ctx.prefix}help для создания!')
            return

        mem = users.find_one({"userid": member.id})
        user = users.find_one({"userid": ctx.author.id})

        if member is None:
            emb = discord.Embed(description = 'Укажите пользователя!', color=0xf03e65)
            emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
            await ctx.send(embed = emb)
            return

        if user['guild'] != None:
            guild = db.clubs.find_one({"name": user['guild']})
            if guild['owner'] == ctx.author.id:
                if mem['guild'] == user['guild']:
                    ad = guild['admins']
                    ad.remove(member.id)

                    db.clubs.update_one({'name': user['guild']}, {'$set': {'admins': ad}})
                    emb = discord.Embed(description = f'Вы сняли <@{member.id}> с поста админа!', color=0xf03e65)
                    emb.set_author(icon_url = '{}'.format(ctx.author.avatar.url), name = '{}'.format(ctx.author))
                    await ctx.send(embed = emb)
                else:
                    emb = discord.Embed(description = 'Пользователь не в вашем клубе!', color=0xf03e65)
                    emb.set_author(icon_url = '{}'.format(ctx.author.avatar.url), name = '{}'.format(ctx.author))
                    await ctx.send(embed = emb)
            else:
                emb = discord.Embed(description = 'Только глава может назначать админов клуба!', color=0xf03e65)
                emb.set_author(icon_url = '{}'.format(ctx.author.avatar.url), name = '{}'.format(ctx.author))
                await ctx.send(embed = emb)
        else:
            emb = discord.Embed(description = 'Вы не состоите в клубе', color=0xf03e65)
            emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
            await ctx.send(embed = emb)
            await ctx.message.delete()

    @commands.command(usage = '-', description = 'Изменение статуса клуба.', aliases = ['статус_клуба'])
    async def club_status(self, ctx):
        global users

        if users.find_one({"userid": ctx.author.id}) == None:
            await ctx.send(f'У данного пользователя не создан аккаунт, пропишите {ctx.prefix}help для создания!')
            return

        user = users.find_one({"userid": ctx.author.id})
        reaction = 'a'


        if user['guild'] != None:
            guild = db.clubs.find_one({"name": user['guild']})
            if guild['owner'] == ctx.author.id or ctx.author.id in guild["admins"]:

                if guild['global_club'] == False:
                    t1 = "закрытого"
                    t2 = "открытый"
                    t3 = True
                else:
                    t1 = "открытого"
                    t2 = "закрытый"
                    t3 = False


                solutions = ['✒', '❌']
                emb1 = discord.Embed(title = f'Смена статуса клуба',
                description = f'Нажмите на `✒` что бы сменить статус клуба с `{t1}` на `{t2}`', color=0xf03e65)

                emb2 = discord.Embed(title = f'Статус клуба изменён',
                description = f'Статус клуба теперь `{t2}`', color=0xf03e65)



                msg = await ctx.send(embed = emb1)

                def check( reaction, user):
                    nonlocal msg
                    return user == ctx.author and str(reaction.emoji) in solutions and str(reaction.message) == str(msg)

                async def rr():
                    nonlocal reaction
                    if str(reaction.emoji) == '✒':
                        await msg.remove_reaction('✒', ctx.author)
                        await msg.edit(embed = emb2)
                        db.clubs.update_one({'name': user['guild']}, {'$set': {'global_club': t3}})
                        await msg.clear_reactions()
                        pass

                    elif str(reaction.emoji) == '❌':
                        await msg.clear_reactions()

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

            else:
                emb = discord.Embed(description = 'Только глава/админ может менять статус клуба!', color=0xf03e65)
                emb.set_author(icon_url = '{}'.format(ctx.author.avatar.url), name = '{}'.format(ctx.author))
                await ctx.send(embed = emb)
        else:
            emb = discord.Embed(description = 'Вы не состоите в клубе', color=0xf03e65)
            emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
            await ctx.send(embed = emb)
            await ctx.message.delete()

    @commands.command(usage = '(lvl)', description = 'Изменение уровня входа.', aliases = ['уровень_входа'])
    async def club_lvl_enter(self, ctx, lvl:int = 0):
        global users

        if users.find_one({"userid": ctx.author.id}) == None:
            await ctx.send(f'У данного пользователя не создан аккаунт, пропишите {ctx.prefix}help для создания!')
            return

        user = users.find_one({"userid": ctx.author.id})


        if user['guild'] != None:
            guild = db.clubs.find_one({"name": user['guild']})
            if guild['owner'] == ctx.author.id or ctx.author.id in guild["admins"]:
                if lvl >= 0 and lvl < 999:
                    emb = discord.Embed(description = f'Вы поменяли уровень вступления в клуб на {lvl}', color=0xf03e65)
                    emb.set_author(icon_url = '{}'.format(ctx.author.avatar.url), name = '{}'.format(ctx.author))
                    await ctx.send(embed = emb)
                    db.clubs.update_one({'name': user['guild']}, {'$set': {'lvl_enter': lvl}})

                else:
                    emb = discord.Embed(description = 'Можно указать уровень от 0 до 999!', color=0xf03e65)
                    emb.set_author(icon_url = '{}'.format(ctx.author.avatar.url), name = '{}'.format(ctx.author))
                    await ctx.send(embed = emb)
            else:
                emb = discord.Embed(description = 'Только глава/админ может менять уровень вступления в клуб!', color=0xf03e65)
                emb.set_author(icon_url = '{}'.format(ctx.author.avatar.url), name = '{}'.format(ctx.author))
                await ctx.send(embed = emb)
        else:
            emb = discord.Embed(description = 'Вы не состоите в клубе', color=0xf03e65)
            emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
            await ctx.send(embed = emb)
            await ctx.message.delete()

    @commands.command(usage = '(name)', description = 'Вступить в клую.', aliases = ['вступить'])
    async def club_enter(self, ctx, *, name = None):
        global users

        if users.find_one({"userid": ctx.author.id}) == None:
            await ctx.send(f'У данного пользователя не создан аккаунт, пропишите {ctx.prefix}help для создания!')
            return

        user = users.find_one({"userid": ctx.author.id})

        if name is None:
            emb = discord.Embed(description = 'Укажите клуб!', color=0xf03e65)
            emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
            await ctx.send(embed = emb)
            return


        if user['guild'] == None:
            guild = db.clubs.find_one({"name": name})
            if guild['global_club'] == False:
                await ctx.send("Данный клуб закрытый")
                return
            if guild != None:
                if len(guild['members']) < guild['max_users']:
                    if guild['lvl_enter'] <= user['lvl']:
                        emb = discord.Embed(description = f'Вы успешно вступили в клуб {guild["name"]}', color=0xf03e65)
                        emb.set_author(icon_url = '{}'.format(ctx.author.avatar.url), name = '{}'.format(ctx.author))
                        await ctx.send(embed = emb)

                        mem = guild['members']
                        mem.append(ctx.author.id)

                        db.clubs.update_one({'name': name}, {'$set': {'members': mem}})
                        users.update_one({'userid': ctx.author.id}, {'$set': {'guild': name}})

                    else:
                        emb = discord.Embed(description = 'Ваш уровень меньше чем уровень для вступления в этот клуб!', color=0xf03e65)
                        emb.set_author(icon_url = '{}'.format(ctx.author.avatar.url), name = '{}'.format(ctx.author))
                        await ctx.send(embed = emb)
                else:
                    emb = discord.Embed(description = 'В клубе максимальное колличество пользователей!', color=0xf03e65)
                    emb.set_author(icon_url = '{}'.format(ctx.author.avatar.url), name = '{}'.format(ctx.author))
                    await ctx.send(embed = emb)
            else:
                emb = discord.Embed(description = f'Клуба по имени {name} не найден', color=0xf03e65)
                emb.set_author(icon_url = '{}'.format(ctx.author.avatar.url), name = '{}'.format(ctx.author))
                await ctx.send(embed = emb)
        else:
            emb = discord.Embed(description = 'Вы уже состоите в клубе!', color=0xf03e65)
            emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
            await ctx.send(embed = emb)
            await ctx.message.delete()

    @commands.command(aliases = ['club_dep', 'пополнить_банк'], usage = '(amout)', description = 'Внести сумму в банк клуба.')
    async def club_deposit(self,ctx, amout:int):
        global users

        if users.find_one({"userid": ctx.author.id}) == None:
            await ctx.send(f'У данного пользователя не создан аккаунт, пропишите {ctx.prefix}help для создания!')
            return

        kk = self.bot.get_emoji(778533802342875136)
        user = users.find_one({"userid": ctx.author.id})

        if user['guild'] != None:
            guild = db.clubs.find_one({"name": user['guild']})
            if user['money'] >= amout and amout > 0:
                if user['Nitro'] == False:
                    am = amout - amout / 100 * 2
                else:
                    am = amout

                emb = discord.Embed(description = f'Вы положили в банк клуба {am}', color=0xf03e65)
                emb.set_author(icon_url = '{}'.format(ctx.author.avatar.url), name = '{}'.format(ctx.author))
                await ctx.send(embed = emb)

                users.update_one({'userid':ctx.author.id}, {'$inc':{"money": -amout}})
                db.clubs.update_one({'name': user['guild']}, {'$inc':{"bank": round(am)}})

            else:
                emb = discord.Embed(description = f'У вас не достаточно {kk}монет или число меньше 0!', color=0xf03e65)
                emb.set_author(icon_url = '{}'.format(ctx.author.avatar.url), name = '{}'.format(ctx.author))
                await ctx.send(embed = emb)
        else:
            emb = discord.Embed(description = 'Вы не состоите в клубе', color=0xf03e65)
            emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
            await ctx.send(embed = emb)
            await ctx.message.delete()

    @commands.command(usage = '(amout)', description = 'Снять депозит с банка клуба.', aliases = ['снять'])
    async def club_with(self,ctx, amout:int):
        global users

        if users.find_one({"userid": ctx.author.id}) == None:
            await ctx.send(f'У данного пользователя не создан аккаунт, пропишите {ctx.prefix}help для создания!')
            return

        kk = self.bot.get_emoji(778533802342875136)
        user = users.find_one({"userid": ctx.author.id})

        if user['guild'] != None:
            guild = db.clubs.find_one({"name": user['guild']})
            if guild['bank'] >= amout and amout > 0:
                if guild['owner'] == ctx.author.id or ctx.author.id in guild["admins"]:

                    emb = discord.Embed(description = f'Вы взяли из банка клуба {amout}', color=0xf03e65)
                    emb.set_author(icon_url = '{}'.format(ctx.author.avatar.url), name = '{}'.format(ctx.author))
                    await ctx.send(embed = emb)

                    users.update_one({'userid':ctx.author.id}, {'$inc':{"money": amout}})
                    db.clubs.update_one({'name': user['guild']}, {'$inc':{"bank": -amout}})

                else:
                    emb = discord.Embed(description = f'Только глава/админ может взять {kk}монетки из банка клуба!', color=0xf03e65)
                    emb.set_author(icon_url = '{}'.format(ctx.author.avatar.url), name = '{}'.format(ctx.author))
                    await ctx.send(embed = emb)
            else:
                emb = discord.Embed(description = 'В банке клуба нет такой суммы или число меньше 0!', color=0xf03e65)
                emb.set_author(icon_url = '{}'.format(ctx.author.avatar.url), name = '{}'.format(ctx.author))
                await ctx.send(embed = emb)
        else:
            emb = discord.Embed(description = 'Вы не состоите в клубе', color=0xf03e65)
            emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
            await ctx.send(embed = emb)
            await ctx.message.delete()




def setup(bot):
    bot.add_cog(clubs(bot))
