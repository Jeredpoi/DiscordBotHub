import discord
from discord.ext import commands, tasks
from discord import app_commands
import asyncio
import sqlite3
from datetime import datetime
from config import Config  # Твои цвета и настройки

# --- Подключение к базе данных ---
conn = sqlite3.connect("private_rooms.db")
cursor = conn.cursor()

# Таблица для настроек приватных комнат
cursor.execute("""
CREATE TABLE IF NOT EXISTS private_room_settings (
    guild_id INTEGER PRIMARY KEY,
    category_id INTEGER,
    join_channel_id INTEGER,
    settings_channel_id INTEGER,
    settings_message_id INTEGER
)
""")
conn.commit()

# Таблица для активных комнат
cursor.execute("""
CREATE TABLE IF NOT EXISTS active_private_rooms (
    guild_id INTEGER,
    channel_id INTEGER,
    owner_id INTEGER,
    created_at TEXT,
    PRIMARY KEY (guild_id, channel_id)
)
""")
conn.commit()


class PrivateRooms(commands.Cog):
    """Система приватных голосовых комнат с кнопками"""

    def __init__(self, bot):
        self.bot = bot

    # -------------------- Настройка системы --------------------
    @app_commands.command(
        name="setup_private_rooms",
        description="🏠 Настроить систему приватных комнат"
    )
    @app_commands.describe(
        category="Категория для приватных комнат",
        join_channel="Канал для присоединения (создание приватной комнаты)"
    )
    async def setup_private_rooms(
        self,
        interaction: discord.Interaction,
        category: discord.CategoryChannel,
        join_channel: discord.VoiceChannel
    ):
        if interaction.user.id != interaction.guild.owner_id:
            await interaction.response.send_message(
                "❌ Только владелец сервера может использовать эту команду!", ephemeral=True
            )
            return
        guild_id = interaction.guild.id
        cursor.execute("""
        INSERT OR REPLACE INTO private_room_settings (guild_id, category_id, join_channel_id)
        VALUES (?, ?, ?)
        """, (guild_id, category.id, join_channel.id))
        conn.commit()

        embed = discord.Embed(
            title="🏠 Система приватных комнат настроена",
            description="Пользователи могут создавать свои приватные голосовые комнаты!",
            color=Config.COLORS['success']
        )
        embed.add_field(name="📁 Категория", value=category.mention, inline=True)
        embed.add_field(name="🚪 Канал для присоединения", value=join_channel.mention, inline=True)
        embed.add_field(
            name="🔧 Как это работает:",
            value="• Пользователь заходит в канал для присоединения\n"
                  "• Автоматически создается приватная комната\n"
                  "• Пользователь становится владельцем комнаты\n"
                  "• Комната удаляется когда становится пустой",
            inline=False
        )
        await interaction.response.send_message(embed=embed)

    # -------------------- Установка канала настроек --------------------
    @app_commands.command(
        name="setsettings_privaterooms",
        description="⚙️ Установить канал для управления приватными комнатами"
    )
    @app_commands.describe(settings_channel="Канал для сообщений с кнопками управления")
    @app_commands.default_permissions(manage_channels=True)
    async def setsettings_privaterooms(self, interaction: discord.Interaction, settings_channel: discord.TextChannel):
        guild_id = interaction.guild.id
        cursor.execute("SELECT * FROM private_room_settings WHERE guild_id = ?", (guild_id,))
        row = cursor.fetchone()
        if not row:
            await interaction.response.send_message("❌ Сначала настройте систему через `/setup_private_rooms`", ephemeral=True)
            return

        category_id, join_channel_id = row[1], row[2]

        # Создаем сообщение с кнопками управления
        view = PrivateRoomButtons(self.bot)
        msg = await settings_channel.send(
            embed=discord.Embed(
                title="⚙️ Управление приватными комнатами",
                description="Используйте кнопки ниже для управления вашей приватной комнатой.",
                color=Config.COLORS['info']
            ),
            view=view
        )

        # Сохраняем ID канала и сообщения для управления
        cursor.execute("""
        UPDATE private_room_settings
        SET settings_channel_id = ?, settings_message_id = ?
        WHERE guild_id = ?
        """, (settings_channel.id, msg.id, guild_id))
        conn.commit()

        await interaction.response.send_message(f"✅ Канал настроек установлен: {settings_channel.mention}", ephemeral=True)

    # -------------------- Создание приватной комнаты --------------------
    async def create_private_room(self, member, category_id):
        guild = member.guild
        category = guild.get_channel(category_id)
        if not category:
            return

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(connect=False),
            member: discord.PermissionOverwrite(connect=True, speak=True, manage_channels=True, move_members=True),
            guild.me: discord.PermissionOverwrite(connect=True, manage_channels=True, move_members=True)
        }

        room_name = f"🏠 {member.display_name}"
        private_room = await guild.create_voice_channel(name=room_name, category=category, overwrites=overwrites)

        # Добавляем в базу
        cursor.execute("""
        INSERT INTO active_private_rooms (guild_id, channel_id, owner_id, created_at)
        VALUES (?, ?, ?, ?)
        """, (guild.id, private_room.id, member.id, datetime.utcnow().isoformat()))
        conn.commit()

        # Перемещаем пользователя
        await member.move_to(private_room)

    # -------------------- Проверка и удаление пустых комнат --------------------
    async def check_empty_room(self, channel, guild_id):
        await asyncio.sleep(2)
        if len(channel.members) == 0:
            try:
                cursor.execute("DELETE FROM active_private_rooms WHERE guild_id = ? AND channel_id = ?", (guild_id, channel.id))
                conn.commit()
                await channel.delete(reason="Приватная комната опустела")
            except:
                pass

    # -------------------- Событие присоединения/покидания --------------------
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        guild_id = member.guild.id
        cursor.execute("SELECT category_id, join_channel_id FROM private_room_settings WHERE guild_id = ?", (guild_id,))
        row = cursor.fetchone()
        if not row:
            return
        category_id, join_channel_id = row

        if after.channel and after.channel.id == join_channel_id:
            await self.create_private_room(member, category_id)

        if before.channel:
            cursor.execute("SELECT * FROM active_private_rooms WHERE guild_id = ? AND channel_id = ?", (guild_id, before.channel.id))
            if cursor.fetchone():
                await self.check_empty_room(before.channel, guild_id)


