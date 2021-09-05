import nextcord as discord
from nextcord.ext import tasks, commands
import sys
import random
from random import choice
import asyncio
import time
import datetime
import pymongo

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


class mod(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(usage = '(@member) [reason]', description = 'Забанить пользователя.', help = 'Модерация', aliases = ['бан'])
    async def ban(self, ctx, member: discord.Member, *, arg="Причина не указана"):
        if funs.roles_check(ctx.author, ctx.guild.id) == False:
            await ctx.send("У вас недостаточно прав для использования этой команды!")
            return

        if ctx.author.guild_permissions.ban_members == True:
            await member.send(f'Вы были забанены на сервере `{ctx.guild.name}` по причине: `{arg}`\nСоздатель сервера: `{ctx.guild.owner}`')

        ban = f"{ctx.author}({ctx.author.id}) - {arg}"
        await member.ban(reason=ban)
        msg = [
            "Забаненый уже никогда не будет тем, кто был раньше...",
            "Бан это и плохо и хорошо, смотря с какой стороны смотреть...",
            "Тот ли человек после бана кем он был раньше?",
        ]
        server = servers.find_one({"server": ctx.guild.id})
        message = await ctx.send(embed = discord.Embed(color=server['embed_color']).add_field(
            name="Бан",
            value=f"Забанен: {member.mention}\n"
            f"Забанил: {ctx.author.mention}\n"
            f"Причина: {arg}\n"
            f"Банов: {int(len(await ctx.guild.bans()))-1} +1"
            ).set_thumbnail(
            url= "https://ia.wampi.ru/2020/08/09/1452967606_anime-sword-art-online-lisbeth-anime-gifki-2775271.gif").set_footer(
            icon_url=ctx.author.avatar.url,
            text=random.choice(msg)))

    @commands.command(usage = '(member_id)', description = 'Разбанить пользователя на сервере.', help = 'Модерация', aliases = ['разбанить'])
    async def unban(self, ctx, member_id:int):
        user = await self.bot.fetch_user(member_id)
        await ctx.guild.unban(user)
        await user.send(f'Вы были разбанены на сервере `{ctx.guild.name}`\nСоздатель сервера: `{ctx.guild.owner}`')
        await ctx.send(f"Пользователь {user} был разбанен.")

    @commands.command(usage = '(@member) [reason]', description = 'Кикнуть пользователя.', help = 'Модерация', aliases = ['кик'])
    async def kick(self, ctx, member: discord.Member, arg="Причина не указана"):
        if funs.roles_check(ctx.author, ctx.guild.id) == False:
            await ctx.send("У вас недостаточно прав для использования этой команды!")
            return

        if ctx.author.guild_permissions.kick_members == True:
            await member.send(f'Вы были выгнаны с сервере `{ctx.guild.name}` по причине: `{arg}`\nСоздатель сервера: `{ctx.guild.owner}`')

        k = f"{ctx.author}({ctx.author.id}) - {arg}"
        await member.kick(reason=k)
        server = servers.find_one({"server": ctx.guild.id})
        message = await ctx.send(embed = discord.Embed(color=server['embed_color']).add_field(
            name="Кик",
            value=f"Кикнут: {member.mention}\n"
            f"Кикнул: {ctx.author.mention}\n"
            f"Причина: {arg}\n"
            ).set_thumbnail(
            url= "https://pa1.narvii.com/6392/9b4dd5ba812d32198cbd5465e0d10b46153c2208_hq.gif"))

    @commands.command(usage = '-', description = 'Задержка бота.', help = 'Бот', aliases = ['пинг'])
    async def ping(self, ctx):
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

        message = await ctx.send("Пожалуйста, подождите. . .")
        await message.edit(content = f"Понг! {ping_emoji} `{ping * 1000:.0f}ms` :ping_pong:")

    @commands.command(aliases = ['complaint', "репорт", "жалоба"], usage = '(message)', description = 'Отправить жалобу на баг бота.', help = 'Бот')
    async def report(self,ctx, *, complaint):
        global settings
        s = settings.find_one({"sid": 1})

        if ctx.author.id in s['black list']:
            return

        await ctx.channel.purge(limit = 1)
        channel = self.bot.get_channel(792710440693137438)
        files = []
        link = await ctx.channel.create_invite(max_age = 0)
        server = servers.find_one({"server": ctx.guild.id})
        emb=discord.Embed(title="Баг/жалоба",
            colour=server['embed_color']).add_field(name='Данные',
            value=f"Имя: {ctx.author.name}\n"
            f"ID: {ctx.author.id}\n"
            f"Имя сервера: {ctx.guild.name}"
            ).add_field(name='Приглашение на сервер',
            value= f"[Инвайт]({link})").add_field(name="Проблемма",
            value=f"{complaint}", inline=False)

        await channel.send(embed=emb)
        await ctx.send("Ваша жалоба отправлена!")

    @commands.command(usage = '(@member) (time) [reason]', description = 'Замьютить пользователя на сервере.', help = 'Мьюты', aliases = ['мьют'])
    async def mute(self, ctx, member: discord.Member = None, timem = None, *, reason = None):
        if funs.roles_check(ctx.author, ctx.guild.id) == False:
            await ctx.send("У вас недостаточно прав для использования этой команды!")
            return

        server = servers.find_one({"server": ctx.guild.id})
        if member is None:
            await ctx.send("Вы не указали пользователя!")
        elif timem is None:
            await ctx.send("Вы не указали время!\nФормат: 10m (s/m/h/d)")

        elif server['mod']['muterole'] is None:
            await ctx.send(f"Роль мьюта не настроена на этом сервере!")

        else:
            if member.id == ctx.guild.owner.id:
                return

            role = discord.utils.get(ctx.guild.roles, id = server['mod']['muterole']) #id роли
            await member.add_roles(role)

            if timem.endswith("s"):
                a = server['mute_members'].copy()
                a.update({str(member.id): time.time() + int(timem[:-1]) })
                servers.update_one({"server": ctx.guild.id}, {"$set": {"mute_members": a}})
                times = funs.time_end(int(timem[:-1]))
                embs = discord.Embed(title = "Мьют", description = f"Пользователю {member.name}, был выдан мьют на {times}\nПричина: {reason}", color=server['embed_color'])
                await ctx.send(embed = embs)

            elif timem.endswith("m"):
                a = server['mute_members'].copy()
                a.update({str(member.id): time.time() + int(timem[:-1])*60 })
                servers.update_one({"server": ctx.guild.id}, {"$set": {"mute_members": a}})
                times = funs.time_end(int(timem[:-1])*60)
                embm = discord.Embed(title = "Мьют", description = f"Пользователю {member.name}, был выдан мьют на {times}\n\n**Причина: {reason}**", color=server['embed_color'])
                await ctx.send(embed = embm)

            elif timem.endswith("h"):
                a = server['mute_members'].copy()
                a.update({str(member.id): time.time() + int(timem[:-1])*3600 })
                servers.update_one({"server": ctx.guild.id}, {"$set": {"mute_members": a}})
                times = funs.time_end(int(timem[:-1])*3600)
                embh = discord.Embed(title = "Мьют", description = f"Пользователю {member.name}, был выдан мьют на {times}\n\n**Причина: {reason}**", color=server['embed_color'])
                await ctx.send(embed = embh)

            elif timem.endswith("d"):
                a = server['mute_members'].copy()
                a.update({str(member.id): time.time() + int(timem[:-1])*86400 })
                servers.update_one({"server": ctx.guild.id}, {"$set": {"mute_members": a}})
                times = funs.time_end(int(timem[:-1])*86400)
                embd = discord.Embed(title = "Мьют", description = f"Пользователю {member.name}, был выдан мьют на {times}\n\n**Причина: {reason}**", color=server['embed_color'])
                await ctx.send(embed = embd)
            else:
                await ctx.send('Ошибка указания времени.')
                return


    @commands.command(usage = '(@member) [reason]', description = 'Выдать варн пользователю.', help = 'Варны', aliases = ['варн'])
    async def warn(self, ctx, user:discord.Member, *,reason = None):
        if funs.roles_check(ctx.author, ctx.guild.id) == False:
            await ctx.send("У вас недостаточно прав для использования этой команды!")
            return

        await funs.warn(ctx, user, reason, ctx.author)

    @commands.command(usage = '(@member)', description = 'Просмотреть варны пользователя.', help = 'Варны', aliases = ['варны'])
    async def warns(self, ctx, user:discord.Member = None):
        if user == None:
            user = ctx.author
        server = servers.find_one({'server':ctx.guild.id})
        text = ""
        if user == None:
            await ctx.send("Вы не указали пользователя")
            return
        try:
            print(server['mod']['warns'][str(user.id)].items())
        except Exception:
            embd = discord.Embed(title = f"Варны: {user.name}", description = f"Варны отсутсвуют", color=server['embed_color'])
            await ctx.send(embed = embd)
            return
        else:
            for i in server['mod']['warns'][str(user.id)].items():
                if i[1]['reason'] == None:
                    reason = "Не указано"
                else:
                    reason = i[1]['reason']
                text = text + f"**#{i[0]}** **{i[1]['time']}: **{reason}\nВыдал: <@{i[1]['author']}>\n\n"
            embd = discord.Embed(title = f"Варны: {user.name}", description = f"{text}", color=server['embed_color'])

            await ctx.send(embed = embd)

    @commands.command(usage = '(@member) [warn_id]', description = 'Снять варн с пользователя.', help = 'Варны', aliases = ['разварнить'])
    async def unwarn(self, ctx, member:discord.Member, num:int = 1):
        if funs.roles_check(ctx.author, ctx.guild.id) == False:
            await ctx.send("У вас недостаточно прав для использования этой команды!")
            return
        server = servers.find_one({'server':ctx.guild.id})

        try:
            server['mod']['warns'][str(member.id)]
        except Exception:
            await ctx.send("У этого пользователя нету такого варна.")
            return

        w = server['mod']['warns']
        w.copy()
        try:
            w[str(member.id)].pop(str(num))
            servers.update_one({"server": ctx.guild.id}, {"$set": {'mod': w}})
        except Exception:
            await ctx.send(f"У данного пользователя нет варна #{num}")
            return

        embd = discord.Embed(title = "Сброс", description = f"Варн #{num}, пользователя {member.mention} был сброшен", color=server['embed_color'])
        await ctx.send(embed = embd)

    @commands.command(usage = '(@member)', description = 'Размьютить пользователя.', help = 'Мьюты', aliases = ['размьютить'])
    async def unmute(self, ctx, member:discord.Member):
        if funs.roles_check(ctx.author, ctx.guild.id) == False:
            await ctx.send("У вас недостаточно прав для использования этой команды!")
            return
        server = servers.find_one({'server':ctx.guild.id})
        try:
            server['mute_members'][str(member.id)]
        except Exception:
            await ctx.send("Этот пользователь не в мьюте.")
            return

        a = server['mute_members'].copy()
        a.pop(str(member.id))
        servers.update_one({'server':server['server']},{'$set': {'mute_members':a}})

        try:
            await self.bot.get_guild(ctx.guild.id).get_member(member.id).remove_roles(self.bot.get_guild(ctx.guild.id).get_role(server['mod']['muterole']))
        except Exception:
            await ctx.send("У бота не достаточно прав на снятие или роль мьюта сброшена")
            return

        embd = discord.Embed(title = "Сброс", description = f"Мьют с пользователя {member.mention} был снят.", color=server['embed_color'])
        await ctx.send(embed = embd)


    @commands.command(usage = '-', description = 'Просмотреть всех замьюченых пользователей.', help = 'Мьюты', aliases = ['мьюты'])
    async def mutes(self,ctx):
        server = servers.find_one({'server':ctx.guild.id})
        text = ''
        for memid in server['mute_members']:
            try:
                member = ctx.guild.get_member(int(memid))
                text = text + f"{member.mention}, осталось: {funs.time_end(server['mute_members'][str(memid)]-time.time())}\n"
            except Exception:
                a = server['mute_members'].copy()
                a.pop(memid)
                servers.update_one({'server':server['server']},{'$set':{'mute_members':a}})

        await ctx.send(embed = discord.Embed(title="Мьюты", description=text, color=server['embed_color']))

    @commands.command(usage = '(number max100)', description = 'Очистить чат.', help = 'Модерация', aliases = ['очистить'])
    async def clear(self, ctx, number:int):
        if funs.roles_check(ctx.author, ctx.guild.id) == False:
            await ctx.send("У вас недостаточно прав для использования этой команды!")
            return
        if number <= 100:
            deleted = await ctx.channel.purge(limit=number)
            message = await ctx.send('Удалено {} сообщений(я)'.format(len(deleted)))
            await asyncio.sleep(3)
            await message.delete()
        else:
            await ctx.send('Не возможно удалить более 100-та сообщений за раз!')

    @commands.command(hidden=True)
    async def global_warn(self,ctx, id:int, *, reason:str = "None"):
        s = settings.find_one({"sid": 1})
        if ctx.author.id not in s['moderators']:
            await ctx.send("У вас нет прав модератора бота!")
            return

        try:
            s['bl global chat'][str(id)]
            nw = len(s['bl global chat'][str(id)].keys())
            if nw < 3:
                s['bl global chat'][str(id)].update({str(nw+1):{'reason':reason,"time":time.time() + 2628000}})
                settings.update_one({"sid": 1},{'$set': {'bl global chat':s['bl global chat']}})
                await ctx.send(f"Пользователь c id `{id}` получил варн #{nw+1}")
            else:
                s['bl global chat'][str(id)].update({'ban':f'{reason} | auto ban due to 3 warns'})
                settings.update_one({"sid": 1},{'$set': {'bl global chat':s['bl global chat']}})
                await ctx.send(f"Пользователь c id `{id}` был автоматически забанен за х3 предупреждения")

        except Exception:
            s['bl global chat'].update({str(id):{'1':{'reason':reason,"time":time.time() + 2628000}}})
            settings.update_one({"sid": 1},{'$set': {'bl global chat':s['bl global chat']}})
            await ctx.send(f"Пользователь c id `{id}` получил варн #1")

    @commands.command(hidden=True)
    async def global_ban(self,ctx, id:int, *, reason:str = "None"):
        s = settings.find_one({"sid": 1})
        if ctx.author.id not in s['moderators']:
            await ctx.send("У вас нет прав модератора бота!")
            return

        try:
            s['bl global chat'][str(id)].update({'ban':f'ban: {reason}'})
        except Exception:
            s['bl global chat'].update({str(id):{} })
            s['bl global chat'][str(id)].update({'ban':f'ban: {reason}'})

        settings.update_one({"sid": 1},{'$set': {'bl global chat':s['bl global chat']}})
        await ctx.send(f"Пользователь c id `{id}` был забанен в межсерверном чате.")

    @commands.command(usage = '[#channel]', description = 'Очистить голос. канал\каналы от пользователей.', help = 'Модерация', aliases = ['очистить_войс'])
    async def voice_clean(self, ctx, channel:discord.VoiceChannel = None):
        if funs.roles_check(ctx.author, ctx.guild.id) == False:
            await ctx.send("У вас недостаточно прав для использования этой команды!")
            return

        if channel != None:
            for i in channel.members:
                await i.move_to(channel=None)
            await ctx.send("Голосовой канал был очищен от пользователей!")

        else:
            ch = []
            for i in ctx.guild.channels:
                if type(i) == discord.channel.VoiceChannel:
                    if len(i.members) > 0:
                        ch.append(i)

            for c in ch:
                for i in c.members:
                    await i.move_to(channel=None)

            await ctx.send("Голосовой канал был очищен от пользователей!")



def setup(bot):
    bot.add_cog(mod(bot))
