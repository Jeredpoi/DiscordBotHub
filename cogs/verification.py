import discord
from discord.ext import commands
from discord import app_commands
import sqlite3

class VerificationView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        # кнопка с callback
        button = discord.ui.Button(label="Верифицироваться", style=discord.ButtonStyle.success, custom_id="verify_button")
        button.callback = self.verify_callback
        self.add_item(button)

    async def verify_callback(self, interaction: discord.Interaction):
        member = interaction.user
        guild = interaction.guild

        role_verified = discord.utils.get(guild.roles, name="Верифицирован")
        role_unverified = discord.utils.get(guild.roles, name="Unverified")

        if role_verified and role_unverified:
            await member.remove_roles(role_unverified)
            await member.add_roles(role_verified)
            await interaction.response.send_message("🎉 Ты успешно верифицировался!", ephemeral=True)
        else:
            await interaction.response.send_message(
                "⚠️ Роли Verified/Unverified не найдены. Обратись к администратору.",
                ephemeral=True
            )


class Verification(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.dbpath = "database.db"
        self.role_verified = "Верифицирован"
        self.role_unverified = "Unverified"

        self.create_table()

    def create_table(self):
        with sqlite3.connect(self.dbpath) as db:
            cursor = db.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS verification (
                    guild_id INTEGER PRIMARY KEY,
                    channel_id INTEGER,
                    message_id INTEGER
                )
            """)
            db.commit()

    @app_commands.command(name="send_verification", description="📩 Отправить сообщение для верификации")
    @app_commands.describe(channel="Канал, в который отправить сообщение для верификации")
    async def send_verification(self, interaction: discord.Interaction, channel: discord.TextChannel):
        embed = discord.Embed(
            title="✅ Верификация",
            description="Нажми кнопку ниже, чтобы пройти верификацию и получить доступ ко всем каналам.",
            color=discord.Color.green()
        )

        view = VerificationView()
        msg = await channel.send(embed=embed, view=view)

        # сохраняем канал и ID сообщения в БД
        with sqlite3.connect(self.dbpath) as db:
            cursor = db.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO verification (guild_id, channel_id, message_id)
                VALUES (?, ?, ?)
            """, (interaction.guild.id, channel.id, msg.id))
            db.commit()

        # подключаем persistent view
        self.bot.add_view(view, message_id=msg.id)

        await interaction.response.send_message(f"📨 Сообщение верификации отправлено в {channel.mention}", ephemeral=True)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """Авто-выдача роли Unverified"""
        role = discord.utils.get(member.guild.roles, name=self.role_unverified)
        if role:
            await member.add_roles(role)
            print(f"✅ {member.name} получил роль Unverified")
        else:
            print("❌ Роль 'Unverified' не найдена!")

    @commands.Cog.listener()
    async def on_ready(self):
        """Восстановление persistent view после перезапуска бота"""
        await self.bot.wait_until_ready()
        with sqlite3.connect(self.dbpath) as db:
            cursor = db.cursor()
            cursor.execute("SELECT guild_id, channel_id, message_id FROM verification")
            rows = cursor.fetchall()

        for guild_id, channel_id, message_id in rows:
            guild = self.bot.get_guild(guild_id)
            if not guild:
                continue
            channel = guild.get_channel(channel_id)
            if not channel:
                continue
            try:
                await channel.fetch_message(message_id)
                view = VerificationView()
                self.bot.add_view(view, message_id=message_id)
                print(f"🔄 Верификация восстановлена для {guild.name}")
            except Exception as e:
                print(f"⚠️ Не удалось восстановить верификацию в {guild_id}: {e}")


async def setup(bot: commands.Bot):
    await bot.add_cog(Verification(bot))