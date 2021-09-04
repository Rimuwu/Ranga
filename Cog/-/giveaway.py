import discord  # Discord
from discord.ext import commands  # Discord
import config
import asyncio
import time
import random
from random import choice

class giveaway(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.command(aliases = ['g'])
    async def giveaway( self, ctx, seconds: int, arg, *, text ):
        def time_end_form( seconds ):
            d = seconds//86400
            h = (seconds - d*86400)//3600
            hh = seconds//3600
            m = (seconds - hh*3600)//60
            s = seconds%60
            if d < 10:
                d = f"0{d}"
            if h < 10:
                h = f"0{h}"
            if m < 10:
                m = f"0{m}"
            if s < 10:
                s = f"0{s}"
            time_reward = f"{d} : {h} : {m} : {s}"
            return time_reward
        if arg == "s":
            pass
        if arg == "m":
            seconds = seconds*60
        if arg == "h":
            seconds = seconds*3600
        if arg == "d":
            seconds = seconds*86400
        else:
            pass
        author = ctx.message.author
        time_end = time_end_form(seconds)
        message = await ctx.send(embed = discord.Embed(
            description = f"**Разыгрывается : `{text}`\nЗавершится через: `{time_end}` \n\nОрганизатор: {author.mention} \nДля участия нажмите на реакцию ниже.**",
            colour = 0xde2e1).set_footer(
            text = 'Посмотрим кто победит...',
            icon_url = ctx.message.author.avatar_url))
        await message.add_reaction("🎉")
        while seconds > -60:
            time_end = time_end_form(seconds)
            text_message = discord.Embed(
                description = f"**Разыгрывается: *_{text}_*\nЗавершится через: `{time_end}` \n\nОрганизатор: {author.mention} \nДля участия нажмите на реакцию ниже.**",
                colour = 0xde2e1).set_footer(
                text = 'Посмотрим кто победит...',
                icon_url = ctx.message.author.avatar_url)
            await message.edit(embed = text_message)
            await asyncio.sleep(60)
            seconds -= 60
            if seconds < -60:
                break
        channel = message.channel
        message_id = message.id
        message = await channel.fetch_message(message_id)
        reaction = message.reactions[ 0 ]

        users = await reaction.users().flatten()
        if reaction.count == 1:

            win = discord.Embed(
                description = f'**В этом розыгрыше нет победителя!**',
                colour = 0xde2e1).set_footer(
                text = 'Интересный поворот...',
                icon_url = ctx.message.author.avatar_url)
            await message.edit(embed = win)
        else:
            user_win = random.choice(users)
            while str(user_win.id) == str(self.bot.user.id):
                user_win = random.choice(users)
      
            win = discord.Embed(
                description = f'**Розыгрыш завершён!\nПобедитель розыгрыша: {user_win.mention}!\nНапишите организатору, {author.mention}, чтобы получить награду.**',
                colour = 0xde2e1).set_footer(
                text = 'Это круто!',
                icon_url = ctx.message.author.avatar_url)
            await message.edit(embed = win)
 
def setup(bot):
    bot.add_cog(giveaway(bot))