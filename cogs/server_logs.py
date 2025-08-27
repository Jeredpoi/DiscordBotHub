import discord
from discord.ext import commands
from discord import app_commands
import sqlite3
from datetime import datetime
from config import Config

DB_PATH = "logs.db"

# ------------------ Инициализация базы ------------------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS log_channels (
            guild_id INTEGER,
            channel_id INTEGER,
            log_type TEXT,
            PRIMARY KEY(guild_id, log_type)
        )
    """)
    conn.commit()
    conn.close()

init_db()

class ServerLogs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.voice_times = {}  # Для расчета длительности в голосе

    # ------------------ Вспомогательные методы ------------------
    async def get_log_channel(self, guild_id, log_type):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT channel_id FROM log_channels WHERE guild_id=? AND log_type=?", (guild_id, log_type))
        result = cursor.fetchone()
        conn.close()
        if result:
            return self.bot.get_channel(result[0])
        return None

    async def send_log(self, guild_id: int, log_type: str, embed: discord.Embed):
        channel = await self.get_log_channel(guild_id, log_type)
        if channel:
            try:
                await channel.send(embed=embed)
            except Exception as e:
                print(f"Ошибка отправки лога {log_type}: {e}")

    # ------------------ Команда установки логов ------------------
    @app_commands.command(name="set_log_channel", description="📋 Настроить канал для логов")
    @app_commands.describe(log_type="Тип логов", channel="Канал для логов")
    @app_commands.choices(log_type=[
        app_commands.Choice(name="Сообщения", value="messages"),
        app_commands.Choice(name="Голосовые", value="voice"),
        app_commands.Choice(name="Модерация", value="moderation"),
        app_commands.Choice(name="Роли", value="roles")
    ])
    @app_commands.default_permissions(manage_guild=True)
    async def set_log_channel(self, interaction: discord.Interaction, log_type: app_commands.Choice[str], channel: discord.TextChannel):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("REPLACE INTO log_channels (guild_id, log_type, channel_id) VALUES (?, ?, ?)",
                       (interaction.guild.id, log_type.value, channel.id))
        conn.commit()
        conn.close()
        embed = discord.Embed(
            title="✅ Логи настроены",
            description=f"Теперь логи типа **{log_type.name}** будут отправляться в {channel.mention}",
            color=Config.COLORS['success']
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    # ------------------ Логи сообщений ------------------
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.bot: return
        embed = discord.Embed(title="🗑️ Сообщение удалено", color=Config.COLORS['error'], timestamp=datetime.utcnow())
        embed.add_field(name="👤 Автор", value=f"{message.author} (`{message.author.id}`)")
        embed.add_field(name="📺 Канал", value=f"{message.channel} (`{message.channel.id}`)")
        content = message.content[:1000] if message.content else "*Без текста*"
        embed.add_field(name="📝 Содержимое", value=f"```{content}```" if content != "*Без текста*" else content)
        embed.add_field(name="📎 Вложения", value=str(len(message.attachments)))
        embed.add_field(name="🔗 Упоминания", value=", ".join([u.mention for u in message.mentions]) or "Нет")
        await self.send_log(message.guild.id, "messages", embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.author.bot or before.content == after.content: return
        embed = discord.Embed(title="✏️ Сообщение отредактировано", color=Config.COLORS['warning'], timestamp=datetime.utcnow())
        embed.add_field(name="👤 Автор", value=f"{before.author} (`{before.author.id}`)")
        embed.add_field(name="📺 Канал", value=f"{before.channel} (`{before.channel.id}`)")
        embed.add_field(name="📝 Старое", value=f"```{before.content[:500]}```" if before.content else "*Без текста*")
        embed.add_field(name="📝 Новое", value=f"```{after.content[:500]}```" if after.content else "*Без текста*")
        embed.add_field(name="📎 Вложения", value=str(len(after.attachments)))
        embed.add_field(name="🔗 Упоминания", value=", ".join([u.mention for u in after.mentions]) or "Нет")
        await self.send_log(before.guild.id, "messages", embed)

    # ------------------ Логи голосовых ------------------
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if before.channel != after.channel:
            now = datetime.utcnow()
            embed = discord.Embed(title="🔊 Голосовое событие", color=Config.COLORS['info'], timestamp=now)
            embed.add_field(name="👤 Пользователь", value=f"{member}")
            if before.channel is None and after.channel is not None:
                embed.title = "🔊 Присоединился к голосовому каналу"
                embed.add_field(name="📺 Канал", value=f"{after.channel} (`{after.channel.id}`)")
                self.voice_times[member.id] = now
            elif before.channel is not None and after.channel is None:
                embed.title = "🔇 Покинул голосовой канал"
                embed.add_field(name="📺 Канал", value=f"{before.channel} (`{before.channel.id}`)")
                start_time = self.voice_times.pop(member.id, None)
                if start_time:
                    duration = now - start_time
                    embed.add_field(name="⏱ Длительность в голосе", value=str(duration).split(".")[0])
            elif before.channel != after.channel:
                embed.title = "🔄 Переключение между каналами"
                embed.add_field(name="📺 Из канала", value=f"{before.channel} (`{before.channel.id}`)")
                embed.add_field(name="📺 В канал", value=f"{after.channel} (`{after.channel.id}`)")
            await self.send_log(member.guild.id, "voice", embed)

    # ------------------ Логи модерации ------------------
    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        embed = discord.Embed(title="🔨 Пользователь заблокирован", color=Config.COLORS['error'], timestamp=datetime.utcnow())
        embed.add_field(name="👤 Пользователь", value=f"{user} (`{user.id}`)")
        try:
            ban_info = await guild.fetch_ban(user)
            if ban_info.reason:
                embed.add_field(name="📋 Причина", value=ban_info.reason)
        except:
            embed.add_field(name="📋 Причина", value="Не указана")
        member = guild.get_member(user.id)
        if member:
            embed.add_field(name="🎭 Роли до бана", value=", ".join([r.name for r in member.roles if r != guild.default_role]) or "Нет")
        await self.send_log(guild.id, "moderation", embed)

    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):
        embed = discord.Embed(title="🔓 Пользователь разблокирован", color=Config.COLORS['success'], timestamp=datetime.utcnow())
        embed.add_field(name="👤 Пользователь", value=f"{user} (`{user.id}`)")
        await self.send_log(guild.id, "moderation", embed)

    # ------------------ Логи ролей ------------------
    @commands.Cog.listener()
    async def on_guild_role_create(self, role):
        embed = discord.Embed(title="🎭 Роль создана", color=role.color if role.color != discord.Color.default() else Config.COLORS['success'], timestamp=datetime.utcnow())
        embed.add_field(name="📝 Название", value=role.name)
        embed.add_field(name="🔢 ID", value=str(role.id))
        embed.add_field(name="🎨 Цвет", value=str(role.color))
        perms = [p[0] for p in role.permissions if p[1]]
        embed.add_field(name="⚙ Разрешения", value=", ".join(perms) if perms else "Нет")
        await self.send_log(role.guild.id, "roles", embed)

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
        embed = discord.Embed(title="🗑️ Роль удалена", color=Config.COLORS['error'], timestamp=datetime.utcnow())
        embed.add_field(name="📝 Название", value=role.name)
        embed.add_field(name="🔢 ID", value=str(role.id))
        embed.add_field(name="🎨 Цвет", value=str(role.color))
        await self.send_log(role.guild.id, "roles", embed)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if before.roles != after.roles:
            added = set(after.roles) - set(before.roles)
            removed = set(before.roles) - set(after.roles)
            if added or removed:
                embed = discord.Embed(title="🎭 Роли изменены", color=Config.COLORS['info'], timestamp=datetime.utcnow())
                embed.add_field(name="👤 Пользователь", value=f"{after}")
                if added:
                    embed.add_field(name="➕ Добавлены роли", value=", ".join([r.name for r in added]))
                if removed:
                    embed.add_field(name="➖ Удалены роли", value=", ".join([r.name for r in removed]))
                await self.send_log(after.guild.id, "roles", embed)

# ================== Глобальные переменные ==================
logs_cog: ServerLogs = None  # тут будет храниться объект COG

# ================== Функция для вызова из других файлов ==================
async def log_event(guild_id: int, log_type: str, embed: discord.Embed):
    if logs_cog:
        await logs_cog.send_log(guild_id, log_type, embed)

# ================== setup ==================
async def setup(bot):
    global logs_cog
    logs_cog = ServerLogs(bot)
    await bot.add_cog(logs_cog)

    # Проверяем и выводим в консоль каждый тип логов
    log_types = [("messages", "Текстовые логи"),
                 ("voice", "Голосовые логи"),
                 ("moderation", "Модераторские логи"),
                 ("roles", "Логи ролей")]

    for log_type, name in log_types:
        try:
            print(f"🔑 {name} загружены успешно")
        except Exception as e:
            print(f"❌ Ошибка при загрузке {name}: {e}")