# -------------------- Модальные окна --------------------
class RenameModal(discord.ui.Modal, title="Переименовать комнату"):
    new_name = discord.ui.TextInput(label="Новое название", max_length=100)

    def __init__(self, channel):
        super().__init__()
        self.channel = channel

    async def on_submit(self, interaction: discord.Interaction):
        try:
            await self.channel.edit(name=self.new_name.value)
            await interaction.response.send_message(f"✅ Комната переименована в {self.new_name.value}", ephemeral=True)
        except discord.Forbidden:
            await interaction.response.send_message("❌ Недостаточно прав!", ephemeral=True)


class LimitModal(discord.ui.Modal, title="Установить лимит участников"):
    limit = discord.ui.TextInput(label="Лимит участников (0 = без лимита)", max_length=3)

    def __init__(self, channel):
        super().__init__()
        self.channel = channel

    async def on_submit(self, interaction: discord.Interaction):
        try:
            limit_value = int(self.limit.value)
            await self.channel.edit(user_limit=limit_value)
            description = "Лимит снят!" if limit_value == 0 else f"Лимит установлен: {limit_value}"
            await interaction.response.send_message(f"✅ {description}", ephemeral=True)
        except:
            await interaction.response.send_message("❌ Некорректное значение!", ephemeral=True)

