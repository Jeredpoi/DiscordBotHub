import discord
import asyncio
import sqlite3
import json
from discord.ext import commands
from discord import app_commands
from datetime import datetime, timedelta
from config import Config

# Хранилище предупреждений (в реальном боте используйте базу данных)
warnings_storage = {}
muted_users = {}
DB_BAN = sqlite3.connect("db_ban.sqlite3")  # глобальная база для банов
DB_BAN.execute("""
CREATE TABLE IF NOT EXISTS bans (
    guild_id INTEGER,
    user_id INTEGER,
    roles TEXT,
    reason TEXT,
    timestamp REAL,
    duration TEXT,
    PRIMARY KEY(guild_id, user_id)
)
""")
DB_BAN.commit()

class Moderation(commands.Cog):
    """Команды модерации сервера"""
    
    def __init__(self, bot):
        self.bot = bot
    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """Проверка прав для команд модерации"""
        return True  # Проверки прав будут в каждой команде отдельно
    
    @app_commands.command(name="kick", description="👢 Исключить участника с сервера")
    @app_commands.describe(user="Пользователь для исключения", reason="Причина исключения")
    @app_commands.default_permissions(kick_members=True)
    async def kick(self, interaction: discord.Interaction, user: discord.Member, reason: str = "Не указана"):
        """Исключает пользователя с сервера"""
        # Проверки
        if user.id == interaction.user.id:
            await interaction.response.send_message("❌ Вы не можете исключить самого себя!", ephemeral=True)
            return
        
        if user.id == self.bot.user.id:
            await interaction.response.send_message("❌ Я не могу исключить самого себя!", ephemeral=True)
            return
        
        if user.top_role >= interaction.user.top_role:
            await interaction.response.send_message("❌ Вы не можете исключить пользователя с равной или более высокой ролью!", ephemeral=True)
            return
        
        try:
            await user.kick(reason=f"Исключён {interaction.user}: {reason}")
            
            embed = discord.Embed(
                title="👢 Пользователь исключён",
                description=f"**Пользователь:** {user.mention}\n**Модератор:** {interaction.user.mention}\n**Причина:** {reason}",
                color=Config.COLORS['moderation']
            )
            embed.timestamp = datetime.now()
            
            await interaction.response.send_message(embed=embed)
            
        except discord.Forbidden:
            await interaction.response.send_message("❌ У меня недостаточно прав для исключения этого пользователя!", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Произошла ошибка: {str(e)}", ephemeral=True)

    @app_commands.command(
        name="ban",
        description="🔨 Добавить пользователя в черный список (роль-блокировка)"
    )
    @app_commands.describe(
        user="Пользователь для блокировки",
        reason="Причина блокировки",
        duration="Время блокировки (например: 1d2h30m)"
    )
    @app_commands.default_permissions(manage_roles=True)
    async def ban(self, interaction: discord.Interaction, user: discord.Member, reason: str = "Не указана",
                  duration: str = None):
        guild = interaction.guild

        # --- Внутренний парсер времени ---
        def parse_time(time_str: str) -> int:
            units = {"d": 86400, "h": 3600, "m": 60, "s": 1}
            seconds = 0
            num = ""
            for char in time_str:
                if char.isdigit():
                    num += char
                elif char in units and num:
                    seconds += int(num) * units[char]
                    num = ""
            return seconds

        # --- Проверки ---
        if not interaction.user.guild_permissions.manage_roles:
            await interaction.response.send_message("❌ У вас нет прав!", ephemeral=True)
            return
        if user.id == interaction.user.id:
            await interaction.response.send_message("❌ Нельзя заблокировать себя!", ephemeral=True)
            return
        if user.top_role >= interaction.user.top_role:
            await interaction.response.send_message("❌ У пользователя слишком высокая роль!", ephemeral=True)
            return

        # --- Роль "Заблокирован" ---
        blacklist_role = discord.utils.get(guild.roles, name="Заблокирован")
        if blacklist_role is None:
            blacklist_role = await guild.create_role(
                name="Заблокирован",
                color=discord.Color.dark_grey(),
                permissions=discord.Permissions.none(),
                reason="Создана роль для блокировки"
            )
            for channel in guild.channels:
                try:
                    await channel.set_permissions(blacklist_role, send_messages=False, speak=False, add_reactions=False)
                except:
                    pass

        if blacklist_role in user.roles:
            await interaction.response.send_message("❌ Пользователь уже заблокирован!", ephemeral=True)
            return

        # --- Сохраняем роли пользователя в глобальную БД ---
        roles_to_remove = [r for r in user.roles if r != guild.default_role]
        role_names = [r.name for r in roles_to_remove]
        role_ids = [r.id for r in roles_to_remove]
        cursor = DB_BAN.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO bans (guild_id, user_id, roles) VALUES (?, ?, ?)",
            (guild.id, user.id, ",".join(map(str, role_ids)))
        )
        DB_BAN.commit()

        # --- Снимаем все роли ---
        if roles_to_remove:
            await user.remove_roles(*roles_to_remove, reason=f"Блокировка: {reason}")
            print(f"[BAN] Пользователь {user} — сняты роли: {', '.join(role_names)}")

        # --- Выдаём только роль "Заблокирован" ---
        await user.add_roles(blacklist_role, reason=f"Блокировка: {reason}")
        print(f"[BAN] Пользователь {user} получил роль 'Заблокирован'")

        # --- Embed уведомление ---
        embed = discord.Embed(
            title="🔨 Пользователь заблокирован",
            description=f"**Пользователь:** {user.mention}\n"
                        f"**Модератор:** {interaction.user.mention}\n"
                        f"**Причина:** {reason}\n"
                        f"**Длительность:** {'Навсегда' if not duration else duration}",
            color=discord.Color.dark_red()
        )
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.timestamp = datetime.now()
        await interaction.response.send_message(embed=embed, ephemeral=True)

        # --- Таймер автоматического разбанa ---
        if duration:
            seconds = parse_time(duration)
            if seconds > 0:
                async def remove_role_later():
                    await asyncio.sleep(seconds)
                    member = guild.get_member(user.id)
                    if member and blacklist_role in member.roles:
                        await member.remove_roles(blacklist_role, reason="Автоматический разбан")
                        print(f"[UNBAN] Пользователь {member} разбанен автоматически после {duration}.")

                        # --- Восстановление прежних ролей ---
                        roles_to_restore = cursor.execute(
                            "SELECT roles FROM bans WHERE guild_id = ? AND user_id = ?",
                            (guild.id, user.id)
                        ).fetchone()
                        restored_names = []
                        if roles_to_restore and roles_to_restore[0]:
                            role_ids_restore = [int(rid) for rid in roles_to_restore[0].split(",")]
                            for rid in role_ids_restore:
                                role = guild.get_role(rid)
                                if role:
                                    await member.add_roles(role, reason="Восстановление ролей после бана")
                                    restored_names.append(role.name)
                        if restored_names:
                            print(f"[UNBAN] Пользователю {member} восстановлены роли: {', '.join(restored_names)}")

                asyncio.create_task(remove_role_later())

    @app_commands.command(
        name="unban",
        description="🔓 Снять чёрный список с пользователя"
    )
    @app_commands.describe(user="Пользователь для разблокировки")
    @app_commands.default_permissions(ban_members=True)
    async def unban(self, interaction: discord.Interaction, user: discord.Member):
        guild = interaction.guild
        black_role = discord.utils.get(guild.roles, name="Заблокирован")

        if not black_role:
            await interaction.response.send_message("❌ Роль 'Заблокирован' не найдена!", ephemeral=True)
            return

        if black_role not in user.roles:
            await interaction.response.send_message("❌ Этот пользователь не в чёрном списке!", ephemeral=True)
            return

        # Снимаем роль "Заблокирован"
        try:
            await user.remove_roles(black_role, reason=f"Разблокирован {interaction.user}")
            print(f"[UNBAN] Пользователь {user} снята роль 'Заблокирован' модератором {interaction.user}.")
        except discord.Forbidden:
            await interaction.response.send_message("❌ У меня нет прав, чтобы снять роль!", ephemeral=True)
            return

        # Восстанавливаем прежние роли из БД
        cursor = DB_BAN.cursor()
        roles_record = cursor.execute(
            "SELECT roles FROM bans WHERE guild_id = ? AND user_id = ?",
            (guild.id, user.id)
        ).fetchone()

        restored_names = []
        if roles_record and roles_record[0]:
            role_ids_restore = [int(rid) for rid in roles_record[0].split(",")]
            for rid in role_ids_restore:
                role = guild.get_role(rid)
                if role:
                    await user.add_roles(role, reason="Восстановление ролей после бана")
                    restored_names.append(role.name)

        if restored_names:
            print(f"[UNBAN] Пользователю {user} восстановлены роли: {', '.join(restored_names)}")

        # Embed уведомление
        embed = discord.Embed(
            title="🔓 Пользователь разблокирован",
            description=f"**Пользователь:** {user.mention}\n**Модератор:** {interaction.user.mention}\n",
            color=discord.Color.green()
        )
        embed.timestamp = datetime.now()

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="mute", description="🔇 Выдать роль 'Muted' пользователю")
    @app_commands.describe(user="Пользователь для заглушения", duration="Длительность в минутах",
                           reason="Причина заглушения")
    @app_commands.default_permissions(moderate_members=True)
    async def mute(self, interaction: discord.Interaction, user: discord.Member, duration: int = 10,
                   reason: str = "Не указана"):
        if user.id == interaction.user.id:
            await interaction.response.send_message("❌ Вы не можете заглушить самого себя!", ephemeral=True)
            return

        if user.id == self.bot.user.id:
            await interaction.response.send_message("❌ Я не могу заглушить самого себя!", ephemeral=True)
            return

        guild = interaction.guild

        # ищем или создаём роль Muted
        muted_role = discord.utils.get(guild.roles, name="Muted")
        if muted_role is None:
            muted_role = await guild.create_role(name="Muted", color=discord.Color.dark_grey(),
                                                 reason="Для системы мута")

            # запрещаем отправку сообщений во всех каналах
            for channel in guild.channels:
                try:
                    await channel.set_permissions(muted_role, send_messages=False, speak=False, add_reactions=False)
                except:
                    pass

        # выдаём роль
        await user.add_roles(muted_role, reason=f"Мут от {interaction.user}: {reason}")

        embed = discord.Embed(
            title="🔇 Пользователь заглушен",
            description=f"**Пользователь:** {user.mention}\n**Модератор:** {interaction.user.mention}\n**Длительность:** {duration} минут\n**Причина:** {reason}",
            color=discord.Color.orange()
        )
        embed.timestamp = discord.utils.utcnow()
        await interaction.response.send_message(embed=embed)

        # снимаем роль через duration минут
        await asyncio.sleep(duration * 60)
        if muted_role in user.roles:
            await user.remove_roles(muted_role, reason="Время мута истекло")
            try:
                await user.send(f"✅ Ваш мут на сервере **{guild.name}** истёк.")
            except:
                pass

    @app_commands.command(name="unmute", description="🔊 Снять заглушение")
    @app_commands.describe(user="Пользователь для снятия заглушения")
    @app_commands.default_permissions(moderate_members=True)
    async def unmute(self, interaction: discord.Interaction, user: discord.Member):
        """Снимает заглушение с пользователя (удаляет роль Muted)"""
        guild = interaction.guild
        muted_role = discord.utils.get(guild.roles, name="Muted")

        if muted_role is None:
            await interaction.response.send_message("❌ Роль `Muted` не найдена на сервере!", ephemeral=True)
            return

        if muted_role not in user.roles:
            await interaction.response.send_message("ℹ️ У пользователя нет роли `Muted`.", ephemeral=True)
            return

        try:
            await user.remove_roles(muted_role, reason=f"Заглушение снято {interaction.user}")

            embed = discord.Embed(
                title="🔊 Заглушение снято",
                description=f"**Пользователь:** {user.mention}\n**Модератор:** {interaction.user.mention}",
                color=discord.Color.green()
            )
            embed.timestamp = discord.utils.utcnow()

            await interaction.response.send_message(embed=embed)

        except discord.Forbidden:
            await interaction.response.send_message("❌ У меня недостаточно прав для снятия заглушения!", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Произошла ошибка: {str(e)}", ephemeral=True)

    @app_commands.command(name="warn", description="⚠️ Выдать предупреждение")
    @app_commands.describe(user="Пользователь для предупреждения", reason="Причина предупреждения")
    @app_commands.default_permissions(moderate_members=True)
    async def warn(self, interaction: discord.Interaction, user: discord.Member, reason: str = "Не указана"):
        """Выдает предупреждение пользователю"""
        if user.id == interaction.user.id:
            await interaction.response.send_message("❌ Вы не можете предупредить самого себя!", ephemeral=True)
            return
        
        guild_id = interaction.guild.id
        if guild_id not in warnings_storage:
            warnings_storage[guild_id] = {}
        
        if user.id not in warnings_storage[guild_id]:
            warnings_storage[guild_id][user.id] = []
        
        warning = {
            'reason': reason,
            'moderator': interaction.user.id,
            'date': datetime.now(),
            'id': len(warnings_storage[guild_id][user.id]) + 1
        }
        
        warnings_storage[guild_id][user.id].append(warning)
        warn_count = len(warnings_storage[guild_id][user.id])
        
        embed = discord.Embed(
            title="⚠️ Предупреждение выдано",
            description=f"**Пользователь:** {user.mention}\n**Модератор:** {interaction.user.mention}\n**Причина:** {reason}\n**Всего предупреждений:** {warn_count}",
            color=Config.COLORS['warning']
        )
        embed.timestamp = datetime.now()
        
        # Автодействия при достижении лимитов
        if warn_count >= Config.MODERATION['auto_ban_warns']:
            try:
                await user.ban(reason=f"Автобан: {Config.MODERATION['auto_ban_warns']} предупреждений")
                embed.add_field(name="🔨 Автобан", value="Пользователь автоматически заблокирован", inline=False)
            except:
                pass
        elif warn_count >= Config.MODERATION['max_warns']:
            try:
                timeout_until = datetime.now() + timedelta(hours=1)
                await user.timeout(timeout_until, reason=f"Автозаглушение: {warn_count} предупреждений")
                embed.add_field(name="🔇 Автозаглушение", value="Пользователь заглушен на 1 час", inline=False)
            except:
                pass
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="check_warnings", description="📋 Посмотреть предупреждения пользователя")
    @app_commands.describe(user="Пользователь для проверки предупреждений")
    async def check_warnings(self, interaction: discord.Interaction, user: discord.Member = None):
        """Показывает предупреждения пользователя"""
        if user is None:
            user = interaction.user
        
        guild_id = interaction.guild.id
        if guild_id not in warnings_storage or user.id not in warnings_storage[guild_id]:
            embed = discord.Embed(
                title="📋 Предупреждения",
                description=f"У пользователя {user.mention} нет предупреждений.",
                color=Config.COLORS['success']
            )
            await interaction.response.send_message(embed=embed)
            return
        
        warnings = warnings_storage[guild_id][user.id]
        
        embed = discord.Embed(
            title="📋 Предупреждения",
            description=f"**Пользователь:** {user.mention}\n**Всего предупреждений:** {len(warnings)}",
            color=Config.COLORS['warning']
        )
        
        for i, warning in enumerate(warnings[-5:], 1):  # Показываем последние 5
            moderator = interaction.guild.get_member(warning['moderator'])
            mod_name = moderator.display_name if moderator else "Неизвестно"
            
            embed.add_field(
                name=f"⚠️ Предупреждение #{warning['id']}",
                value=f"**Причина:** {warning['reason']}\n**Модератор:** {mod_name}\n**Дата:** {warning['date'].strftime('%d.%m.%Y %H:%M')}",
                inline=False
            )
        
        if len(warnings) > 5:
            embed.set_footer(text=f"Показаны последние 5 из {len(warnings)} предупреждений")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="clear_warnings", description="🗑️ Очистить предупреждения пользователя")
    @app_commands.describe(user="Пользователь для очистки предупреждений")
    @app_commands.default_permissions(administrator=True)
    async def clear_warnings(self, interaction: discord.Interaction, user: discord.Member):
        """Очищает все предупреждения пользователя"""
        guild_id = interaction.guild.id
        
        if guild_id not in warnings_storage or user.id not in warnings_storage[guild_id]:
            await interaction.response.send_message(f"❌ У пользователя {user.mention} нет предупреждений!", ephemeral=True)
            return
        
        warn_count = len(warnings_storage[guild_id][user.id])
        del warnings_storage[guild_id][user.id]
        
        embed = discord.Embed(
            title="🗑️ Предупреждения очищены",
            description=f"**Пользователь:** {user.mention}\n**Очищено предупреждений:** {warn_count}\n**Модератор:** {interaction.user.mention}",
            color=Config.COLORS['success']
        )
        embed.timestamp = datetime.now()
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="clear", description="🧹 Удалить сообщения")
    @app_commands.describe(amount="Количество сообщений для удаления (1-100)")
    @app_commands.default_permissions(manage_messages=True)
    async def clear(self, interaction: discord.Interaction, amount: int):
        if amount < 1 or amount > 100:
            await interaction.response.send_message("❌ Количество сообщений должно быть от 1 до 100!", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)  # предотвращаем таймаут

        channel = interaction.channel
        deleted_count = 0
        to_bulk = []

        async for msg in channel.history(limit=amount):
            age_seconds = (discord.utils.utcnow() - msg.created_at).total_seconds()
            if age_seconds < 14 * 24 * 60 * 60:
                to_bulk.append(msg)
            else:
                # Сообщения старше 14 дней удаляем по одному
                try:
                    await msg.delete()
                    deleted_count += 1
                except (discord.Forbidden, discord.HTTPException):
                    continue

        # Bulk delete для сообщений младше 14 дней
        if to_bulk:
            try:
                await channel.delete_messages(to_bulk)
                deleted_count += len(to_bulk)  # Просто прибавляем количество сообщений, которые мы пытались удалить
            except discord.HTTPException:
                pass  # Игнорируем ошибки

        await interaction.followup.send(f"🧹 Удалено {deleted_count} сообщений!", ephemeral=True)

    @app_commands.command(name="slowmode", description="⏰ Установить медленный режим")
    @app_commands.describe(seconds="Задержка в секундах (0-21600)")
    @app_commands.default_permissions(manage_channels=True)
    async def slowmode(self, interaction: discord.Interaction, seconds: int):
        """Устанавливает медленный режим в канале"""
        if seconds < 0 or seconds > 21600:  # 6 часов максимум
            await interaction.response.send_message("❌ Задержка должна быть от 0 до 21600 секунд (6 часов)!", ephemeral=True)
            return
        
        try:
            await interaction.channel.edit(slowmode_delay=seconds)
            
            if seconds == 0:
                description = "Медленный режим отключен"
                color = Config.COLORS['success']
            else:
                description = f"Медленный режим установлен: **{seconds} секунд**"
                color = Config.COLORS['warning']
            
            embed = discord.Embed(
                title="⏰ Медленный режим",
                description=description,
                color=color
            )
            embed.add_field(name="Канал", value=interaction.channel.mention, inline=True)
            embed.add_field(name="Модератор", value=interaction.user.mention, inline=True)
            
            await interaction.response.send_message(embed=embed)
            
        except discord.Forbidden:
            await interaction.response.send_message("❌ У меня недостаточно прав для изменения канала!", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Произошла ошибка: {str(e)}", ephemeral=True)
    
    @app_commands.command(name="lock", description="🔒 Заблокировать канал")
    @app_commands.default_permissions(manage_channels=True)
    async def lock(self, interaction: discord.Interaction):
        """Блокирует канал для @everyone"""
        try:
            overwrite = interaction.channel.overwrites_for(interaction.guild.default_role)
            overwrite.send_messages = False
            await interaction.channel.set_permissions(interaction.guild.default_role, overwrite=overwrite)
            
            embed = discord.Embed(
                title="🔒 Канал заблокирован",
                description=f"**Канал:** {interaction.channel.mention}\n**Модератор:** {interaction.user.mention}",
                color=Config.COLORS['error']
            )
            
            await interaction.response.send_message(embed=embed)
            
        except discord.Forbidden:
            await interaction.response.send_message("❌ У меня недостаточно прав для изменения канала!", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Произошла ошибка: {str(e)}", ephemeral=True)
    
    @app_commands.command(name="unlock", description="🔓 Разблокировать канал")
    @app_commands.default_permissions(manage_channels=True)
    async def unlock(self, interaction: discord.Interaction):
        """Разблокирует канал для @everyone"""
        try:
            overwrite = interaction.channel.overwrites_for(interaction.guild.default_role)
            overwrite.send_messages = None  # Сброс к настройкам по умолчанию
            await interaction.channel.set_permissions(interaction.guild.default_role, overwrite=overwrite)
            
            embed = discord.Embed(
                title="🔓 Канал разблокирован",
                description=f"**Канал:** {interaction.channel.mention}\n**Модератор:** {interaction.user.mention}",
                color=Config.COLORS['success']
            )
            
            await interaction.response.send_message(embed=embed)
            
        except discord.Forbidden:
            await interaction.response.send_message("❌ У меня недостаточно прав для изменения канала!", ephemeral=True)
        except Exception as e:
            await interaction.response.send_message(f"❌ Произошла ошибка: {str(e)}", ephemeral=True)
    
    @app_commands.command(name="moderation_help", description="❓ Помощь по командам модерации")
    async def moderation_help(self, interaction: discord.Interaction):
        """Показывает помощь по командам модерации"""
        embed = discord.Embed(
            title="🛡️ Команды модерации",
            description="Все доступные команды для модерации сервера",
            color=Config.COLORS['moderation']
        )
        
        commands_list = [
            "`/kick [@пользователь] [причина]` - Исключить участника",
            "`/ban [@пользователь] [причина]` - Заблокировать участника",
            "`/unban [ID]` - Разблокировать пользователя",
            "`/mute [@пользователь] [время] [причина]` - Заглушить",
            "`/unmute [@пользователь]` - Снять заглушение",
            "`/warn [@пользователь] [причина]` - Выдать предупреждение",
            "`/check_warnings [@пользователь]` - Посмотреть предупреждения",
            "`/clear_warnings [@пользователь]` - Очистить предупреждения",
            "`/clear [количество]` - Удалить сообщения",
            "`/slowmode [секунды]` - Медленный режим канала",
            "`/lock` - Заблокировать канал",
            "`/unlock` - Разблокировать канал"
        ]
        
        embed.add_field(
            name="📋 Команды:",
            value="\n".join(commands_list),
            inline=False
        )
        
        embed.add_field(
            name="⚙️ Автомодерация:",
            value=f"• **{Config.MODERATION['max_warns']}** предупреждения = заглушение на 1 час\n"
                  f"• **{Config.MODERATION['auto_ban_warns']}** предупреждений = автобан",
            inline=False
        )
        
        embed.add_field(
            name="🔒 Требуемые права:",
            value="• Kick Members - для исключения\n"
                  "• Ban Members - для блокировки\n"
                  "• Moderate Members - для заглушения\n"
                  "• Manage Messages - для удаления сообщений\n"
                  "• Manage Channels - для блокировки каналов",
            inline=False
        )
        
        embed.set_footer(text="Используйте команды ответственно!")
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Moderation(bot))
