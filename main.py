import discord
from discord.ext import commands, tasks
import os
import json
import datetime
import sys # Import sys
import traceback
import pytz
from keep_alive import keep_alive
from itertools import cycle
from dotenv import load_dotenv
import time

# ===== Load biến môi trường =====
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
if TOKEN is None:
    print("<:HadeCross:1218836263180697684> Không tìm thấy token!")
    exit()

# Dòng này KHÔNG cần thiết nếu thư mục 'cogs' nằm CÙNG CẤP với 'main.py'
# Nếu thư mục 'cogs' của bạn nằm trong một thư mục con như 'project',
# bạn cần kích hoạt lại dòng này và đảm bảo đường dẫn chính xác.
# Ví dụ: sys.path.insert(0, os.path.join(os.path.dirname(__file__), "project"))

intents = discord.Intents.default()
intents.message_content = True
intents.reactions = True
intents.voice_states = True

bot = commands.Bot(command_prefix=".", intents=intents)
start_time = time.time()

# ===== DỮ LIỆU NGƯỜI DÙNG =====
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
        print("❌ Lỗi khi load dữ liệu:", e)
        bot.user_balances = {}
        bot.user_daily = {}
    print("✅ Dữ liệu đã được tải.")

def save_user_data():
    with open("user_data.json", "w") as f:
        json.dump({
            "balances": {str(k): v for k, v in bot.user_balances.items()},
            "daily": {str(k): v.isoformat() for k, v in bot.user_daily.items()}
        }, f, indent=4)
    print("✅ Dữ liệu đã được lưu.")

bot.save_user_data = save_user_data
load_user_data()

# ===== TRẠNG THÁI BOT =====
status_messages = [
    "6/7 | 2025 ",
    "leu leu fa",
    "python | botv1",
    "/help | .bj,..",
    "/help | 24hnw "
]
status_cycle = cycle(status_messages)

@tasks.loop(minutes=5)
async def change_status():
    activity = discord.Game(name=next(status_cycle))
    await bot.change_presence(status=discord.Status.online, activity=activity)

# ===== LỆNH TOP (Giữ nguyên hoặc đưa vào cogs nếu cần) =====
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


# ===== VIEW HELP + MENU (Đã thêm nội dung chi tiết cho từng lệnh) =====
class CategorySelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="🎮 Game", description="Lệnh chơi game"),
            discord.SelectOption(label="💰 Kinh tế", description="Lệnh quản lý tiền"),
            discord.SelectOption(label="⚙️ Hệ thống", description="Lệnh hệ thống và trợ giúp"),
            discord.SelectOption(label="📝 Message Counter", description="Các lệnh về đếm tin nhắn"),
        ]
        super().__init__(placeholder="📂 Chọn danh mục lệnh...", options=options, row=1)

    async def callback(self, interaction: discord.Interaction):
        embed = discord.Embed(color=discord.Color.blurple())
        if self.values[0] == "🎮 Game":
            embed.title = "🎮 Danh sách lệnh Game"
            embed.description = (
                "**Các lệnh chơi game:**\n\n"
                "**.taixiu [tài/xỉu] [số tiền]**\n"
                "Đặt cược tài hoặc xỉu để thử vận may.\n\n"
                "**.blackjack [số tiền]**\n"
                "Chơi bài Blackjack đối đầu với bot.\n\n"
                "**.duangua**\n"
                "Game đuổi gà siêu nhọ - vui là chính!\n\n"
                "**.s**\n"
                "Chơi máy kéo slot kiểu cổ điển để kiếm tiền."
            )
        elif self.values[0] == "💰 Kinh tế":
            embed.title = "💰 Danh sách lệnh Kinh tế"
            embed.description = (
                "**Các lệnh quản lý tiền:**\n\n"
                "**.bal**\n"
                "Kiểm tra số dư tiền hiện tại của bạn.\n\n"
                "**.daily**\n"
                "Nhận phần thưởng mỗi ngày một lần.\n\n"
                "**.give [@user] [số tiền]**\n"
                "Tặng tiền cho người khác trong server.\n\n"
                "**.top**\n"
                "Hiển thị bảng xếp hạng người có nhiều tiền nhất."
            )
        elif self.values[0] == "⚙️ Hệ thống":
            embed.title = "⚙️ Danh sách lệnh hệ thống"
            embed.description = (
                "**Các lệnh hệ thống và trợ giúp:**\n\n"
                "**/help**\n"
                "Hiển thị giao diện trợ giúp (slash command).\n\n"
                "**.ping**\n"
                "Kiểm tra độ trễ (ping) của bot.\n\n"
                "**.setbal [@user] [số tiền]** *(chỉ admin)*\n"
                "Đặt lại số dư cho người dùng."
            )
        elif self.values[0] == "📝 Message Counter":
            embed.title = "📝 Message Counter"
            embed.description = (
                "Commands for message counter.\n\n"
                "**/messages**\n"
                "Shows the number of messages sent by a member.\n\n"
                "**/messages-admin settings**\n"
                "Configure the message counter.\n\n"
                "**/messages-admin enable**\n"
                "Enable the message counter.\n\n"
                "**/messages-admin disable**\n"
                "Disable the message counter.\n\n"
                "**/messages-admin reset-all**\n"
                "Resets all message counts.\n\n"
                "**/messages-admin add**\n"
                "Adds a number of messages to a member's message count.\n\n"
                "**/messages-admin remove**\n"
                "Removes a number of messages from a member's message count."
            )
        embed.set_footer(text="📂 Chọn danh mục khác để xem thêm lệnh...")
        await interaction.response.edit_message(embed=embed, view=self.view)

