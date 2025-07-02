import discord
from discord.ext import commands, tasks
import random
import datetime
import pytz

class Ancap(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ancap_data = {
            "last_used": {},
            "daily_count": {}
        }
        self.last_reset_date = ""
        self.reset_ancap_daily.start()

    @commands.command(name="ancap")
    @commands.cooldown(1, 5 * 60, commands.BucketType.user)  # mỗi 5 phút
    async def ancap(self, ctx):
        user_id = ctx.author.id
        now = datetime.datetime.now(pytz.timezone("Asia/Ho_Chi_Minh"))
        today_str = now.strftime("%Y-%m-%d")

        # Reset nếu qua ngày mới
        if self.ancap_data["daily_count"].get(user_id, {}).get("date") != today_str:
            self.ancap_data["daily_count"][user_id] = {"date": today_str, "count": 0}

        if self.ancap_data["daily_count"][user_id]["count"] >= 2:
            return await ctx.send("❌ Bạn đã dùng `.ancap` 2 lần hôm nay rồi.")

        # Danh sách người chơi khác
        potential_targets = [uid for uid in self.bot.user_balances if uid != user_id]
        if not potential_targets:
            return await ctx.send("❌ Không có ai để bạn an cắp cả.")

        # Thử tối đa 10 lần tìm người có 100–200 tiền
        for _ in range(10):
            target_id = random.choice(potential_targets)
            balance = self.bot.user_balances.get(target_id, 0)
            if 100 <= balance <= 200:
                amount = random.randint(10, 50)

                self.bot.user_balances[target_id] -= amount
                self.bot.user_balances[user_id] = self.bot.user_balances.get(user_id, 0) + amount
                self.bot.save_user_data()

                try:
                    target_user = await self.bot.fetch_user(target_id)
                    target_name = target_user.name
                except:
                    target_name = f"ID {target_id}"

                self.ancap_data["daily_count"][user_id]["count"] += 1
                return await ctx.send(f"🦹 Bạn vừa an cắp {amount} 💵 từ **{target_name}**!")

        return await ctx.send("❌ Không tìm được ai có từ 100 đến 200 💵 để an cắp.")

    @tasks.loop(minutes=5)
    async def reset_ancap_daily(self):
        now = datetime.datetime.now(pytz.timezone("Asia/Ho_Chi_Minh"))
        today_str = now.strftime("%Y-%m-%d")
        if today_str != self.last_reset_date:
            self.ancap_data["daily_count"] = {}
            self.last_reset_date = today_str

    @reset_ancap_daily.before_loop
    async def before_reset(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(Ancap(bot))
