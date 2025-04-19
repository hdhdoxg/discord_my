import os
import discord
from discord import ui
from discord.ext import commands

from myserver import server_on

# ตั้งค่า Intents
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.members = True
intents.presences = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ฐานข้อมูล (แนะนำให้ใช้ SQLite หรือ MongoDB ในโปรดักชัน)
user_profiles = {}

class ProfileView(ui.View):
    def __init__(self, player_name):
        super().__init__(timeout=None)
        self.player_name = player_name

    @ui.button(label="📊 เช็คเครดิต", style=discord.ButtonStyle.primary)
    async def check_credits(self, interaction: discord.Interaction, button: ui.Button):
        profile = user_profiles.get(self.player_name, {"credits": 0, "reviews": 0})
        await interaction.response.send_message(
            f"💰 {self.player_name} มีเครดิต: {profile['credits']} คะแนน",
            ephemeral=True
        )

    @ui.button(label="⭐ ให้รีวิว", style=discord.ButtonStyle.success)
    async def add_review(self, interaction: discord.Interaction, button: ui.Button):
        # ตรวจสอบและสร้างโปรไฟล์หากไม่มี
        if self.player_name not in user_profiles:
            user_profiles[self.player_name] = {"credits": 0, "reviews": 0}
        
        # เพิ่มเครดิตและรีวิว
        user_profiles[self.player_name]["credits"] += 1
        user_profiles[self.player_name]["reviews"] += 1

        # อัปเดต Embed
        embed = self.create_profile_embed()
        await interaction.response.edit_message(embed=embed)
        
        # ส่งข้อความยืนยันแบบส่วนตัว
        await interaction.followup.send(
            f"✅ คุณได้ให้รีวิว {self.player_name} (+1 เครดิต)!",
            ephemeral=True
        )

    def create_profile_embed(self):
        profile = user_profiles.get(self.player_name, {"credits": 0, "reviews": 0})
        embed = discord.Embed(
            title=f"📊 โปรไฟล์ {self.player_name}",
            color=discord.Color.green()
        )
        embed.add_field(name="เครดิต", value=f"{profile['credits']} คะแนน", inline=True)
        embed.add_field(name="รีวิวทั้งหมด", value=f"{profile['reviews']} ครั้ง", inline=True)
        return embed

@bot.event
async def on_ready():
    print(f"✅ บอท {bot.user.name} พร้อมทำงาน!")
    await bot.change_presence(activity=discord.Game(name="!โปรไฟล์"))

@bot.command()
async def โปรไฟล์(ctx):
    player_name = ctx.author.name
    view = ProfileView(player_name)
    embed = view.create_profile_embed()
    await ctx.send(embed=embed, view=view)

server_on()


bot.run(os.getenv('TOKEN'))
