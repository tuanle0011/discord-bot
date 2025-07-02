import discord
from discord.ext import commands
import random
import asyncio

class Blackjack(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.hit_emoji = "🃏"
        self.stand_emoji = "🛑"
        self.cooldowns = {}

    def calculate_hand(self, hand):
        total = 0
        aces = hand.count('A')
        for card in hand:
            if card in ['J', 'Q', 'K']:
                total += 10
            elif card != 'A':
                total += int(card)
        for _ in range(aces):
            total += 11 if total + 11 <= 21 else 1
        return total

    def draw_card(self):
        cards = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        return random.choice(cards)

    @commands.command(aliases=["bj"])
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def blackjack(self, ctx, bet: int):
        user_id = ctx.author.id

        if not hasattr(self.bot, 'user_balances') or user_id not in self.bot.user_balances or self.bot.user_balances[user_id] < bet:
            await ctx.send("❌ Bạn không đủ tiền để đặt cược hoặc số dư của bạn chưa được thiết lập.")
            return

        if bet <= 0:
            await ctx.send("❌ Số tiền cược phải lớn hơn 0.")
            return

        if user_id in self.cooldowns:
            await ctx.send("⏳ Bạn vừa thua. Vui lòng chờ vài giây.")
            return

        self.bot.user_balances[user_id] -= bet
        self.bot.save_user_data()

        player_hand = [self.draw_card(), self.draw_card()]
        dealer_hand = [self.draw_card(), self.draw_card()]
        player_total = self.calculate_hand(player_hand)

        embed = discord.Embed(title="🃏 Blackjack", description=f"**Cược của bạn:** {bet} 💵", color=discord.Color.blue())
        embed.add_field(name="Bài của bạn", value=f"{' '.join(player_hand)}\nTổng: {player_total}", inline=False)
        embed.add_field(name="Bài của nhà cái", value=f"{dealer_hand[0]} ❓", inline=False)
        embed.set_footer(text="🃏 Nhấn 🃏 để rút bài | 🛑 để dừng")
        message = await ctx.send(embed=embed)

        await message.add_reaction(self.hit_emoji)
        await message.add_reaction(self.stand_emoji)

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in [self.hit_emoji, self.stand_emoji] and reaction.message.id == message.id

        while True:
            try:
                reaction, user = await self.bot.wait_for("reaction_add", timeout=30.0, check=check)

                try:
                    await message.remove_reaction(reaction.emoji, user)
                except discord.HTTPException:
                    pass

            except asyncio.TimeoutError:
                embed.set_footer(text="⏱️ Hết thời gian chờ phản hồi.")
                embed.color = discord.Color.red()
                await message.edit(embed=embed)
                try:
                    await message.clear_reactions()
                except discord.Forbidden:
                    pass
                return

            if str(reaction.emoji) == self.hit_emoji:
                player_hand.append(self.draw_card())
                player_total = self.calculate_hand(player_hand)
                embed.set_field_at(0, name="Bài của bạn", value=f"{' '.join(player_hand)}\nTổng: {player_total}", inline=False)
                await message.edit(embed=embed)

                if player_total > 21:
                    embed.set_footer(text="💥 Bạn đã bị quắc! Thua cược.")
                    embed.color = discord.Color.red()
                    await message.edit(embed=embed)
                    self.cooldowns[user_id] = True
                    try:
                        await message.clear_reactions()
                    except discord.Forbidden:
                        pass
                    await asyncio.sleep(5)
                    self.cooldowns.pop(user_id, None)
                    return
            else:
                try:
                    await message.clear_reactions()
                except discord.Forbidden:
                    pass
                break

        dealer_total = self.calculate_hand(dealer_hand)
        embed.set_field_at(1, name="Bài của nhà cái", value=f"{' '.join(dealer_hand)}\nTổng: {dealer_total}", inline=False)
        embed.set_footer(text="Nhà cái đang rút bài...")
        embed.color = discord.Color.blue()
        await message.edit(embed=embed)
        await asyncio.sleep(1.5)

        while dealer_total < 17:
            dealer_hand.append(self.draw_card())
            dealer_total = self.calculate_hand(dealer_hand)
            embed.set_field_at(1, name="Bài của nhà cái", value=f"{' '.join(dealer_hand)}\nTổng: {dealer_total}", inline=False)
            embed.color = discord.Color.blue()
            await message.edit(embed=embed)
            await asyncio.sleep(1.5)

        result = ""
        if dealer_total > 21:
            result = f"🎉 Nhà cái bị quắc! Bạn thắng! Nhận {bet * 2} 💵."
            self.bot.user_balances[user_id] += bet * 2
            embed.color = discord.Color.gold()
        elif player_total > dealer_total:
            result = f"🎉 Bạn thắng! Nhận {bet * 2} 💵."
            self.bot.user_balances[user_id] += bet * 2
            embed.color = discord.Color.gold()
        elif player_total == dealer_total:
            result = "🤝 Hòa. Bạn được hoàn tiền."
            self.bot.user_balances[user_id] += bet
            embed.color = discord.Color.green()
        else:
            result = "💸 Bạn thua rồi!"
            self.cooldowns[user_id] = True
            embed.color = discord.Color.red()

        embed.set_footer(text=result)
        await message.edit(embed=embed)
        self.bot.save_user_data()

        if user_id in self.cooldowns:
            await asyncio.sleep(5)
            self.cooldowns.pop(user_id, None)

async def setup(bot):
    await bot.add_cog(Blackjack(bot))
