import discord
from discord.ext import commands, tasks
import os
import json
import datetime
import sys
import traceback
import pytz
from keep_alive import keep_alive
from itertools import cycle  # thêm để xoay trạng thái

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "project"))

TOKEN = os.getenv("DISCORD_TOKEN")
if TOKEN is None:
    print("❌ Không tìm thấy token!")
    exit()

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True

bot = commands.Bot(command_prefix=".", intents=intents)

# Dữ liệu người dùng
bot.user_balances = {}
bot.user_daily = {}

def load_user_data():
    try:
        with open("user_data.json", "r") as f:
            data = json.load(f)
            bot.user_balances = {int(k): v for k, v in data.get("balances", {}).items()}
            bot.user_daily = {
                int(k): datetime.datetime.strptime(v, "%Y-%m-%d").date()
                for k, v in data.get("daily", {}).items()
            }
    except Exception as e:
        print("❌ Lỗi khi load dữ liệu người dùng:", e)
        bot.user_balances = {}
        bot.user_daily = {}
    print("✅ Dữ liệu người dùng đã được tải.")

def save_user_data():
    with open("user_data.json", "w") as f:
        json.dump({
            "balances": {str(k): v for k, v in bot.user_balances.items()},
            "daily": {str(k): v.isoformat() for k, v in bot.user_daily.items()}
        }, f, indent=4)
    print("✅ Dữ liệu đã được lưu.")

bot.save_user_data = save_user_data
load_user_data()

# 5p
status_messages = [
    "🎰 | lũ đú",
    "🎲 | play .tx 🎲",
    "💰 Nhận tiền mỗi ngày | .daily",
    "🏇 | sikibidi🤪",
    "🃏 | chơi với t nè bọn đú"
]
status_cycle = cycle(status_messages)

@tasks.loop(minutes=5)
async def change_status():
    activity = discord.Game(name=next(status_cycle))
    await bot.change_presence(status=discord.Status.online, activity=activity)

# Leaderboard
LEADERBOARD_CHANNEL_ID = 1389166293604892734

@tasks.loop(minutes=30)
async def send_daily_leaderboard():
    channel = bot.get_channel(LEADERBOARD_CHANNEL_ID)
    if channel:
        sorted_users = sorted(bot.user_balances.items(), key=lambda x: x[1], reverse=True)
        top_10 = sorted_users[:10]
        embed = discord.Embed(
            title="🌟 BẢNG XẾP HẠNG CẬP NHẬT THƯỜNG XUYÊN🪙",
            description="Top 10 anh giàu nhất🪙",
            color=discord.Color.gold(),
            timestamp=datetime.datetime.utcnow()
        )
        for i, (user_id, balance) in enumerate(top_10, start=1):
            try:
                user = await bot.fetch_user(user_id)
                name = user.name
            except:
                name = f"User ID: {user_id}"
            embed.add_field(name=f"#{i} - {name}", value=f"{balance} 💵", inline=False)

        await channel.send(embed=embed)

@bot.command(name="top")
async def top(ctx):
    sorted_users = sorted(bot.user_balances.items(), key=lambda x: x[1], reverse=True)
    top_10 = sorted_users[:10]
    embed = discord.Embed(title="🪙 TOP 10 NAM VƯƠNG GIÀU NHẤT SERVER 🪙", color=discord.Color.green())
    for i, (user_id, balance) in enumerate(top_10, start=1):
        try:
            user = await bot.fetch_user(user_id)
            name = user.name
        except:
            name = f"User ID: {user_id}"
        embed.add_field(name=f"#{i} - {name}", value=f"{balance} 💵", inline=False)
    await ctx.send(embed=embed)

# Slash command
@bot.tree.command(name="help", description="Hiển thị danh sách lệnh")
async def help_command(interaction: discord.Interaction):
    embed = discord.Embed(title="📖 Lệnh có sẵn", color=discord.Color.blue())
    embed.add_field(name="`.bal`", value="Xem số dư", inline=False)
    embed.add_field(name="`.daily`", value="Nhận tiền hàng ngày", inline=False)
    embed.add_field(name="`.give <@user> <số>`", value="Chuyển tiền", inline=False)
    embed.add_field(name="`.taixiu` / `.blackjack` / `.duangua`", value="Các trò chơi", inline=False)
    embed.add_field(name="`.s <tiền>`", value="Chơi máy xèng (Slot)", inline=False)
    embed.add_field(name="`.top`", value="Xem bảng xếp hạng top 10", inline=False)
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="setbal", description="Đặt số dư cho người dùng (chỉ admin)")
async def setbal_command(interaction: discord.Interaction, member: discord.Member, amount: int):
    ADMIN_ID = 1259533919041097809
    if interaction.user.id != ADMIN_ID:
        return await interaction.response.send_message("❌ Chỉ admin mới có quyền dùng lệnh này.", ephemeral=True)
    if amount < 0:
        return await interaction.response.send_message("❌ Số dư phải ≥ 0.", ephemeral=True)
    bot.user_balances[member.id] = amount
    bot.save_user_data()
    await interaction.response.send_message(f"✅ Đã đặt số dư của {member.mention} thành {amount} 💵.")

@bot.event
async def on_ready():
    change_status.start()  # 🟢 Bắt đầu xoay trạng thái
    print(f"{bot.user} đã sẵn sàng!")
    try:
        await bot.load_extension("cogs.utils.economy")
        await bot.load_extension("cogs.taixiu")
        await bot.load_extension("cogs.blackjack")
        await bot.load_extension("cogs.duangua")
        await bot.load_extension("cogs.slot")
        await bot.load_extension("cogs.ancap")
        print("✅ Đã tải tất cả cogs.")
    except Exception as e:
        print(f"❌ Lỗi khi load cogs: {e}")
        traceback.print_exception(type(e), e, e.__traceback__)
    try:
        synced = await bot.tree.sync()
        print(f"✅ Slash command synced ({len(synced)} lệnh)")
    except Exception as e:
        print(f"❌ Lỗi sync slash command: {e}")
        traceback.print_exception(type(e), e, e.__traceback__)
    send_daily_leaderboard.start()

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send("⏳ Lệnh chưa sẵn sàng.")
    elif isinstance(error, commands.CommandNotFound):
        pass
    else:
        await ctx.send("❌ Đã xảy ra lỗi.")
        traceback.print_exception(type(error), error, error.__traceback__)

keep_alive()
bot.run(TOKEN)
