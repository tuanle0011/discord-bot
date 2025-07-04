import discord
from discord.ext import commands
import datetime
import random

class Economy(commands.Cog):
    def __init__(self, bot, user_balances, user_daily, save_user_data):
        self.bot = bot
        self.user_balances = user_balances
        self.user_daily = user_daily
        self.save_user_data = save_user_data

    def ensure_user(self, user_id):
        if user_id not in self.user_balances:
            self.user_balances[user_id] = 1000
            self.save_user_data()

    @commands.command()
    async def bal(self, ctx):
        self.ensure_user(ctx.author.id)
        embed = discord.Embed(
            description=f"💰 Số dư của bạn: {self.user_balances[ctx.author.id]} 💵",
            color=0x00ff00
        )
        await ctx.send(embed=embed)

    @commands.command()
    async def give(self, ctx, member: discord.Member, amount: int):
        sender = ctx.author.id
        receiver = member.id
        self.ensure_user(sender)
        self.ensure_user(receiver)

        if amount <= 0:
            await ctx.send("❌ Số tiền phải lớn hơn 0.")
        elif self.user_balances[sender] < amount:
            await ctx.send("❌ Bạn không đủ tiền để tặng.")
        else:
            self.user_balances[sender] -= amount
            self.user_balances[receiver] += amount
            self.save_user_data()
            embed = discord.Embed(
                description=f"💸 {ctx.author.mention} đã cho {member.mention} {amount} 💵",
                color=0xffff00
            )
            await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(1, 86400, commands.BucketType.user)
    async def daily(self, ctx):
        user_id = ctx.author.id
        self.ensure_user(user_id)
        today = datetime.date.today()

        if self.user_daily.get(user_id) == today:
            await ctx.send("🕒 Bạn đã nhận daily hôm nay rồi! Hãy quay lại vào ngày mai.")
        else:
            reward = random.randint(1000, 2000)
            self.user_balances[user_id] += reward
            self.user_daily[user_id] = today
            self.save_user_data()
            embed = discord.Embed(
                description=f"🎁 Bạn nhận được {reward} 💵!\nSố dư hiện tại: {self.user_balances[user_id]} 💵",
                color=0xff9900
            )
            await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Economy(bot, bot.user_balances, bot.user_daily, bot.save_user_data))
