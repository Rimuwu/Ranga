import nextcord as discord
from nextcord.ext import tasks, commands
import requests
import io
import sys
import asyncio
import time
import os
import pymongo
import config

sys.path.append("..")
from ai3 import functions as funs

client = pymongo.MongoClient(config.cluster_token)
db = client.bot
users = db.users
servers = db.servers


class voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(usage = '[@member]', description = 'Закрыть приватку.')
    async def voice_lock(self,ctx, member:discord.Member = None):

        try:
            await ctx.channel.purge(limit = 1)
        except Exception:
           pass

        server = servers.find_one({"server": ctx.guild.id})
        if ctx.author.voice == None:
            await ctx.send("Вы не в войс канале", delete_after = 5.0)
            return
        else:
            channel = await self.bot.fetch_channel(ctx.author.voice.channel.id)
            try:
                channel_owner = server['private_voices'][f'{channel.id}']
            except Exception:
                await ctx.send("Вы находитесь не в приватном войс канале!", delete_after = 5.0)
                return

            if channel_owner != ctx.author.id:
                await ctx.send("Вы не являетесь создателем войса!", delete_after = 5.0)
                return

            if member != None:
                await channel.set_permissions(member, connect=False)
                emb = discord.Embed(description = f'Канал был закрыт для подключения пользователем {member.mention}!', color=0xf03e65)

            else:
                await channel.set_permissions(ctx.guild.default_role, connect=False)
                emb = discord.Embed(description = 'Канал был закрыт для подключения пользователей!', color=0xf03e65)

            emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
            message = await ctx.send(embed = emb, delete_after = 5.0)

    @commands.command(usage = '[@member]', description = 'Открыть приватку.')
    async def voice_unlock(self,ctx, member:discord.Member = None):

        try:
            await ctx.channel.purge(limit = 1)
        except Exception:
           pass

        server = servers.find_one({"server": ctx.guild.id})
        if ctx.author.voice == None:
            await ctx.send("Вы не в войс канале", delete_after = 5.0)
            return
        else:
            channel = await self.bot.fetch_channel(ctx.author.voice.channel.id)
            try:
                channel_owner = server['private_voices'][f'{channel.id}']
            except Exception:
                await ctx.send("Вы находитесь не в приватном войс канале!", delete_after = 5.0)
                return

            if channel_owner != ctx.author.id:
                await ctx.send("Вы не являетесь создателем войса!", delete_after = 5.0)
                return

            if member != None:
                await channel.set_permissions(member, connect=True)
                emb = discord.Embed(description = f'Канал был открыт для подключения пользователем {member.mention}!', color=0xf03e65)

            else:
                await channel.set_permissions(ctx.guild.default_role, connect=True)
                emb = discord.Embed(description = 'Канал был открыт для подключения пользователей!', color=0xf03e65)

            emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
            message = await ctx.send(embed = emb, delete_after = 5.0)

    @commands.command(usage = '[@member]', description = 'Скрыть приватку.')
    async def voice_hide(self,ctx, member:discord.Member = None):

        try:
            await ctx.channel.purge(limit = 1)
        except Exception:
           pass

        server = servers.find_one({"server": ctx.guild.id})
        if ctx.author.voice == None:
            await ctx.send("Вы не в войс канале", delete_after = 5.0)
            return
        else:
            channel = await self.bot.fetch_channel(ctx.author.voice.channel.id)
            try:
                channel_owner = server['private_voices'][f'{channel.id}']
            except Exception:
                await ctx.send("Вы находитесь не в приватном войс канале!", delete_after = 5.0)
                return

            if channel_owner != ctx.author.id:
                await ctx.send("Вы не являетесь создателем войса!", delete_after = 5.0)
                return

            if member != None:
                await channel.set_permissions(member, view_channel=False)
                emb = discord.Embed(description = f'Канал был закрыт для просмотра пользователем {member.mention}!', color=0xf03e65)

            else:
                await channel.set_permissions(ctx.guild.default_role, view_channel=False)
                emb = discord.Embed(description = 'Канал был закрыт для просмотра пользователей!', color=0xf03e65)

            emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
            message = await ctx.send(embed = emb, delete_after = 5.0)

    @commands.command(usage = '[@member]', description = 'Раскрыть приватку.')
    async def voice_unhide(self,ctx, member:discord.Member = None):

        try:
            await ctx.channel.purge(limit = 1)
        except Exception:
           pass

        server = servers.find_one({"server": ctx.guild.id})
        if ctx.author.voice == None:
            await ctx.send("Вы не в войс канале", delete_after = 5.0)
            return
        else:
            channel = await self.bot.fetch_channel(ctx.author.voice.channel.id)
            try:
                channel_owner = server['private_voices'][f'{channel.id}']
            except Exception:
                await ctx.send("Вы находитесь не в приватном войс канале!", delete_after = 5.0)
                return

            if channel_owner != ctx.author.id:
                await ctx.send("Вы не являетесь создателем войса!", delete_after = 5.0)
                return

            if member != None:
                await channel.set_permissions(member, view_channel=True)
                emb = discord.Embed(description = f'Канал был открыт для просмотра пользователем {member.mention}!', color=0xf03e65)

            else:
                await channel.set_permissions(ctx.guild.default_role, view_channel=True)
                emb = discord.Embed(description = 'Канал был открыт для просмотра пользователей!', color=0xf03e65)

            emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
            message = await ctx.send(embed = emb, delete_after = 5.0)

    @commands.command(usage = '(@member)', description = 'Кикнуть из приватки')
    async def voice_kick(self,ctx, member:discord.Member):

        try:
            await ctx.channel.purge(limit = 1)
        except Exception:
           pass

        server = servers.find_one({"server": ctx.guild.id})
        if ctx.author.voice == None:
            await ctx.send("Вы не в войс канале", delete_after = 5.0)
            return
        if member.voice == None:
            await ctx.send("Пользователь не в войс канале", delete_after = 5.0)
            return
        else:
            channel = await self.bot.fetch_channel(ctx.author.voice.channel.id)
            try:
                channel_owner = server['private_voices'][f'{channel.id}']
            except Exception:
                await ctx.send("Вы находитесь не в приватном войс канале!", delete_after = 5.0)
                return

            if channel_owner != ctx.author.id:
                await ctx.send("Вы не являетесь создателем войса!", delete_after = 5.0)
                return

            await member.move_to(channel=None, reason="Пользователь кикнут создателем приватного войса")
            emb = discord.Embed(description = f'{member.mention} был исключён из войса!', color=0xf03e65)

            emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
            message = await ctx.send(embed = emb, delete_after = 5.0)

    @commands.command(usage = '(@member)', description = 'Передать управление.')
    async def voice_owner(self,ctx, member:discord.Member):

        try:
            await ctx.channel.purge(limit = 1)
        except Exception:
           pass

        server = servers.find_one({"server": ctx.guild.id})
        if ctx.author.voice == None:
            await ctx.send("Вы не в войс канале", delete_after = 5.0)
            return
        if member.voice == None:
            await ctx.send("Пользователь не в войс канале", delete_after = 5.0)
            return
        else:
            channel = await self.bot.fetch_channel(ctx.author.voice.channel.id)
            try:
                channel_owner = server['private_voices'][f'{channel.id}']
            except Exception:
                await ctx.send("Вы находитесь не в приватном войс канале!", delete_after = 5.0)
                return

            if channel_owner != ctx.author.id:
                await ctx.send("Вы не являетесь создателем войса!", delete_after = 5.0)
                return

            v = server['private_voices']
            v.update({f"{channel.id}": member.id})
            servers.update_one({'server': ctx.guild.id},{'$set': {'private_voices': v}})
            emb = discord.Embed(description = f'{member.mention} теперь создатель войса!', color=0xf03e65)

            emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
            message = await ctx.send(embed = emb, delete_after = 5.0)

    @commands.command(usage = '(limit)', description = 'Установить лимит')
    async def voice_limit(self, ctx, limit:int):

        if limit > 99:
            limit = 99
        elif limit < 0:
            limit = 0

        try:
            await ctx.channel.purge(limit = 1)
        except Exception:
           pass

        server = servers.find_one({"server": ctx.guild.id})
        if ctx.author.voice == None:
            await ctx.send("Вы не в войс канале", delete_after = 5.0)
            return
        else:
            channel = await self.bot.fetch_channel(ctx.author.voice.channel.id)
            try:
                channel_owner = server['private_voices'][f'{channel.id}']
            except Exception:
                await ctx.send("Вы находитесь не в приватном войс канале!", delete_after = 5.0)
                return

            if channel_owner != ctx.author.id:
                await ctx.send("Вы не являетесь создателем войса!", delete_after = 5.0)
                return

            emb = discord.Embed(description = f'Лимит канала был установлен на {limit}!', color=0xf03e65)
            await channel.edit(user_limit = limit ,reason="Настройка лимита приватного войса")

            emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
            message = await ctx.send(embed = emb, delete_after = 5.0)

    @commands.command(usage = '(name)', description = 'Изменить название приватки.')
    async def voice_name(self, ctx, *,name:str):

        if len(name) > 100:
            await ctx.send("Название не может быть больше чем 100 символов!", delete_after = 5.0)
            return
        elif len(name) < 1:
            await ctx.send("Название не может быть меньше чем 1 символ!", delete_after = 5.0)
            return

        try:
            await ctx.channel.purge(limit = 1)
        except Exception:
           pass

        server = servers.find_one({"server": ctx.guild.id})
        if ctx.author.voice == None:
            await ctx.send("Вы не в войс канале", delete_after = 5.0)
            return
        else:
            channel = await self.bot.fetch_channel(ctx.author.voice.channel.id)
            try:
                channel_owner = server['private_voices'][f'{channel.id}']
            except Exception:
                await ctx.send("Вы находитесь не в приватном войс канале!", delete_after = 5.0)
                return

            if channel_owner != ctx.author.id:
                await ctx.send("Вы не являетесь создателем войса!", delete_after = 5.0)
                return

            emb = discord.Embed(description = f'Название канала было изменено на  {name}!', color=0xf03e65)
            await channel.edit(name = name ,reason="Настройка названия приватного войса")

            emb.set_author(name = '{}'.format(ctx.author), icon_url = '{}'.format(ctx.author.avatar.url))
            message = await ctx.send(embed = emb, delete_after = 5.0)




def setup(bot):
    bot.add_cog(voice(bot))
