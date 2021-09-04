import nextcord as discord
from nextcord.ext import tasks, commands
import random
from random import choice
import asyncio
import time
import sys
import pymongo

sys.path.append("..")
from ai3 import functions as funs
import config

client = pymongo.MongoClient(config.cluster_token)
db = client.bot
servers = db.servers


class reactions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(usage = '[@member]', description = 'Реакция суицид.', aliases = ['суицид'], help = 'Грустные')
    async def suicide(self, ctx,member:discord.Member = None):

        server = servers.find_one({"server": ctx.guild.id})

        try:
            await ctx.channel.purge(limit = 1)
        except Exception:
           pass
        if member == ctx.author:
            msg = f'**<@{ctx.author.id}>** совершил(а) суицид'
        elif member == None:
            msg = f'**<@{ctx.author.id}>** совершил(а) суицид'
        else:
            msg = f'**<@{ctx.author.id}>** совершил(а) суицид из-за **<@{member.id}>**'

        emb=discord.Embed(description = str(msg), color = server['embed_color'])
        giff = random.randint(1,4)
        if giff == 1:
            gif = "https://i.gifer.com/DpQV.gif"
        if giff == 2:
            gif = "https://pa1.narvii.com/6843/d7015105f2d207190ed5cdd9be1e63fa5d86476e_hq.gif"
        if giff == 3:
            gif = "https://pa1.narvii.com/6919/920cff9e6642eca82f8a0e5529b9b428241981c6r1-500-299_hq.gif"
        if giff == 4:
            gif = "https://i.gifer.com/UYOF.gif"
        emb.set_image(url = gif )
        await ctx.send(embed=emb)

    @commands.command(usage = '[@member]', description = 'Реакция погладить.', aliases = ['погладить'], help = 'Милые')
    async def pat(self, ctx, member:discord.Member = None):
        server = servers.find_one({"server": ctx.guild.id})
        try:
            await ctx.channel.purge(limit = 1)
        except Exception:
           pass
        if member == ctx.author:
            msg = f'**<@{ctx.author.id}>** погладил(а) самого себя, вот чсв....'
        elif member == None:
            msg = f'**<@{ctx.author.id}>** погладил(а) <@734730292484505631>'
        else:
            msg = f'**<@{ctx.author.id}>** погладил(а) **<@{member.id}>**'
        emb=discord.Embed(description = str(msg), color=server['embed_color'])
        giff = random.randint(1,9)
        if giff == 1:
            gif = "https://static.grouple.co/uploads/pics/10/83/525_o.gif"
        if giff == 2:
            gif = "https://pa1.narvii.com/6607/1f16bfa7ba7763602c172cfef17510ec863872a0_hq.gif"
        if giff == 3:
            gif = "https://data.whicdn.com/images/116773791/original.gif"
        if giff == 4:
            gif = "https://animegif.ru/up/photos/album/oct17/171021_210.gif"
        if giff == 5:
            gif = "https://i.gifer.com/78D.gif"
        if giff == 6:
            gif = "https://tenor.com/view/peachcat-cuddle-hug-back-hug-love-gif-14541113"
        if giff == 7:
            gif = "https://media.tenor.com/images/a671268253717ff877474fd019ef73e9/tenor.gif"
        if giff == 8:
            gif = "https://i.pinimg.com/originals/e3/e2/58/e3e2588fbae9422f2bd4813c324b1298.gif"
        if giff == 9:
            gif = "https://i.gifer.com/embedded/download/8jQj.gif"

        emb.set_image(url = gif )
        await ctx.send(embed=emb)

    @commands.command(usage = '[@member]', description = 'Реакция поцеловать.', aliases = ['поцеловать'], help = 'Любовные')
    async def kiss(self, ctx, member:discord.Member = None):
        try:
            await ctx.dele
        except Exception:
           pass
        if member == ctx.author:
            msg = f'**<@{ctx.author.id}>** поцеловал(а) самого себя, без комментариев'
        elif member == None:
            msg = f'**<@{ctx.author.id}>** поцеловал(а) <@734730292484505631>'
        else:
            msg = f'**<@{ctx.author.id}>** поцеловал(а) **<@{member.id}>**'

        server = servers.find_one({"server": ctx.guild.id})
        emb=discord.Embed(description = str(msg), color=server['embed_color'])
        giff = random.randint(1,8)
        if giff == 1:
            gif = "https://i.pinimg.com/originals/6b/8a/4d/6b8a4d963f5221df1bf6eb22cd5fe1a4.gif"
        if giff == 2:
            gif = "https://giffiles.alphacoders.com/131/131257.gif"
        if giff == 3:
            gif = "https://giffiles.alphacoders.com/131/131257.gif"
        if giff == 4:
            gif = "https://i.pinimg.com/originals/58/2e/31/582e311043fb847a9a2dd1d6548ab766.gif"
        if giff == 5:
            gif = "https://www.booksie.com/uploads/userfiles/6742/images/fe7582e99876519a286ccc73252ac8b0.gif"
        if giff == 6:
            gif = "https://data.whicdn.com/images/294084710/original.gif"
        if giff == 7:
            gif = "https://i2.wp.com/kawaii2ch.com/wp-content/uploads/2019/03/L1sv3xk.gif?fit=400%2C225f"
        if giff == 8:
            gif = "https://lifeo.ru/wp-content/uploads/gif-anime-kisses-48.gif"

        emb.set_image(url = gif )
        await ctx.send(embed=emb)

    @commands.command(usage = '[@member]', description = 'Реакция сделать кусь.', aliases = ['кусь', 'укусить'], help = 'Агрессивные')
    async def bite(self, ctx, member:discord.Member = None):
        try:
            await ctx.channel.purge(limit = 1)
        except Exception:
           pass
        if member == ctx.author:
            msg = f'**<@{ctx.author.id}>** сделал(а) кусь самому (самой) себя(e), без комментариев'
        elif member == None:
            msg = f'**<@{ctx.author.id}>** сделал(а) кусь самому (самой) себя(e), без комментариев'
        else:
            msg = f'**<@{ctx.author.id}>** сделал(а) кусь **<@{member.id}>**'

        server = servers.find_one({"server": ctx.guild.id})
        emb=discord.Embed(description = str(msg), color=server['embed_color'])
        giff = random.randint(1,9)
        if giff == 1:
            gif = "https://pa1.narvii.com/6930/5a613b4a946232707c5a4775d8aa9166fcf82a90r1-540-309_hq.gif"
        if giff == 2:
            gif = "https://pa1.narvii.com/6930/639c95b3a42222dd30e83977a5ee2b69652b3afbr1-600-340_hq.gif"
        if giff == 3:
            gif = "https://pa1.narvii.com/6930/be7e84430d835e27f3990cd47063ee51b30d3ffer1-499-281_hq.gif"
        if giff == 4:
            gif = "https://pa1.narvii.com/6331/ae361000cc331d13b29110b407a69bf9ddb9f44e_hq.gif"
        if giff == 5:
            gif = "https://i.gifer.com/9fjL.gif"
        if giff == 6:
            gif = "https://pa1.narvii.com/6908/f2c102ac7f48f9bec59b86f27dffa13a144a601er1-420-240_hq.gif"
        if giff == 7:
            gif = "https://i.pinimg.com/originals/c0/b4/a9/c0b4a94993a08d1df826e27e55dd2fb0.gif"
        if giff == 8:
            gif = "https://img-s1.onedio.com/id-586442b636c2c8871dbaa978/rev-0/raw/s-292dc47640dde020472cac90785b140dbbd90553.gif"
        if giff == 9:
            gif = "https://cdn.discordapp.com/attachments/604631379497713665/736236186246578296/c00c7d5bf26a8c016e3848cb936739f17a390efe_hq.gif"

        emb.set_image(url = gif )
        await ctx.send(embed=emb)

    @commands.command(usage = '[@member]', description = 'Реакция плакать.', aliases = ['плакать'], help = 'Грустные')
    async def cry(self, ctx, member:discord.Member = None):
        try:
            await ctx.channel.purge(limit = 1)
        except Exception:
           pass
        if member == ctx.author:
            msg = f'**<@{ctx.author.id}>** расплакался(ась)'
        elif member == None:
            msg = f'**<@{ctx.author.id}>** расплакался(ась)'
        else:
            msg = f'**<@{ctx.author.id}>** расплакался(ась) из-за **<@{member.id}>**'

        server = servers.find_one({"server": ctx.guild.id})
        emb=discord.Embed(description = str(msg), color=server['embed_color'])
        giff = random.randint(1,5)
        if giff == 1:
            gif = "https://cdn.discordapp.com/attachments/707663547928412250/736977136338075729/tenor.gif"
        if giff == 2:
            gif = "https://cdn.discordapp.com/attachments/707663547928412250/736977152456786050/orig.gif"
        if giff == 3:
            gif = "https://cdn.discordapp.com/attachments/707663547928412250/736977223495581777/tenor.gif"
        if giff == 4:
            gif = "https://cdn.discordapp.com/attachments/707663547928412250/736977356501286943/orig.gif"
        if giff == 5:
            gif = "https://i.pinimg.com/originals/74/d2/33/74d233d1a21abdcd0f59a3cb427d8c6c.gif"
        emb.set_image(url = gif )
        await ctx.send(embed=emb)

    @commands.command(usage = '[@member]', description = 'Реакция обнять.', aliases = ['обнять'], help = 'Милые')
    async def hug(self, ctx, member:discord.Member = None):
        try:
            await ctx.channel.purge(limit = 1)
        except Exception:
           pass
        if member == ctx.author:
            msg = f'**<@{ctx.author.id}>** обнял(а) котика'
        elif member == None:
            msg = f'**<@{ctx.author.id}>** обнял(а) <@734730292484505631>'
        else:
            msg = f'**<@{ctx.author.id}>** обнял(а) **<@{member.id}>**'

        server = servers.find_one({"server": ctx.guild.id})
        emb=discord.Embed(description = str(msg), color=server['embed_color'])
        giff = random.randint(1,5)
        if giff == 1:
            gif = "https://otvet.imgsmail.ru/download/67207789_49d3635feb46fda3a1c51fc0eb0800a9_800.gif"
        if giff == 2:
            gif = "https://anime-chan.me/uploads/posts/2016-07/1468759968_tumblr_oadopsQjh91v09euno1_540.gif"
        if giff == 3:
            gif = "http://pa1.narvii.com/6502/63f0a31cc78f6663ef8d0e194e40da0fba83a782_00.gif"
        if giff == 4:
            gif = "https://img1.ak.crunchyroll.com/i/spire4/a35d8d2ca642fde2c5cdcb3bcf3f57941484469595_full.gif"
        if giff == 5:
            gif = "https://i.gifer.com/3Ypn.gif"
        emb.set_image(url = gif )
        await ctx.send(embed=emb)

    @commands.command(usage = '[@member]', description = 'Реакция убить.', aliases = ['убить'], help = 'Агрессивные')
    async def kill(self, ctx, member:discord.Member = None):
        try:
            await ctx.channel.purge(limit = 1)
        except Exception:
           pass
        if member == ctx.author:
            msg = f'**<@{ctx.author.id}>** убил(а) себя'
        elif member == None:
            msg = f'**<@{ctx.author.id}>** убил(а) <@734730292484505631>😭'
        else:
            msg = f'**<@{ctx.author.id}>** убил(а) **<@{member.id}>**'

        server = servers.find_one({"server": ctx.guild.id})
        emb=discord.Embed(description = str(msg), color=server['embed_color'])
        giff = random.randint(1,5)
        if giff == 1:
            gif = "https://pa1.narvii.com/6550/6db2f0bd45340e49c3dc7dc0d8a21b239855f978_hq.gif"
        if giff == 2:
            gif = "https://i.gifer.com/embedded/download/DTBu.gif"
        if giff == 3:
            gif = "https://i.gifer.com/BzlD.gif"
        if giff == 4:
            gif = "https://pa1.narvii.com/6234/8e7ec2b3858123190128f3474b616ef5b3b9d6f2_hq.gif"
        if giff == 5:
            gif = "https://i.pinimg.com/originals/43/d9/1a/43d91af64d4830fc9d92e8fd2ea31c97.gif"
        emb.set_image(url = gif )
        await ctx.send(embed=emb)

    @commands.command(usage = '[@member]', description = 'Реакция ударить.', aliases = ['ударить'], help = 'Агрессивные')
    async def punch(self, ctx, member:discord.Member = None):
        try:
            await ctx.channel.purge(limit = 1)
        except Exception:
           pass
        if member == ctx.author:
            msg = f'**<@{ctx.author.id}>** ударил(а) себя'
        elif member == None:
            msg = f'**<@{ctx.author.id}>** ударил(а) mee6'
        else:
            msg = f'**<@{ctx.author.id}>** ударил(а) **<@{member.id}>**'

        server = servers.find_one({"server": ctx.guild.id})
        emb=discord.Embed(description = str(msg), color=server['embed_color'])
        giff = random.randint(1,12)
        if giff == 1:
            gif = "https://media.indiedb.com/cache/images/groups/1/25/24269/thumb_620x2000/t3_56xx0a.gif"
        if giff == 2:
            gif = "https://data.whicdn.com/images/187664188/original.gif"
        if giff == 3:
            gif = "https://i.gifer.com/Vx5G.gif"
        if giff == 4:
            gif = "https://i.gifer.com/embedded/download/Ua1c.gif"
        if giff == 5:
            gif = "https://i.gifer.com/embedded/download/EHzF.gif"
        if giff == 6:
            gif = "https://pa1.narvii.com/6866/9b0ba3ba4f29eab79ad7a8418855f7794eb912cfr1-480-360_hq.gif"
        if giff == 7:
            gif = "https://i.gifer.com/8sWB.gif"
        if giff == 8:
            gif = "http://blog-imgs-96.fc2.com/y/a/r/yarakan/fm64184.gif"
        if giff == 9:
            gif = "https://i.gifer.com/7zBH.gif"
        if giff == 10:
            gif = "https://i.gifer.com/HirD.gif"
        if giff == 11:
            gif = "https://anime-chan.me/uploads/posts/2016-06/1466605321_tumblr_o6vl2drsqu1tndn6wo1_540.gif"
        if giff == 12:
            gif = "https://s01.yapfiles.ru/files/1066009/TheRollingGirlsAnimegifkiAnime1831696.gif"
        emb.set_image(url = gif )
        await ctx.send(embed=emb)

    @commands.command(usage = '[@member]', description = 'Реакция лизнуть.', aliases = ['лизнуть'], help = 'Любовные')
    async def lick(self, ctx, member:discord.Member = None):
        try:
            await ctx.channel.purge(limit = 1)
        except Exception:
           pass
        if member == ctx.author:
            msg = f'**<@{ctx.author.id}>** лизнул(а) себя'
        elif member == None:
            msg = f'**<@{ctx.author.id}>** лизнул(а) <@734730292484505631>'
        else:
            msg = f'**<@{ctx.author.id}>** лизнул(а) **<@{member.id}>**'

        server = servers.find_one({"server": ctx.guild.id})
        emb=discord.Embed(description = str(msg), color=server['embed_color'])
        giff = random.randint(1,7)
        if giff == 1:
            gif = "https://media.tenor.com/images/3c32c3db39c6d5d80a291a753baa9d95/tenor.gif"
        if giff == 2:
            gif = "https://media.tenor.com/images/e045343b19f32c1fb276ddf0544e7bd8/tenor.gif"
        if giff == 3:
            gif = "https://media.tenor.com/images/1ce96858ae1368c5c6eef23f33594f0a/tenor.gif"
        if giff == 4:
            gif = "https://media.tenor.com/images/454ff7fc7d37fbf3482cdb8b1426103c/tenor.gif"
        if giff == 5:
            gif = "https://media.tenor.com/images/1e8001af03ad6bb7af661cf0265f86cb/tenor.gif"
        if giff == 6:
            gif = "https://i2.yuki.la/c/6e/977f19bf9a24f6c6c60a23d809bad2626c0faba723895dc9c6bbf507548f16ec.gif"
        if giff == 7:
            gif = "https://i2.yuki.la/b/29/b7af0499fd98cb63df18ca9a90f1261eeee8a094c00f32d341dd4c9a152e829b.gif"
        emb.set_image(url = gif )
        await ctx.send(embed=emb)

    @commands.command(usage = '[@member]', description = 'Реакция дать вкусняшку.', aliases = ['вкусняшка'], help = 'Милые')
    async def yummy(self, ctx, member:discord.Member = None):
        try:
            await ctx.channel.purge(limit = 1)
        except Exception:
           pass
        if member == ctx.author:
            msg = f'**<@{ctx.author.id}>** съел(а) вкусняшку'
        elif member == None:
            msg = f'**<@{ctx.author.id}>** дал(а) вкусняшку <@734730292484505631>'
        else:
            msg = f'**<@{ctx.author.id}>** дал(а) вкусняшку **<@{member.id}>**'

        server = servers.find_one({"server": ctx.guild.id})
        emb=discord.Embed(description = str(msg), color=server['embed_color'])
        giff = random.randint(1,9)
        if giff == 1:
            gif = "https://i.gifer.com/2yNA.gif"
        if giff == 2:
            gif = "https://i.gifer.com/32Ph.gif"
        if giff == 3:
            gif = "https://i.kym-cdn.com/photos/images/original/001/221/161/c8e.gif"
        if giff == 4:
            gif = "https://i.gifer.com/1yS5.gif"
        if giff == 5:
            gif = "https://i.gifer.com/G1T3.gif"
        if giff == 6:
            gif = "http://slinky.me/uploads/pic/8/original_fu_53f5ec85dd7d2.gif"
        if giff == 7:
            gif = "https://i.gifer.com/Iy14.gif"
        if giff == 8:
            gif = "https://data.whicdn.com/images/300737750/original.gif"
        if giff == 9:
            gif = "https://i.gifer.com/embedded/download/SKP2.gif"

        emb.set_image(url = gif )
        await ctx.send(embed=emb)


    @commands.command(usage = '[@member]', description = 'Реакция танцевать.', aliases = ['танцевать'], help = 'Весёлые')
    async def dance(self, ctx,member:discord.Member = None):
        try:
            await ctx.channel.purge(limit = 1)
        except Exception:
           pass
        if member == ctx.author:
            msg = f'**<@{ctx.author.id}>** танцует'
        elif member == None:
            msg = f'**<@{ctx.author.id}>** танцует с котиком.'
        else:
            msg = f'**<@{ctx.author.id}>** танцует с **<@{member.id}>**'

        server = servers.find_one({"server": ctx.guild.id})
        emb=discord.Embed(description = str(msg), color=server['embed_color'])
        giff = random.randint(1,4)
        if giff == 1:
            gif = "https://cdn-ak.f.st-hatena.com/images/fotolife/p/pema/20120831/20120831223551_original.gif"
        if giff == 2:
            gif = "https://pa1.narvii.com/6818/0bebae774b7114f10370c2d33447f68cfc355863_hq.gif"
        if giff == 3:
            gif = "https://i.pinimg.com/originals/d0/c5/67/d0c567253ce4b83823fa11069ae0bc1b.gif"
        if giff == 4:
            gif = "https://i.kym-cdn.com/photos/images/original/000/986/899/d51.gif"
        emb.set_image(url = gif )
        await ctx.send(embed=emb)

    @commands.command(usage = '[@member]', description = 'Реакция спать.', aliases = ['спать'], help = 'Спокойные')
    async def sleep(self, ctx,member:discord.Member = None):
        try:
            await ctx.channel.purge(limit = 1)
        except Exception:
           pass
        if member == ctx.author:
            msg = f'**<@{ctx.author.id}>** заснул(а)'
        elif member == None:
            msg = f'**<@{ctx.author.id}>** заснул(а) вместе с <@734730292484505631>'
        else:
            msg = f'**<@{ctx.author.id}>** заснул(а) вместе с **<@{member.id}>**'

        server = servers.find_one({"server": ctx.guild.id})
        emb=discord.Embed(description = str(msg), color=server['embed_color'])
        giff = random.randint(1,7)
        if giff == 1:
            gif = "https://data.whicdn.com/images/258078020/original.gif"
        if giff == 2:
            gif = "https://pa1.narvii.com/6940/46692bcf9c716840e8350e2588745f1018793158r1-540-304_hq.gif"
        if giff == 3:
            gif = "https://thumbs.gfycat.com/GorgeousIncompatibleJerboa-size_restricted.gif"
        if giff == 4:
            gif = "https://thumbs.gfycat.com/DeliciousBogusImperatorangel-size_restricted.gif"
        if giff == 5:
            gif = "https://img.gifmagazine.net/gifmagazine/images/498453/original.gif"
        if giff == 6:
            gif = "https://data.whicdn.com/images/47921711/original.gif"
        if giff == 7:
            gif = "https://i.pinimg.com/originals/dc/5c/d3/dc5cd3670390cb757c9f7c52591d3c09.gif"
        emb.set_image(url = gif )
        await ctx.send(embed=emb)

    @commands.command(usage = '[@member]', description = 'Реакция дать пощечину.', aliases = ['пощечина'], help = 'Агрессивные')
    async def slap(self, ctx,member:discord.Member = None):
        try:
            await ctx.channel.purge(limit = 1)
        except Exception:
           pass
        if member == ctx.author:
            msg = f'**<@{ctx.author.id}>** дал(а) пощёчину себе '
        elif member == None:
            msg = f'**<@{ctx.author.id}>** дал(а) пощёчину <@734730292484505631>'
        else:
            msg = f'**<@{ctx.author.id}>** дал(а) пощёчину **<@{member.id}>**'

        server = servers.find_one({"server": ctx.guild.id})
        emb=discord.Embed(description = str(msg), color=server['embed_color'])
        giff = random.randint(1,5)
        if giff == 1:
            gif = "https://media.tenor.com/images/79c666d38d5494bad25c5c023c0bbc44/tenor.gif"
        if giff == 2:
            gif = "https://media.tenor.com/images/45a27dba6f60c6a8deee02335dd5f1a0/tenor.gif"
        if giff == 3:
            gif = "https://media.tenor.com/images/c366bb3a5d7820139646d8cdce96f7a8/tenor.gif"
        if giff == 4:
            gif = "https://media.tenor.com/images/49b0ce2032f6134c31e1313cb078fe5a/tenor.gif"
        if giff == 5:
            gif = "https://media.tenor.com/images/a107547117e0b8f22e00a3f39c40eb2f/tenor.gif"
        emb.set_image(url = gif )
        await ctx.send(embed=emb)

    @commands.command(usage = '[@member]', description = 'Реакция тыкнуть.', aliases = ['тыкнуть'], help = 'Милые')
    async def poke(self, ctx,member:discord.Member = None):
        try:
            await ctx.channel.purge(limit = 1)
        except Exception:
           pass
        if member == ctx.author:
            msg = f'**<@{ctx.author.id}>** тыкнул(а) себе '
        elif member == None:
            msg = f'**<@{ctx.author.id}>** тыкнул(а) <@734730292484505631>'
        else:
            msg = f'**<@{ctx.author.id}>** тыкнул(а) **<@{member.id}>**'

        server = servers.find_one({"server": ctx.guild.id})
        emb=discord.Embed(description = str(msg), color=server['embed_color'])
        giff = random.randint(1,8)
        if giff == 1:
            gif = "https://media.tenor.com/images/8bf3b4bec5055537dda92d86d16ea5bd/tenor.gif"
        if giff == 2:
            gif = "https://media.tenor.com/images/88dad48943ce9f198047e8d83ca58fcb/tenor.gif"
        if giff == 3:
            gif = "https://media.tenor.com/images/d31bb1bef6b6cfd486a9ab11be25dbcc/tenor.gif"
        if giff == 4:
            gif = "https://media.tenor.com/images/7eeed38fd37c7dd93b93546fa12bd174/tenor.gif"
        if giff == 5:
            gif = "https://media.tenor.com/images/1e70d4ccc02335ee194e55aaa0dc23b4/tenor.gif"
        if giff == 6:
            gif = "https://media.tenor.com/images/5f0d2906b9fbffb020d0bb25b0666b1c/tenor.gif"
        if giff == 7:
            gif = "https://media.tenor.com/images/e9fa94b95440f5823c73ef4154866bf8/tenor.gif"
        if giff == 8:
            gif = "https://media.tenor.com/images/fbbf9713d5202abed4ad4f4c3306cbe9/tenor.gif"
        emb.set_image(url = gif )
        await ctx.send(embed=emb)

    @commands.command(usage = '[@member]', description = 'Реакция дать пять.', aliases = ['дать_пять'], help = 'Дружеские')
    async def highfive(self, ctx,member:discord.Member = None):
        try:
            await ctx.channel.purge(limit = 1)
        except Exception:
           pass
        if member == ctx.author:
            msg = f'**<@{ctx.author.id}>** дал(а) пять себе '
        elif member == None:
            msg = f'**<@{ctx.author.id}>** дал(а) пять <@734730292484505631>'
        else:
            msg = f'**<@{ctx.author.id}>** дал(а) пять **<@{member.id}>**'

        server = servers.find_one({"server": ctx.guild.id})
        emb=discord.Embed(description = str(msg), color=server['embed_color'])
        giff = random.randint(1,5)
        if giff == 1:
            gif = "https://media.tenor.com/images/d5dafcce563b87bc56c95a21ce5d2a08/tenor.gif"
        if giff == 2:
            gif = "https://media.tenor.com/images/5628f231595350b459d6bf8278cc5e59/tenor.gif"
        if giff == 3:
            gif = "https://media.tenor.com/images/b00b1e796f9ee25bd867ffe0bc80b1be/tenor.gif"
        if giff == 4:
            gif = "https://media.tenor.com/images/275f81b7ccacad49faf2056ad47c1519/tenor.gif"
        if giff == 5:
            gif = "https://media.tenor.com/images/0e95047c3c3103eb894d478646e408af/tenor.gif"
        emb.set_image(url = gif )
        await ctx.send(embed=emb)

    @commands.command(usage = '(@member)', description = 'Реакция заняться кексом.', aliases = ['кекс'], help = 'Любовные')
    async def sex(self,ctx, member:discord.Member):
        server = servers.find_one({"server": ctx.guild.id})
        try:
            await ctx.channel.purge(limit = 1)
        except Exception:
           pass
        if not member == ctx.author:
            reaction = 'a'
            giff = random.randint(1,3)
            if giff == 1:
                gif = "https://media.tenor.com/images/0c8887f7281df4efb89a0733532b9cab/tenor.gif"
            if giff == 2:
                gif = "https://media.tenor.com/images/2f9c0911fc5d320c0b6c2d9748a24395/tenor.gif"
            if giff == 3:
                gif = "https://media.tenor.com/images/cd005faf41f7ac442a5acc0a7082cc75/tenor.gif"

            emb1=discord.Embed(description = f"<@{member.id}>, <@{ctx.author.id}> предлагает вам занятся кексом. Вы согласны?", color=server['embed_color']).set_footer(
            text = 'Нажми на реакцию ❤️ если да.',icon_url = member.avatar.url)
            emb2=discord.Embed(description = f"<@{ctx.author.id}> и <@{member.id}> занялись кексом", color=server['embed_color']).set_thumbnail(url = gif )
            emb3=discord.Embed(description = f"<@{member.id}> не ответил на предложение", color=server['embed_color'])

            def check( reaction, user):
                nonlocal msg
                return user == member and str(reaction.emoji) == '❤️' and str(reaction.message) == str(msg)

            async def pt():
                await msg.edit(embed = emb3)
                return

            async def reackt(msg):
                nonlocal reaction
                await msg.add_reaction('❤️')
                try:
                    reaction, user = await self.bot.wait_for('reaction_add', timeout=30.0, check = check)
                except asyncio.TimeoutError:
                    await pt()
                else:
                    return True

            async def xs():
                await msg.edit(embed = emb2)
                return

            msg = await ctx.send(embed = emb1)
            if await reackt(msg)== True:
                if str(reaction.emoji) == '❤️':
                    await xs()
                    return
        else:
            await ctx.send("Не нарушай законы этого мира")


    @commands.command(aliases = ["ha-ha", "hah",'смеяться'], usage = '[@member]', description = 'Реакция посмеяться над кем то.', help = 'Весёлые')
    async def ha(self, ctx, member:discord.Member = None):

        try:
            await ctx.channel.purge(limit = 1)
        except Exception:
           pass

        if member == ctx.author:
            msg = f'**<@{ctx.author.id}>** посмеялся(ась) '
        elif member == None:
            msg = f'**<@{ctx.author.id}>** посмеялся(ась) вместе с <@734730292484505631>'
        else:
            msg = f'**<@{ctx.author.id}>** посмеялся(ась) над **<@{member.id}>**'

        server = servers.find_one({"server": ctx.guild.id})
        emb=discord.Embed(description = str(msg), color=server['embed_color'])
        rr = ['https://media.tenor.com/images/b7dccbe27053b82434fa2419da378eba/tenor.gif',
        'https://media.tenor.com/images/114732cc0b35c228006d734b0051b9ee/tenor.gif',
        'https://media.tenor.com/images/0953b631d73358ecbc4d1fb2de8770a9/tenor.gif',
        'https://media.tenor.com/images/215fc61f486486ebfc40c235e2c6b970/tenor.gif',
        'https://media.tenor.com/images/c622cef81456cb18fbda3af23098992f/tenor.gif',
        'https://media.tenor.com/images/fee78c6a17e907dd775bcbf4ac029e5c/tenor.gif',
        'https://media.tenor.com/images/d441ee43d1b5f41425a3bdc99320a710/tenor.gif',
        'https://media.tenor.com/images/36d6ca060d01c5a19fb5b4047f00d1cd/tenor.gif',
        'https://media.tenor.com/images/e90526eed1dbdac2432bdbbc579ca825/tenor.gif']
        gif = random.choice(rr)
        emb.set_image(url = gif )
        await ctx.send(embed=emb)


    @commands.command(usage = '[@member]', description = 'Реакция спеть с кем то.', aliases = ['петь'], help = 'Спокойные')
    async def sing(self, ctx, member:discord.Member = None):
        try:
            await ctx.channel.purge(limit = 1)
        except Exception:
           pass


        if member == ctx.author:
            msg = f'**<@{ctx.author.id}>** поёт '
        elif member == None:
            msg = f'**<@{ctx.author.id}>** поёт с котиком'
        else:
            msg = f'**<@{ctx.author.id}>** поёт вместе с **<@{member.id}>**'

        server = servers.find_one({"server": ctx.guild.id})
        emb=discord.Embed(description = str(msg), color=server['embed_color'])
        rr = ['https://i.gifer.com/Clel.gif',
        'https://pa1.narvii.com/6859/60b89bbe504ac79f5c98c875a06c908bfe7b2f0c_hq.gif',
        'https://i.gifer.com/NBYu.gif',
        'https://i.gifer.com/LPIu.gif',
        'https://i.gifer.com/embedded/download/3ZZZ.gif',
        'https://i.gifer.com/embedded/download/VpFw.gif',
        'https://pa1.narvii.com/6115/e66f5e96b8b7d66ca49c3c74c66f5a2c0ae402a9_hq.gif',
        'https://pa1.narvii.com/6871/7e39d811701f7687b25c2ec78c87b07c392ff60ar1-500-300_hq.gif',
        'https://i.gifer.com/EmkU.gif']
        gif = random.choice(rr)
        emb.set_image(url = gif )
        await ctx.send(embed=emb)

    @commands.command(aliases = ['drink', 'выпить_чаю'], usage = '[@member]', description = 'Реакция выпить чаю.', help = 'Спокойные')
    async def drink_tea(self, ctx, member:discord.Member = None):
        server = servers.find_one({"server": ctx.guild.id})
        try:
            await ctx.channel.purge(limit = 1)
        except Exception:
           pass

        if member == ctx.author:
            msg = f'**<@{ctx.author.id}>** пьёт чай сам с собой'
        elif member == None:
            msg = f'**<@{ctx.author.id}>** пьёт чай '
        else:
            msg = f'**<@{ctx.author.id}>** пьёт чай с **<@{member.id}>**'

        emb = discord.Embed(description = str(msg), color=server['embed_color'])
        rr = ['https://data.whicdn.com/images/336042372/original.gif',
        'https://pa1.narvii.com/7018/c33c362bc8ccfebb380f8d96b945f2a57093fa3dr1-500-281_hq.gif',
        'https://pa1.narvii.com/6871/749ea5875cf2ef065abb0ba0fad0bd5868ac2950r1-500-281_hq.gif',
        'https://pa1.narvii.com/6690/997dbe5e01dd0c3f5c56568b44a53672a19f5cc2_hq.gif',
        'https://i.gifer.com/embedded/download/RdLD.gif',
        'https://data.whicdn.com/images/329618110/original.gif',
        'https://i.gifer.com/KDOF.gif'
        ]
        gif = random.choice(rr)
        emb.set_image(url = gif )
        await ctx.send(embed=emb)

    @commands.command(aliases = ['death_note', 'записать_в_тетрадь'], usage = '[@member]', description = 'Реакция записать в тетрадь смерти.', help = 'Агрессивные')
    async def dnote(self, ctx, member:discord.Member = None):
        server = servers.find_one({"server": ctx.guild.id})
        rtime = random.randint(1, 666)
        rtime2 = random.choice(["дней(я)", 'секунд(ы)', 'минут(ы)', 'недель(и)'])
        try:
            await ctx.channel.purge(limit = 1)
        except Exception:
           pass

        if member == ctx.author:
            msg = f'**<@{ctx.author.id}>** записал(а) себя в тетрадку, он(а) умрёт через `{rtime}-{rtime2}`'
        elif member == None:
            msg = f'**<@{ctx.author.id}>** записал(а) Mee6 в тетрадь смерти, он умрёт через `моментально-моментально`'
        else:
            msg = f'**<@{ctx.author.id}>** записал(а) **<@{member.id}>** в тетрадь смерти, он(а) умрёт через `{rtime}-{rtime2}`'

        emb = discord.Embed(description = str(msg), color=server['embed_color'])
        rr = ['https://data.whicdn.com/images/234102919/original.gif', 'http://pa1.narvii.com/5973/77087cfb96d332d3c65a4283ff3a9cb066333e43_hq.gif'
        ]
        gif = random.choice(rr)
        emb.set_image(url = gif )
        await ctx.send(embed=emb)




def setup(bot):
    bot.add_cog(reactions(bot))
