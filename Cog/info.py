import nextcord as discord
from nextcord.ext import tasks, commands
import sys
import random
from random import choice
import asyncio
import time
import pymongo
import requests
from datetime import datetime, timedelta, timezone


sys.path.append("..")
from functions import functions as funs
import config

client = funs.mongo_c()
db = client.bot
servers = db.servers
settings = db.settings


class info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        global settings

    @commands.command(aliases=['bot', 'invite'], usage = '-', description = 'Информация о боте.')
    async def info(self,ctx):

        ping = self.bot.latency
        ping_emoji = "🟩🔳🔳🔳🔳"

        ping_list = [
            {"ping": 0.10000000000000000, "emoji": "🟧🟩🔳🔳🔳"},
            {"ping": 0.15000000000000000, "emoji": "🟥🟧🟩🔳🔳"},
            {"ping": 0.20000000000000000, "emoji": "🟥🟥🟧🟩🔳"},
            {"ping": 0.25000000000000000, "emoji": "🟥🟥🟥🟧🟩"},
            {"ping": 0.30000000000000000, "emoji": "🟥🟥🟥🟥🟧"},
            {"ping": 0.35000000000000000, "emoji": "🟥🟥🟥🟥🟥"}]

        for ping_one in ping_list:
            if ping > ping_one["ping"]:
                ping_emoji = ping_one["emoji"]


        s1 = self.bot.get_guild(601124004224434357)
        b = ctx.guild.me
        embed = discord.Embed(
            title="Ранга",
            description=f"Я Ранга! По велению Римуру-доно, я прибыл чтобы наблюдать за этим местом!\n\nЯ кастомный бот для [{s1}](https://discord.gg/VyDc2e4HYE)",
            color=0x34cb2c)

        embed.add_field(name="Префикс", value=f"{ctx.prefix}")
        embed.add_field(name="Разработчик", value=f"<@323512096350535680>")
        embed.add_field(name="Пинг:",value=f"{ping_emoji} `{ping * 1000:.0f}ms`")
        embed.add_field(name="Статистика:",value=f"Пользователей: {len(self.bot.users)}\nКоманд: {len(self.bot.commands)}\n", inline=True)
        embed.add_field(name="Библиотека", value="nextcord 2.0.0a6")
        embed.add_field(name="Хостинг", value="heroku")
        try:
            embed.set_thumbnail(url= b.avatar.url)
        except:
            pass
        await ctx.send(embed = embed)


    # @commands.command(aliases=['N', 'n', 'Nitro', 'нитро', "Нитро"], usage = '-', description = 'Информация о премиум подписке.')
    # async def nitro(self,ctx):
    #     global settings
    #
    #     kk = self.bot.get_emoji(778533802342875136)
    #     un = self.bot.get_emoji(778545536138608652)
    #
    #     emb = discord.Embed(title = f'{un}Информация о Котик Nitro', color=0xfe00b8)
    #     emb.add_field(name="Плюшки:", value=f"Опыт: х2\ndaily: x2\n Комиссия: Off\n Покупка всех фонов: Бесплатно\nВалюта: 10к{kk}")
    #     emb.add_field(name="Статус:", value=f"Цена: 250 руб. (rus)\nДлительность: 3 месяца")
    #     emb.add_field(name="Связь:", value=f"Покупка: {ctx.prefix}it_nitro_buy", inline = False)
    #     emb.set_thumbnail(url= 'https://ia.wampi.ru/2020/11/18/icons8-dog-paw-print-96.png')
    #     await ctx.send(embed = emb)


    @commands.command(aliases = ["юзеринфо", "юзер", "user"], usage = '(@member)', description = 'Информация о пользователе.')
    async def userinfo(self,ctx, member: discord.Member = None ):
        if member == None:
            member = ctx.author

        user = await self.bot.fetch_user(member.id)
        bd_user = funs.user_check(member, ctx.guild)
        server = servers.find_one({"server": ctx.guild.id})


        if member.nick == None:
            nick = f"**Имя**: {member.name}\n"
        else:
            nick = f"**Имя**: {member.name}\n**Никнейм**: {member.nick}\n"

        emb = discord.Embed(title="Информация о пользователе",color = member.color.value)
        emb.add_field(name="🎋 | Имя / Никнейм",
              value=f"{nick}")

        sec = int(member.joined_at.timestamp())
        emb.add_field(name="🎍 | Об аккаунте",
              value=  f"**Зашёл**: <t:{int(member.joined_at.timestamp())}> (<t:{int(member.joined_at.timestamp())}:R>)\n"
                    f"**Cоздан**:  <t:{int(member.created_at.timestamp())}> (<t:{int(member.created_at.timestamp())}:R>)\n"
                    , inline=False)

        emb.add_field(name="🎨 | Сервер",
        value= f"**Ролей**: {len(member.roles)}\n"
        f"**Высшая роль**: <@&{member.top_role.id}>\n"
        f"**Монет**: {'{:,}'.format(bd_user['money']).replace(',', '.')} <:pokecoin:780356652359745537>\n"
        f"**Уровень**: {bd_user['lvl']} <:lvl:886876034149011486>\n"
        , inline=False)

        emb.set_thumbnail(url= member.avatar.url)
        emb.set_footer(text=f"ID: {member.id}")

        act_n = []
        act_t = []
        for i in list(member.activities):
            act_n.append(i.name)
            act_t.append(type(i))

        print(act_n, '\n', act_t)

        if discord.activity.Spotify in act_t:
            s = member.activities[act_t.index(discord.activity.Spotify)]
            emb.add_field(name = f"<:spoti:935937710152089610> | Слушает **{s.title}**",
            value= f"**Артист**: {s.artist}\n"
                   f"**Автор**: {funs.time_end(int(s.duration.total_seconds()))}\n"
            , inline=True)

        if discord.activity.CustomActivity in act_t:
            s = member.activities[act_t.index(discord.activity.CustomActivity)]
            if s.name != None:
                emb.add_field(name = f"🎴 | Статус",
                value= f"{s.name}"
                , inline=True)

        if discord.activity.Streaming in act_t:
            s = member.activities[act_t.index(discord.activity.Streaming)]
            emb.add_field(name = f"🔮 | Стримит на {s.platform}",
            value= f"**Название**: [{s.name}]({s.url})\n"
             f"**Тема / Игра**: {s.game}\n"
            , inline=True)

        # print(list(member.activities))
        # print(member.raw_status)
        # print(member.status)

        if user.banner != None:
            emb.set_image(url = user.banner.url)
        await ctx.send(embed=emb)



    @commands.command(aliases=["сервер","serverinfo","server info"], usage = '-', description = 'Информация о сервере')
    async def server(self,ctx):
        server = servers.find_one({"server": ctx.guild.id})
        faa = ctx.guild.mfa_level
        if faa == 1:
            msg = "Включён"
        if faa == 0:
            msg = "Выключен"
        allu = self.bot.get_emoji(737350813386539014)
        bans = self.bot.get_emoji(737350831329902622)
        allc = self.bot.get_emoji(737350902729670688)
        cat = self.bot.get_emoji(737350924128878601)
        channels = self.bot.get_emoji(737350940117434389)
        voices = self.bot.get_emoji(737350952100560927)
        fa = self.bot.get_emoji(737350963047694416)
        boost = self.bot.get_emoji(737350974972100688)
        image = self.bot.get_emoji(737350989421740042)
        roles = self.bot.get_emoji(737351006425317439)
        owner = self.bot.get_emoji(737351022477049886)
        bott = self.bot.get_emoji(737364903370948608)
        uss = self.bot.get_emoji(737370245290786866)
        ms = []
        for i in ctx.guild.members:
            if i.bot:
                ms.append(1)

        us = int(ctx.guild.member_count) - int(ms.count(1))
        emb = discord.Embed(title="Информация о сервере "+ctx.guild.name, color=server['embed_color'])
        emb.add_field(name="Участники:",value=
                                            f"{allu}Всех - {int(ctx.guild.member_count)}\n"
                                            f"{uss}Пользователей - {us}\n"
                                            f"{bott}Ботов - {ms.count(1)}\n"
                                            f"{bans}Баны - {len(await ctx.guild.bans())}\n",
                                            inline=True)

        emb.add_field(name="Статус буста:",value=f"{boost}Бусты - {ctx.guild.premium_subscription_count}\n{boost}Уровень - {ctx.guild.premium_tier}",inline=False)

        emb.add_field(name="Каналы:",value=
                                            f"{allc}Всего - {len(ctx.guild.channels)}\n"
                                            f"{cat}Категории - {len(ctx.guild.categories)}\n"
                                            f"{channels}Текстовых каналов - {len(ctx.guild.text_channels)}\n"
                                            f"{voices}Голосовых каналов - {len(ctx.guild.voice_channels)}",
                                            inline=False)

        emb.add_field(name="Сервер:",value=
                                            f"{fa}2FA - "+msg+"\n"
                                            f"{image}Эмоджи - {len(await ctx.guild.fetch_emojis())}\n"
                                            f"{roles}Роли - {len(ctx.guild.roles)}\n",
                                            inline=True)

        emb.add_field(name="Создатель:",value=
                                            f"{owner}<@{ctx.guild.owner_id}>",
                                            inline=True)

        emb.add_field(name="Регион:",value=
                                            f"{ctx.guild.region}",
                                            inline=True)

        emb.add_field(name="Создан:",value=
                                            f"{ctx.guild.created_at.strftime('%X, %d %B, %Y')}",
                                            inline=True)

        emb.add_field(name="ID:",value=
                                        f"{ctx.guild.id}",
                                        inline=True)

        emb.set_thumbnail(url= ctx.guild.icon.url)
        await ctx.send(embed=emb)

    @commands.command(aliases = ['автар', 'аватарка'], usage = '(@member)', description = 'Аватарка пользователя.')
    async def avatar(self, ctx, member: discord.Member = None):
        server = servers.find_one({"server": ctx.guild.id})
        if member == None:
            member = ctx.author
        emb = discord.Embed(description = f'[Аватарка]({member.avatar.url}) {member.name}',color=server['embed_color'])
        emb.set_image(url = member.avatar.url)
        await ctx.send(embed = emb)

    @commands.command(usage = '(:emoji:)', description = 'Информация о эмоджи.')
    async def emoji(self, ctx, emoji: discord.Emoji):
        server = servers.find_one({"server": ctx.guild.id})
        emb = discord.Embed(title = f'Эмоджи: {emoji.name}',color=server['embed_color'])
        emb.set_image(url = emoji.url)
        await ctx.send(embed = emb)

    @commands.command(aliases = ['m'], usage = '(message_id)', description = 'Информация о сооб')
    async def message(self, ctx, mid:int):
        server = servers.find_one({"server": ctx.guild.id})
        try:
            mid = await ctx.channel.fetch_message(mid)
        except Exception:
            await ctx.send('Сообщение не найдено')

        emb = discord.Embed(title="Инфоромация о сообщении",
        description = f"Id: {mid.id} Ссылка: [Жмяк](https://discord.com/channels/{ctx.guild.id}/{ctx.channel.id}/{mid.id})\nАвтор: {mid.author.mention} id автора: {mid.author.id}",
        color=server['embed_color'])
        await ctx.send(embed = emb)

    # @commands.command(usage = '-', description = 'Покупка премиум подписки.')
    # async def it_nitro_buy(self, ctx):
    #     server = servers.find_one({"server": ctx.guild.id})
    #     us = funs.user_check(ctx.author, ctx.author.guild)
    #
    #     emb = discord.Embed(
    #         title="Информация о покупке IT Nitro",
    #         description = f'Для покпки подписки:\n1. Вызовите эту команду\n2. Перейдите на сайт [Клик](https://new.donatepay.ru/@811772)\nВ поле "Ваше имя" введите свой id `( {ctx.author.id} )`\n3. В поле "Сумма пожертвования" введите минимум 250 и укажите валюту "RUB"\n4. Ожидайте в течении 10 минут.\n\nЕсли It Nitro не было получено в течении 10 минут свяжитесь с разработчиком `💧Римуру-самаˢˡⁱᵐᵉ ᵃʷ#6228`',
    #         color = server['embed_color'])
    #
    #     await ctx.send(embed = emb)
    #
    #     await asyncio.sleep(600)
    #     r = requests.get('https://donatepay.ru/api/v1/transactions', params={'access_token': config.donatepay_token, 'status': 'success'})
    #
    #     for i in r.json()['data']:
    #         if i['created_at'][0:10] == str(time.strftime('%Y-%m-%d')):
    #             if i['comment'] == str(ctx.author.id):
    #                 if int(i['sum']) >= 250:
    #                     await ctx.send('Вам было выданно IT Nitro!')
    #
    #                     funs.user_update(ctx.author.id, ctx.author.guild, 'Nitro', True)
    #                     funs.user_update(ctx.author.id, ctx.author.guild, 'money', us + 10000)
    #                     break
    #                 else:
    #                     await ctx.send('Сумма меньше 250-ти рублей!')

def setup(bot):
    bot.add_cog(info(bot))