class HelpView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(discord.ui.Button(
            label="🤖 Mời Bot",
            url="https://discord.com/api/oauth2/authorize?client_id=1388779516914303087&permissions=8&scope=bot+applications.commands"
        ))
        self.add_item(discord.ui.Button(
            label="💬 Hỗ Trợ",
            url="https://discord.gg/Xyhn6ajaUE"
        ))
        self.add_item(CategorySelect())

# ===== SLASH COMMAND =====
@bot.tree.command(name="help", description="Hiển thị danh sách lệnh")
async def help_command(interaction: discord.Interaction):
    embed = discord.Embed(
        title="<:emoji_4:1391456507111149670> Information & Commands",
        description="📂 Chọn danh mục bên dưới để xem các lệnh có sẵn.",
        color=discord.Color.blue()
    )
    await interaction.response.send_message(embed=embed, view=HelpView(), ephemeral=True)

@bot.tree.command(name="setbal", description="Đặt số dư cho người dùng (chỉ admin)")
async def setbal_command(interaction: discord.Interaction, member: discord.Member, amount: int):
    ADMIN_ID = 1259533919041097809
    if interaction.user.id != ADMIN_ID:
        return await interaction.response.send_message("❌ Lệnh này chỉ admin sử dụng.", ephemeral=True)
    if amount < 0:
        return await interaction.response.send_message("❌ Số dư phải ≥ 0.", ephemeral=True)
    bot.user_balances[member.id] = amount
    bot.save_user_data()
    await interaction.response.send_message(f"✅ Đã đặt số dư của {member.mention} thành {amount} 💵.")

# ===== BOT READY =====
@bot.event
async def on_ready():
    change_status.start()
    print(f"{bot.user} đã sẵn sàng!")
    try:
        # Đảm bảo các tên extension này khớp với cấu trúc thư mục của bạn
        # Nếu cogs nằm trực tiếp trong thư mục 'cogs', thì đường dẫn là 'cogs.tencog'
        # Nếu economy nằm trong 'cogs/utils', thì đường dẫn là 'cogs.utils.economy'
        await bot.load_extension("cogs.utils.economy")
        await bot.load_extension("cogs.taixiu")
        await bot.load_extension("cogs.blackjack")
        await bot.load_extension("cogs.duangua")
        await bot.load_extension("cogs.slot")
        await bot.load_extension("cogs.ancap")
        await bot.load_extension("cogs.system")
        print("✅ Đã tải tất cả cogs.")
    except Exception as e:
        print("❌ Lỗi khi load cogs:")
        traceback.print_exception(type(e), e, e.__traceback__)
    try:
        GUILD_ID = discord.Object(id=1388762920594182255) # Thay thế bằng ID guild của bạn nếu muốn sync cụ thể
        synced = await bot.tree.sync(guild=GUILD_ID)
        # Nếu không có guild ID, bot.tree.sync() sẽ sync toàn cầu (có thể mất thời gian)
        # synced = await bot.tree.sync()
        print(f"✅ Slash command synced ({len(synced)} lệnh)")
    except Exception as e:
        print("❌ Lỗi khi sync slash command:")
        traceback.print_exception(type(e), e, e.__traceback__)

# ===== ERROR HANDLER =====
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send("⏳ Lệnh này đang cooldown.")
    elif isinstance(error, commands.CommandNotFound):
        # Bỏ qua lỗi nếu lệnh không tồn tại (có thể là lệnh slash command)
        pass
    else:
        await ctx.send("❌ Đã xảy ra lỗi.")
        traceback.print_exception(type(error), error, error.__traceback__)

# ===== RUN BOT =====
keep_alive()
bot.run(TOKEN)
