import discord
from discord.ext import commands
import requests
from PIL import Image, ImageFont, ImageDraw, ImageOps
import io
import sys
import random
from random import choice
import asyncio
import nekos
import time
import os
from Cybernator import Paginator
import pymongo
from bs4 import BeautifulSoup as BS
from collections import Counter
sys.path.append("..")
from AI2 import functions as funs

client2 = pymongo.MongoClient("mongodb+srv://bot:12452987190076@cluster0.rkh6o.mongodb.net/<dbname>?retryWrites=true&w=majority")
rpg = client2.bot
auc = rpg.auc
bback = rpg.backs
items = rpg.items
players = rpg.players
regions = rpg.regions
mobs = rpg.mobs


class MainCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def create(self,ctx):
        global players
        i = ctx.author
        if players.find_one({"userid": i.id}) == None:
            user = {
                "username": f"{i.name}#{i.discriminator}",
                "userid": i.id,
                "floor": None,
                "hp":100.0,
                "hpmax":100.0,
                "mana": 10.0,
                "manamax": 10.0,
                "lvl": 1,
                "xp":0.0,
                "coins": 0,
                "weapon":1,
                "armor":5,
                "skills": {},
                "pet": None,
                "kingship": None,
                "playstat": "player",
                "elemens": [],
                "regions": [],
                "allies": [],
                "accessories": [],
                "inv":[1]

            }
            players.insert_one(user)
            await ctx.send("Вы были успешно добавнены в игровую систему!")
        else:
            await ctx.send("У вас уже есть аккаунт")

    @commands.command(aliases = ["инвентарь", "i"])
    async def inv(self, ctx, member: discord.Member = None):
        if member == None:
            member = ctx.author

        user = players.find_one({'userid':member.id})
        weapon = items.find_one({'id': user['weapon']})
        inv = user['inv']

        solutions = ['<:profile_page:780678064123412511>', '<:inventory_page:781462475177721877>', '❌']
        reaction = 'a'

        if ctx.author == member:
            players.update_one({'userid': ctx.author.id}, {'$set': {'username':f"{member.name}#{member.discriminator}"}})


        emb = discord.Embed(title='<:profile:780366303965347850> Пофиль | RPG',color=0xf03e65).set_thumbnail(url= member.avatar_url)
        emb2 = discord.Embed(title=f'<:profile:780366303965347850> Инвентарь | {len(inv)}',color=0xf03e65)

        if user["pet"] == None:
            pt = "Нету"

        if user['kingship'] == None:
            ks = "Не состоит"
        else:
            king = kingdoms.find_one({'name': user['kingship']})
            ks = f"{king['name']} [{king['tag']}]"

        inv = user['inv']
        expn = 5 * user['lvl'] * user['lvl'] + 50 * user['lvl'] + 100
        emb.add_field(name="Харрактеристики", value =
            f"<:samurai:780371575676862464> Имя: **{user['username']}**\n"
            f"<:heart:780373079439572993> Здоровье: **{user['hp']}** | **{user['hpmax']}**\n"
            f"<:mana:780352235246452756> Мана: **{user['mana']}** | **{user['manamax']}**\n"
            f"<:leval:780353344157646850> Уровень: **{user['lvl']}**\n"
            f"<:expi:782974020248272957> Опыт: **{user['xp']}** | **{expn}**\n"
            f"<:pokecoin:780356652359745537> Коины: **{user['coins']}**\n"
            f"<:armor:780366328451039252> Броня: **{user['armor']}**\n"
            f"{weapon['emoji']} Оружие: **{weapon['name']}** | Урон: **{weapon['stat']}**\n"
            f"<:pet:780381475207905290> Питомец: **{pt}**\n"
            f"<:kingship:780383273133670420> Королество: **{ks}**\n"
            f"<:status:780386588604629012> Статус пользователя: **{user['playstat']}**\n"

            , inline = False)


        n = []
        text = " "
        num = 0
        text2 = " "
        num2 = 0
        text3 = " "
        num3 = 0
        text4 = " "
        num4 = 0
        text5 = " "
        num5 = 0


        for i in inv:
            if not i in n:
                item = items.find_one({'id':int(i)})
                if item['quality'] == 'n':
                    qul = '<:normal_q:781531816993620001>'
                if item['quality'] == 'u':
                    qul = '<:unusual_q:781531868780691476>'
                if item['quality'] == 'r':
                    qul = '<:rare_q:781531919140651048>'
                if item['quality'] == 'o':
                    qul = '<:orate_q:781531996866084874>'
                if item['quality'] == 'l':
                    qul = '<:legendary_q:781532085130100737>'

                if item['type'] == 'weapon':

                    text = text + f"{item['emoji']}`ID: {item['id']}` | {qul} | { item['name']}: {inv.count(i)}\n"
                    num += 1

                elif item['type'] == 'potion':

                    text2 = text2 + f"{item['emoji']}`ID: {item['id']}` | {qul} | { item['name']}: {inv.count(i)}\n"
                    num2 += 1

                elif item['type'] == 'food':

                    text3 = text3 + f"{item['emoji']}`ID: {item['id']}` | {qul} | { item['name']}: {inv.count(i)}\n"
                    num3 += 1

                elif item['type'] == 'pet':

                    text4 = text4 + f"{item['emoji']}`ID: {item['id']}` | {qul} | { item['name']}: {inv.count(i)}\n"
                    num4 += 1

                else:
                    text5 = text5 + f"{item['emoji']}`ID: {item['id']}` | {qul} | { item['name']}: {inv.count(i)}\n"
                    num5 += 1

                n.append(i)

        if num > 0:
            emb2.add_field(name= f"Предметы | Оружия: {num}", value= text)
        if num2 > 0:
            emb2.add_field(name= f"Предметы | Зелья: {num2}", value= text2)
        if num3 > 0:
            emb2.add_field(name= f"Предметы | Еда: {num3}", value= text3)
        if num4 > 0:
            emb2.add_field(name= f"Предметы | Питомцы: {num4}", value= text4)
        if num5 > 0:
            emb2.add_field(name= f"Предметы | Остальное: {num5}", value= text5)


        msg = await ctx.send(embed = emb)



        def check(reaction, user):
            nonlocal msg
            return user == ctx.author and str(reaction.emoji) in solutions and str(reaction.message) == str(msg)

        async def rr():
            nonlocal reaction

            if str(reaction.emoji) == '<:profile_page:780678064123412511>':
                await msg.remove_reaction('<:profile_page:780678064123412511>', ctx.author)
                await msg.edit(embed = emb)
                pass

            if str(reaction.emoji) == '<:inventory_page:781462475177721877>':
                await msg.remove_reaction('<:inventory_page:781462475177721877>', ctx.author)
                await msg.edit(embed = emb2)
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
                return
            else:
                await rr(), await reackt()

        for x in solutions:
            await msg.add_reaction(x)

        await reackt()

    @commands.command()
    async def item(self, ctx, name, arg, style, stat, emoji, quality, price, *, desc):
        global items

        creators = [323512096350535680, 308082912941572109]
        if ctx.author.id in creators:
            item = {
                "id": items.count_documents({})+1,
                "name": name,        # имя предмета
                "type": arg,         # food weapon potion recipe material armor pet accessor food-material
                "style": style,        #стиль, например фрукт, у оружий это ближний бой, дальний и тд ( close combat - ближний бой,)
                "stat": int(stat),      # урон и тд
                "emoji": emoji,
                "quality": quality,   # n u r o l качества
                "price": f"{price}",          #цена предмета, если нельзя продать то -
                "desc": desc        # текст при использовании
            }
            items.insert_one(item)
            await ctx.send("Предмет добавлен")

    @commands.command()
    async def use(self, ctx, iid):
        global players
        global items
        if players.find_one({"userid": ctx.author.id}) == None:
            await ctx.send("У вас не создан персонаж")
            return

        item = items.find_one({'id': int(iid)})
        user = players.find_one({'userid':ctx.author.id})

        inv = user['inv']

        if str(iid) in inv:
            if item['type'] == 'food' or item['type'] == 'food-material':
                players.update_one({'userid':ctx.author.id},{'$inc':{"hp": item['stat']}})
                players.update_one({'userid':ctx.author.id},{'$set':{"inv": inv}})
                await ctx.send(item['desc'])
                inv.remove(str(iid))

            elif item['type'] == 'weapon' or item['type'] == 'weapon-material':
                players.update_one({'userid':ctx.author.id},{'$inc':{"weapon": item['id']}})
                players.update_one({'userid':ctx.author.id},{'$set':{"inv": inv}})
                await ctx.send(item['desc'])
                inv.remove(str(iid))


            elif item['type'] == 'poition':
                if item['style'] == "hp":
                    players.update_one({'userid':ctx.author.id},{'$inc':{"hp": item['stat']}})
                    if hp > hpmax:
                        players.update_one({'userid':ctx.author.id},{'$inc':{"hp": item['hpmax']}})
                elif item['style'] == 'mana':
                    players.update_one({'userid':ctx.author.id},{'$inc':{"mana": item['stat']}})
                    if mana > manamax:
                        players.update_one({'userid':ctx.author.id},{'$inc':{"mana": item['manamax']}})

                players.update_one({'userid':ctx.author.id},{'$set':{"inv": inv}})
                await ctx.send(item['desc'])
                inv.remove(str(iid))

            elif item['type'] == 'material':
                await ctx.send("Вы не можите использовать этот предмет, так как он используется при крафте")

            elif item['type'] == 'recipe':
                embet = item['desc']
                emb = discord.Embed( color=0xf03e65).add_field(name = item['name'] , value = item['desc'] )
                await ctx.send(embed = emb)

            elif item['type'] == 'armor':
                players.update_one({'userid':ctx.author.id},{'$set':{"armor": item['stat']}})
                players.update_one({'userid':ctx.author.id},{'$set':{"inv": inv}})
                await ctx.send(item['desc'])
                inv.remove(str(iid))

            elif item['type'] == 'pet':
                players.update_one({'userid':ctx.author.id},{'$set':{"pet": item['stat']}})        #оздать отдельную таблицу с питомцами, а в stat удет указываться id из той таблицы
                players.update_one({'userid':ctx.author.id},{'$set':{"inv": inv}})
                await ctx.send(item['desc'])

        else:
            await ctx.send("У вас нет этого предмета")
            return

    @commands.command()
    async def trade(self, ctx, member:discord.Member, iid:int, amout:int, count = 1):
        global players
        global items
        a = 0
        b = 0
        item = items.find_one({"id": iid})

        player = players.find_one({"userid": ctx.author.id})
        player2 = players.find_one({"userid": member.id})
        pweapon = player['weapon']
        iname = item['name']
        itype = item['type']
        inv = player['inv']
        inv2 = player2['inv']
        mon2 = player2['money']



        if players.find_one({"userid": ctx.author.id}) == None:
            await ctx.send("У вас не создан персонаж.")
            return

        if players.find_one({"userid": member.id}) == None:
            await ctx.send(f"У {member.name} не создан персонаж.")
            return

        if amout < 0:
            return

        if member == ctx.author:
            await ctx.send("Только деньги потратишь передавая самому себе.")
            return

        if iid == pweapon:
            await ctx.send('Ха ха, нельзя обменять надетое оружие.')
            return

        if mon2 < amout:
            await ctx.send(f'У {member.name} нет такой суммы на руках.')
            return

        while a !=int(count):
            if str(iid) in inv:
                inv.remove(str(iid))
                b += 1
            a += 1


        if b != int(count):
            await ctx.send(f'У вас нет {count} `{iname}(-a)`, у вас только {b}')
            return

        am = 0
        if amout != 0:
            am = amout - amout / 100 * 20


        reaction = 'a'
        giff = random.randint(1,3)
        if giff == 1:
            gif = "https://pa1.narvii.com/5697/5b13742ef7bb2f243f232d9af50f6d6ee2e31b63_hq.gif"
            emoji = '🍵'
        if giff == 2:
            gif = "https://pa1.narvii.com/6841/7bd586049ab34895c347f97d495011f4c336fc21_hq.gif"
            emoji = '🧁'
        if giff == 3:
            gif = "https://pa1.narvii.com/5697/5b13742ef7bb2f243f232d9af50f6d6ee2e31b63_hq.gif"
            emoji = '🥙'

        if amout == 0:
            gif = "https://pa1.narvii.com/5853/cc83b1cb546f80d5cc2d4a4ca78cd613ee3a05f5_hq.gif"
            emoji = '🎁'

        emb1=discord.Embed(description = f"<@{member.id}>, <@{ctx.author.id}> меняет {count} `{iname}` на {amout} монеток", color=0xf03e65).set_footer(
        text = f'Нажми на реакцию {emoji} если да.',icon_url = member.avatar_url)

        emb2=discord.Embed(description = f"<@{ctx.author.id}> и <@{member.id}> совершили обмен!", color=0xf03e65).set_thumbnail(url = gif )
        emb3=discord.Embed(description = f"<@{member.id}> не ответил или отказал <@{ctx.author.id}>", color=0xf03e65)

        def check( reaction, user):
            nonlocal msg
            return user == member and str(reaction.emoji) == emoji and str(reaction.message) == str(msg)

        async def pt():
            await msg.edit(embed = emb3)
            return

        async def reackt(msg):
            nonlocal reaction
            await msg.add_reaction(emoji)
            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=30.0, check = check)
            except asyncio.TimeoutError:
                await pt()
            else:
                return True

        async def end():
            await msg.edit(embed = emb2)
            a = 0
            while a !=int(count):
                inv2.append(iid)
                a += 1

            players.update_one({"userid":ctx.author.id}, {"$inc":{"money":am}})
            players.update_one({"userid":member.id}, {"$inc":{"money":-amout}})

            players.update_one({"userid":ctx.author.id}, {"$set":{"inv": inv}})
            players.update_one({"userid":member.id}, {"$set":{"inv":inv2}})
            return

        msg = await ctx.send(embed = emb1)
        if await reackt(msg)== True:
            if str(reaction.emoji) == emoji:
                await end()
                return
        else:
            return

    @commands.command()
    async def rpg_hunt(self,ctx):
        global mobs
        global items
        global players
        global items
        player = players.find_one({"userid": ctx.author.id})
        weapon = items.find_one({"id": player['weapon']})
        mobs_list = []
        legg = 5

        for i in mobs.find():

            if i['lvl'] == player['lvl'] or i['lvl'] <= player['lvl'] + legg:
                mobs_list.append(f"{i['mobid']}")

        solutions = [f'{str(weapon["emoji"])}','<:run:782862284144771142>']
        reaction = 'a'
        mob = random.choice(mobs_list)
        mob = mobs.find_one({"mobid": int(mob)})
        leg = mob['up_leg']
        r = random.randint(mob['lvl'], leg['max_lvl'])
        r = leg['max_lvl']


        mhp = int(leg['leg_hp'] * r)
        mrew = leg['leg_money'] * r
        ld = leg['leg_damage'] * r
        if mob['damage'] != ld:
            mdam = random.randint(mob['damage'], ld)
        else:
            mdam = ld
        mlvl = r

        emb1 = discord.Embed(color=0xf03e65).add_field(name = 'Бой', value = f'Вы напали на {mob["emoji"]}{mob["mob_name"]}!', inline = True
        ).add_field(name=f'{mob["emoji"]}{mob["mob_name"]}', value = f'Здоровье: `{mhp}`\nУрон: `{mdam}`\nУровень: `{mlvl}` '
        ).add_field(name=f'Вы:', value = f'Здоровье: `{player["hp"]}`\nУрон: `{weapon["stat"]}`')
        emb_ = discord.Embed(color=0xf03e65).add_field(name = 'Вы покинули бой', value = f'Вы сбежали от {mob["emoji"]}{mob["mob_name"]}!', inline = True)
        emb_l = discord.Embed(color=0xf03e65).add_field(name = 'Бездействие...', value = f'Вы бездействуете и теряете {mob["emoji"]}{mob["mob_name"]} из виду!', inline = True)


        async def attack():
            nonlocal weapon
            nonlocal player
            nonlocal mob
            nonlocal mhp
            nonlocal mrew
            nonlocal mdam
            text = ''
            ar = mob['add_reward']
            rc = mob['reward_count']
            rpa = random.randint(0, weapon['stat']) #рандом урона игрока
            rma = random.randint(0, mdam) #рандом атаки моба
            rx = random.randint(0, mob["expi"])
            rr = random.randint(mob["reward_money"] / 100 * 20, mob["reward_money"])
            r3 = random.randint(1,3)
            inv = player['inv']
            if r3 == 1:
                mhp -= rpa
                tt = rpa
            elif r3 == 2:
                mhp -= round(rpa * 2)
                tt = round(rpa * 2)
            elif r3 == 3:
                mhp -= round(rpa / 100 * 0.5)
                tt = round(rpa / 100 * 0.5)
            mhp = round(mhp)


            if mhp <= 0:
                emb2 = discord.Embed(color=0xf03e65).add_field(name = f'Вы победили {mob["emoji"]}{mob["mob_name"]}',
                value = f'Награда: {rr}<:pokecoin:780356652359745537>, {rx}<:expi:782974020248272957> опыт', inline = True)
                if mob['add_reward'] != {}:
                    for i in mob['add_reward'].keys():
                        if random.randint(1, int(i)) == 1:
                            ri = items.find_one({"id": ar[f'{i}']})
                            r4 = random.randint(1, rc[f'{i}'])
                            text = text + f"{ri['emoji']}{ri['name']} x{r4}"
                            a = 0
                            while a != r4:
                                a += 1
                                inv.append(int(ri['id']))

                if text != '':
                    emb2.add_field(name=f'Предметы:', value = f'{text}' )
                    players.update_one({'userid':ctx.author.id},{'$set':{"inv": inv}})

                await msg.edit(embed = emb2)
                await msg.clear_reactions()
                expn = 5 * player['lvl'] * player['lvl'] + 50 * player['lvl'] + 100
                players.update_one({'userid':ctx.author.id},{'$inc':{"coins": rr}})

                if player['xp'] + rx >= expn:
                    players.update_one({'userid':ctx.author.id},{'$set':{"xp": 0}})
                    players.update_one({'userid':ctx.author.id},{'$inc':{"lvl": 1}})
                else:
                    players.update_one({'userid':ctx.author.id},{'$inc':{"xp": rx}})

                players.update_one({'userid':ctx.author.id},{'$set':{"hp": player['hp']}})


                return

            player['hp'] -= rma

            if player['hp'] <= 0:
                await msg.clear_reactions()
                emb4 = discord.Embed(color=0xf03e65).add_field(name = f'Вы погибли от {mob["emoji"]}{mob["mob_name"]}',
                value = f'Вы потеряли: 80%<:pokecoin:780356652359745537>, теперь ваш уровень: 1', inline = True)
                await msg.edit(embed = emb4)

                players.update_one({'userid':ctx.author.id},{'$set':{"lvl": 1}})
                players.update_one({'userid':ctx.author.id},{'$set':{"xp": 0}})
                players.update_one({'userid':ctx.author.id},{'$set':{"coins": int(player['coins'] / 100 * 20)}})
                players.update_one({'userid':ctx.author.id},{'$set':{"hp": 0}})

                return
            else:
                emb3 = discord.Embed(color=0xf03e65).add_field(name = 'Бой',
                value = f'Вы ведёте бой с {mob["emoji"]}{mob["mob_name"]}!\nВы нанесли: `{tt}`\n{mob["emoji"]} наносит: `{rma}`', inline = True
                ).add_field(name=f'{mob["emoji"]}', value = f'Здоровье: `{mhp}`\nУрон: `{mdam}`\nУровень: `{mlvl}` '
                ).add_field(name=f'Вы:', value = f'Здоровье: `{player["hp"]}`\nУрон: `{weapon["stat"]}`')
                await msg.edit(embed = emb3)
                await reackt()





        def check( reaction, user):
            nonlocal msg
            return user == ctx.author and str(reaction.emoji) in solutions and str(reaction.message) == str(msg)

        async def reackt():
            nonlocal reaction
            nonlocal player
            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check = check)
            except asyncio.TimeoutError:
                await msg.clear_reactions()
                await msg.edit(embed = emb_l)
                players.update_one({'userid':ctx.author.id},{'$set':{"hp": player['hp']}})
                return
            else:
                await rr()

        async def rr():
            nonlocal reaction
            nonlocal player

            if str(reaction.emoji) == f'{str(weapon["emoji"])}':
                await msg.remove_reaction(f'{str(weapon["emoji"])}', ctx.author)
                await attack()
                pass

            elif str(reaction.emoji) == '<:run:782862284144771142>':
                await msg.clear_reactions()
                await msg.edit(embed = emb_)
                players.update_one({'userid':ctx.author.id},{'$set':{"hp": player['hp']}})
                return


        msg = await ctx.send(embed = emb1)
        for x in solutions:
            await msg.add_reaction(x)
        await reackt()



def setup(bot):
    bot.add_cog(MainCog(bot))