class PrivateRoomButtons(discord.ui.View):
    """Кнопки управления приватной комнатой"""

    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(label="Переименовать комнату", style=discord.ButtonStyle.primary)
    async def rename_room(self, interaction: discord.Interaction, button: discord.ui.Button):
        member = interaction.user
        channel = member.voice.channel if member.voice else None
        if not channel:
            await interaction.response.send_message("❌ Вы должны быть в своей приватной комнате!", ephemeral=True)
            return
        cursor.execute("SELECT owner_id FROM active_private_rooms WHERE guild_id = ? AND channel_id = ?",
                       (interaction.guild.id, channel.id))
        row = cursor.fetchone()
        if not row or row[0] != member.id:
            await interaction.response.send_message("❌ Только владелец может управлять комнатой!", ephemeral=True)
            return
        await interaction.response.send_modal(RenameModal(channel))

    @discord.ui.button(label="Установить лимит участников", style=discord.ButtonStyle.secondary)
    async def set_limit(self, interaction: discord.Interaction, button: discord.ui.Button):
        member = interaction.user
        channel = member.voice.channel if member.voice else None
        if not channel:
            await interaction.response.send_message("❌ Вы должны быть в своей приватной комнате!", ephemeral=True)
            return
        cursor.execute("SELECT owner_id FROM active_private_rooms WHERE guild_id = ? AND channel_id = ?",
                       (interaction.guild.id, channel.id))
        row = cursor.fetchone()
        if not row or row[0] != member.id:
            await interaction.response.send_message("❌ Только владелец может управлять комнатой!", ephemeral=True)
            return
        await interaction.response.send_modal(LimitModal(channel))

    @discord.ui.button(label="Пригласить пользователя", style=discord.ButtonStyle.success)
    async def invite_user(self, interaction: discord.Interaction, button: discord.ui.Button):
        member = interaction.user
        channel = member.voice.channel if member.voice else None
        if not channel:
            await interaction.response.send_message("❌ Вы должны быть в своей приватной комнате!", ephemeral=True)
            return
        cursor.execute("SELECT owner_id FROM active_private_rooms WHERE guild_id = ? AND channel_id = ?",
                       (interaction.guild.id, channel.id))
        row = cursor.fetchone()
        if not row or row[0] != member.id:
            await interaction.response.send_message("❌ Только владелец может управлять комнатой!", ephemeral=True)
            return
        await interaction.response.send_modal(UserModal(channel, action="invite"))

    @discord.ui.button(label="Исключить пользователя", style=discord.ButtonStyle.danger)
    async def kick_user(self, interaction: discord.Interaction, button: discord.ui.Button):
        member = interaction.user
        channel = member.voice.channel if member.voice else None
        if not channel:
            await interaction.response.send_message("❌ Вы должны быть в своей приватной комнате!", ephemeral=True)
            return
        cursor.execute("SELECT owner_id FROM active_private_rooms WHERE guild_id = ? AND channel_id = ?",
                       (interaction.guild.id, channel.id))
        row = cursor.fetchone()
        if not row or row[0] != member.id:
            await interaction.response.send_message("❌ Только владелец может управлять комнатой!", ephemeral=True)
            return
        await interaction.response.send_modal(UserModal(channel, action="kick"))

    @discord.ui.button(label="Заблокировать пользователя", style=discord.ButtonStyle.danger)
    async def ban_user(self, interaction: discord.Interaction, button: discord.ui.Button):
        member = interaction.user
        channel = member.voice.channel if member.voice else None
        if not channel:
            await interaction.response.send_message("❌ Вы должны быть в своей приватной комнате!", ephemeral=True)
            return
        cursor.execute("SELECT owner_id FROM active_private_rooms WHERE guild_id = ? AND channel_id = ?",
                       (interaction.guild.id, channel.id))
        row = cursor.fetchone()
        if not row or row[0] != member.id:
            await interaction.response.send_message("❌ Только владелец может управлять комнатой!", ephemeral=True)
            return
        await interaction.response.send_modal(UserModal(channel, action="ban"))

    @discord.ui.button(label="Разблокировать пользователя", style=discord.ButtonStyle.success)
    async def unban_user(self, interaction: discord.Interaction, button: discord.ui.Button):
        member = interaction.user
        channel = member.voice.channel if member.voice else None
        if not channel:
            await interaction.response.send_message("❌ Вы должны быть в своей приватной комнате!", ephemeral=True)
            return
        cursor.execute("SELECT owner_id FROM active_private_rooms WHERE guild_id = ? AND channel_id = ?",
                       (interaction.guild.id, channel.id))
        row = cursor.fetchone()
        if not row or row[0] != member.id:
            await interaction.response.send_message("❌ Только владелец может управлять комнатой!", ephemeral=True)
            return
        await interaction.response.send_modal(UserModal(channel, action="unban"))


class UserModal(discord.ui.Modal):
    """Модальное окно для ввода пользователя и действия"""

    def __init__(self, channel, action):
        title_map = {
            "invite": "Пригласить пользователя",
            "kick": "Исключить пользователя",
            "ban": "Заблокировать пользователя",
            "unban": "Разблокировать пользователя"
        }
        super().__init__(title=title_map[action])
        self.channel = channel
        self.action = action
        self.user_input = discord.ui.TextInput(label="Укажите пользователя (упоминание или ID)", style=discord.TextStyle.short)
        self.add_item(self.user_input)

    async def on_submit(self, interaction: discord.Interaction):
        guild = interaction.guild
        try:
            user_id = int(self.user_input.value.strip("<@!>"))
            user = guild.get_member(user_id)
            if not user:
                await interaction.response.send_message("❌ Пользователь не найден", ephemeral=True)
                return
        except:
            await interaction.response.send_message("❌ Некорректный пользователь", ephemeral=True)
            return

        overwrite = discord.PermissionOverwrite()
        if self.action == "invite":
            overwrite.connect = True
            overwrite.speak = True
            overwrite.view_channel = True
            await self.channel.set_permissions(user, overwrite=overwrite)
            await interaction.response.send_message(f"✅ {user.mention} приглашен в комнату", ephemeral=True)
        elif self.action == "kick":
            if user in self.channel.members:
                await user.move_to(None)
            overwrite.connect = False
            await self.channel.set_permissions(user, overwrite=overwrite)
            await interaction.response.send_message(f"👢 {user.mention} исключен из комнаты", ephemeral=True)
        elif self.action == "ban":
            if user in self.channel.members:
                await user.move_to(None)
            overwrite.connect = False
            overwrite.view_channel = False
            await self.channel.set_permissions(user, overwrite=overwrite)
            await interaction.response.send_message(f"🔨 {user.mention} заблокирован в комнате", ephemeral=True)
        elif self.action == "unban":
            await self.channel.set_permissions(user, overwrite=None)
            await interaction.response.send_message(f"🔓 {user.mention} разблокирован", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(PrivateRooms(bot))