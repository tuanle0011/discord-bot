import discord
from discord.ext import commands
import random
import asyncio

class DuaNgua(commands.Cog):
    def __init__(self, bot, user_balances, user_daily, save_user_data):
        self.bot = bot
        self.user_balances = user_balances
        self.user_daily = user_daily
        self.save_user_data = save_user_data
        self.cooldowns = {}

    def ensure_user(self, user_id):
        if user_id not in self.user_balances:
            self.user_balances[user_id] = 1000
            self.save_user_data()

    def generate_initial_horse_tracks(self, num_horses=5, min_len=15, max_len=25):
        return [random.randint(min_len, max_len) for _ in range(num_horses)]

    def update_horse_tracks(self, current_lengths):
        return [max(0, length - random.randint(1, 3)) for length in current_lengths]

    def create_race_embed(self, amount, chosen_horse, current_lengths, status="Đang chạy..."):
        embed = discord.Embed(title="୨୧ ⌗ **___ĐUA NGỰA___** 🏇", color=0x0099ff)
        embed.add_field(name="💰 Cược", value=f"{amount} 💵", inline=True)
        embed.add_field(name="🔢 Ngựa bạn chọn", value=f"Ngựa số **{chosen_horse}**", inline=True)
        embed.add_field(name="⌛ Trạng thái", value=status, inline=False)

        track_display = ""
        for i, length in enumerate(current_lengths):
            horse_emoji = "🐎"
            if i + 1 == chosen_horse:
                horse_emoji = "🏇"

            if length <= 0:
                track_display += f"**{i+1}**.🏁{horse_emoji}\n"
            else:
                track_display += f"**{i+1}**.{'-' * length}{horse_emoji}\n"

        embed.add_field(name="🐴 Đường đua", value=track_display, inline=False)
        embed.set_footer(text="code made by @minhtuan011")
        return embed

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def duangua(self, ctx, amount: int, horse: int):
        user_id = ctx.author.id
        self.ensure_user(user_id)

        if not (1 <= horse <= 5):
            await ctx.send("🐎 Bạn chỉ có thể chọn số ngựa từ **1** đến **5**.")
            return
        if amount <= 0:
            await ctx.send("❌ Số tiền cược phải lớn hơn 0.")
            return
        if self.user_balances[user_id] < amount:
            await ctx.send("❌ Bạn không đủ tiền để đặt cược.")
            return

        self.user_balances[user_id] -= amount
        self.save_user_data()

        current_lengths = self.generate_initial_horse_tracks()
        message = await ctx.send(embed=self.create_race_embed(amount, horse, current_lengths))
        max_updates = max(current_lengths) + 5
        winner_index = -1

        for _ in range(max_updates):
            await asyncio.sleep(1.5)
            current_lengths = self.update_horse_tracks(current_lengths)
            finished_horses_in_round = [idx for idx, length in enumerate(current_lengths) if length <= 0]
            if finished_horses_in_round:
                winner_index = random.choice(finished_horses_in_round)
                break
            await message.edit(embed=self.create_race_embed(amount, horse, current_lengths))

        if winner_index == -1:
            min_track_len = float('inf')
            leading_horses = []
            for idx, length in enumerate(current_lengths):
                if length < min_track_len:
                    min_track_len = length
                    leading_horses = [idx]
                elif length == min_track_len:
                    leading_horses.append(idx)
            winner_index = random.choice(leading_horses)

        final_tracks_display = []
        for i, length in enumerate(current_lengths):
            horse_emoji = "🐎"
            if i + 1 == horse:
                horse_emoji = "🏇"
            if i == winner_index:
                final_tracks_display.append(f"**{i+1}**.🏁{horse_emoji} **<-- WINNER!**")
            elif length <= 0:
                final_tracks_display.append(f"**{i+1}**.🏁{horse_emoji}")
            else:
                final_tracks_display.append(f"**{i+1}**.{'-' * length}{horse_emoji}")

        final_embed = discord.Embed(title="୨୧ ⌗ **___ĐUA NGỰA___** 🏇", color=0x2ECC71)
        final_embed.add_field(name="💰 Cược", value=f"{amount} 💵", inline=True)
        final_embed.add_field(name="🔢 Ngựa bạn chọn", value=f"Ngựa số **{horse}**", inline=True)
        final_embed.add_field(name="⌛ Trạng thái", value="🏆 Đã Kết Thúc", inline=False)
        final_embed.add_field(name="🐴 Kết quả", value="\n".join(final_tracks_display), inline=False)

        if horse == (winner_index + 1):
            win_amount = amount * 2
            self.user_balances[user_id] += win_amount
            final_embed.set_footer(text=f"🎉 Bạn thắng! Nhận {win_amount} 💵\nSố dư hiện tại: {self.user_balances[user_id]} 💵")
            final_embed.color = discord.Color.gold()
        else:
            final_embed.set_footer(text=f"❌ Bạn thua {amount} 💵 - Ngựa số {winner_index + 1} thắng cuộc\nSố dư hiện tại: {self.user_balances[user_id]} 💵")
            final_embed.color = discord.Color.red()

        self.save_user_data()
        await message.edit(embed=final_embed)

async def setup(bot):
    await bot.add_cog(DuaNgua(bot, bot.user_balances, bot.user_daily, bot.save_user_data))
