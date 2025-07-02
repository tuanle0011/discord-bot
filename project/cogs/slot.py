import discord
from discord.ext import commands
import random
import asyncio

class Slot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Đảm bảo các emoji này là ID đúng của bạn.
        self.emojis = [
            "🍒", # Quả anh đào
            "🍋", # Chanh
            "🍊", # Cam
            "🍇", # Nho
            "🔔", # Chuông
            "💎", # Kim cương
            "💰", # Túi tiền
            "<:coin:1389097855200919672>" # Sử dụng ID emoji coin của bạn
        ]
        # Đã đặt :emoji52: làm biểu tượng quay
        self.rolling_emoji = "<a:emoji_52:1389097855200919672>" 

        self.lose_emoji = "<:EmmaOw:1388869844035960842>"
        self.win_emoji = "<:EmmaEmbarassed:1388869797734776904>"

    def ensure_user(self, user_id):
        if user_id not in self.bot.user_balances:
            self.bot.user_balances[user_id] = 1000 # Gán 1000 tiền ban đầu nếu user mới
            self.bot.save_user_data()

    @commands.command(name="s")
    @commands.cooldown(1, 3, commands.BucketType.user) # Thêm cooldown để tránh spam
    async def slot(self, ctx, amount: int):
        user_id = ctx.author.id
        self.ensure_user(user_id)

        if amount <= 0:
            return await ctx.send("❌ Số tiền cược phải lớn hơn 0.")
        if self.bot.user_balances[user_id] < amount:
            return await ctx.send("❌ Bạn không đủ tiền để chơi.")

        # Trừ tiền cược ngay lập tức
        self.bot.user_balances[user_id] -= amount
        self.bot.save_user_data()

        # Khởi tạo embed với emoji quay
        initial_embed = discord.Embed(
            description=f"{self.rolling_emoji} {self.rolling_emoji} {self.rolling_emoji}",
            color=discord.Color.blurple()
        )
        initial_embed.set_footer(text=f"Đang quay slot với {amount} coins...")
        msg = await ctx.send(embed=initial_embed)

        results = [] # Lưu trữ kết quả cuối cùng của 3 slot
        
        # Quay và dừng slot thứ nhất
        await asyncio.sleep(1)
        slot1 = random.choice(self.emojis)
        await msg.edit(embed=discord.Embed(
            description=f"{slot1} {self.rolling_emoji} {self.rolling_emoji}",
            color=discord.Color.blurple()
        ))
        results.append(slot1)

        # Quay và dừng slot thứ hai
        await asyncio.sleep(1)
        slot2 = random.choice(self.emojis)
        await msg.edit(embed=discord.Embed(
            description=f"{slot1} {slot2} {self.rolling_emoji}",
            color=discord.Color.blurple()
        ))
        results.append(slot2)

        # Quay và dừng slot thứ ba
        await asyncio.sleep(1)
        slot3 = random.choice(self.emojis)
        await msg.edit(embed=discord.Embed(
            description=f"{slot1} {slot2} {slot3}",
            color=discord.Color.blurple()
        ))
        results.append(slot3)

        # Chờ thêm một chút trước khi hiện kết quả cuối cùng
        await asyncio.sleep(0.5)

        result_embed = discord.Embed()
        user_mention = ctx.author.mention

        # Kiểm tra kết quả
        if slot1 == slot2 == slot3:
            # Thắng lớn nếu 3 biểu tượng giống nhau
            win_amount = amount * 5 # Tăng hệ số thắng cho 3 biểu tượng giống nhau
            self.bot.user_balances[user_id] += win_amount
            self.bot.save_user_data()
            result_embed.description = (
                f"**`___SLOTS___`**\n` ` {' '.join(results)} ` ` {user_mention} thắng lớn **{win_amount} coins**!\n"
                f"`|         |` {self.win_emoji} Chúc mừng!"
            )
            result_embed.color = discord.Color.green()
        elif slot1 == slot2 or slot2 == slot3: # Hoặc nếu bạn muốn 2 biểu tượng giống nhau cũng có thưởng
            win_amount = amount * 1.5 # Thắng nhẹ hơn cho 2 biểu tượng giống nhau
            self.bot.user_balances[user_id] += win_amount
            self.bot.save_user_data()
            result_embed.description = (
                f"**`___SLOTS___`**\n` ` {' '.join(results)} ` ` {user_mention} thắng **{win_amount} coins**!\n"
                f"`|         |` Có 2 biểu tượng giống nhau!"
            )
            result_embed.color = discord.Color.gold() # Màu vàng cho thắng nhỏ
        else:
            result_embed.description = (
                f"**`___SLOTS___`**\n` ` {' '.join(results)} ` ` {user_mention} cược **{amount} coins**\n"
                f"`|         |` và thua {self.lose_emoji} Chúc may mắn lần sau!"
            )
            result_embed.color = discord.Color.red()

        await msg.edit(embed=result_embed)

async def setup(bot):
    await bot.add_cog(Slot(bot))
    
