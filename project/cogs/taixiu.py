import discord
from discord.ext import commands
import random
import asyncio

class TaiXiu(commands.Cog):
    def __init__(self, bot, user_balances, user_daily, save_user_data):
        self.bot = bot
        self.user_balances = user_balances
        self.user_daily = user_daily
        self.save_user_data = save_user_data

    def ensure_user(self, user_id):
        if user_id not in self.user_balances:
            self.user_balances[user_id] = 1000
            self.save_user_data()

    def get_dice_emoji(self, roll):
        dice_emojis = {
            1: "<:xucxac1:1388917150865031338>",
            2: "<:xucxac2:1388917074671308950>",
            3: "<:xucxac3:1388916988163657859>",
            4: "<:xucxac4:1388916885457866944>",
            5: "<:xucxac5:1388916772870033630>",
            6: "<:xucxac6:1388916611494182984>",
        }
        return dice_emojis.get(roll, str(roll))

    def get_taixiu_result(self, dice_rolls):
        total = sum(dice_rolls)
        if total == 3 or total == 18:
            return "Bão", total
        elif 4 <= total <= 10:
            return "Xỉu", total
        else:
            return "Tài", total

    @commands.command(aliases=["tx"])
    async def taixiu(self, ctx, amount: int, choice: str):
        user_id = ctx.author.id
        self.ensure_user(user_id)

        choice = choice.lower()
        if choice not in ["tài", "tai", "xỉu", "xiu"]:
            await ctx.send("🎲 Lựa chọn không hợp lệ. Vui lòng chọn `tài` hoặc `xỉu`.")
            return
        if choice == "tai": choice = "tài"
        if choice == "xiu": choice = "xỉu"

        if amount <= 0:
            await ctx.send("❌ Số tiền cược phải lớn hơn 0.")
            return
        if self.user_balances[user_id] < amount:
            await ctx.send("❌ Bạn không đủ tiền để cược.")
            return

        self.user_balances[user_id] -= amount
        self.save_user_data()

        rolling = "<a:emoji_48:1388884913515663371>"  # emoji xúc xắc động
        message = await ctx.send(f"**`___TÀI XỈU___`**\n{rolling} {rolling} {rolling}\n🎲 Đang gieo xúc xắc...")
        await asyncio.sleep(1)

        roll1 = random.randint(1, 6)
        await message.edit(content=f"**`___TÀI XỈU___`**\n{self.get_dice_emoji(roll1)} {rolling} {rolling}\n🎲 Đang gieo xúc xắc...")
        await asyncio.sleep(1)

        roll2 = random.randint(1, 6)
        await message.edit(content=f"**`___TÀI XỈU___`**\n{self.get_dice_emoji(roll1)} {self.get_dice_emoji(roll2)} {rolling}\n🎲 Đang gieo xúc xắc...")
        await asyncio.sleep(1)

        roll3 = random.randint(1, 6)
        dice_rolls = [roll1, roll2, roll3]

        result_type, total = self.get_taixiu_result(dice_rolls)
        emoji_line = " ".join(self.get_dice_emoji(r) for r in dice_rolls)

        if result_type == "Bão":
            win = False
            color = discord.Color.red()
            footer_text = f"❌ Bạn thua {amount} 💵 (Bão)\nSố dư: {self.user_balances[user_id]} 💵"
        elif choice == result_type.lower():
            win = True
            self.user_balances[user_id] += amount * 2
            color = discord.Color.green()
            footer_text = f"✅ Bạn thắng {amount} 💵\nSố dư mới: {self.user_balances[user_id]} 💵"
        else:
            win = False
            color = discord.Color.red()
            footer_text = f"❌ Bạn thua {amount} 💵\nSố dư: {self.user_balances[user_id]} 💵"

        self.save_user_data()

        display = (
            "**`___TÀI XỈU___`**\n"
            f"{emoji_line}   **{total}** điểm – **{result_type}**\n\n"
            f"`|                |`\n"
            f"`|                |` Bạn chọn **{choice}** và {'thắng' if win else 'thua'} `{amount}` 💵\n"
            f"`|     {roll1} {roll2} {roll3}      |`"
        )

        embed = discord.Embed(description=display, color=color)
        embed.set_footer(text=footer_text)
        await message.edit(content=None, embed=embed)

async def setup(bot):
    await bot.add_cog(TaiXiu(bot, bot.user_balances, bot.user_daily, bot.save_user_data))
