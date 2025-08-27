import discord
from discord.ext import commands
from discord import app_commands
from datetime import datetime
import asyncio
from config import Config

# Хранилище настроек сервера (в реальном боте используйте базу данных)
server_settings = {}

class ServerManagement(commands.Cog):
    """Команды управления сервером"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="set_welcome", description="👋 Настроить канал приветствия")
    @app_commands.describe(channel="Канал для приветствия новых участников")
    @app_commands.default_permissions(manage_guild=True)
    async def set_welcome(self, interaction: discord.Interaction, channel: discord.TextChannel):
        """Устанавливает канал для приветствия новых участников"""
        guild_id = interaction.guild.id
        
        if guild_id not in server_settings:
            server_settings[guild_id] = {}
        
        server_settings[guild_id]['welcome_channel'] = channel.id
        
        embed = discord.Embed(
            title="👋 Канал приветствия настроен",
            description=f"Теперь новые участники будут приветствоваться в {channel.mention}!",
            color=Config.COLORS['success']
        )
        embed.add_field(
            name="📋 Что будет происходить:",
            value="• Автоматическое приветствие новых участников\n• Красивые embed сообщения\n• Информация о сервере",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="set_leave", description="👋 Настроить канал прощания")
    @app_commands.describe(channel="Канал для сообщений о покинувших сервер")
    @app_commands.default_permissions(manage_guild=True)
    async def set_leave(self, interaction: discord.Interaction, channel: discord.TextChannel):
        """Устанавливает канал для сообщений о покинувших участников"""
        guild_id = interaction.guild.id
        
        if guild_id not in server_settings:
            server_settings[guild_id] = {}
        
        server_settings[guild_id]['leave_channel'] = channel.id
        
        embed = discord.Embed(
            title="👋 Канал прощания настроен",
            description=f"Теперь сообщения о покинувших будут отправляться в {channel.mention}!",
            color=Config.COLORS['success']
        )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="set_autorole", description="🎭 Настроить авто-выдачу роли")
    @app_commands.describe(role="Роль для автоматической выдачи новым участникам")
    @app_commands.default_permissions(manage_roles=True)
    async def set_autorole(self, interaction: discord.Interaction, role: discord.Role):
        """Устанавливает роль для автоматической выдачи новым участникам"""
        # Проверяем иерархию ролей
        if role.position >= interaction.guild.me.top_role.position:
            await interaction.response.send_message("❌ Эта роль выше моей роли в иерархии! Переместите мою роль выше.", ephemeral=True)
            return
        
        if role.managed:
            await interaction.response.send_message("❌ Эта роль управляется ботом или интеграцией и не может быть автоматически выдана!", ephemeral=True)
            return
        
        guild_id = interaction.guild.id
        
        if guild_id not in server_settings:
            server_settings[guild_id] = {}
        
        server_settings[guild_id]['autorole'] = role.id
        
        embed = discord.Embed(
            title="🎭 Авто-роль настроена",
            description=f"Новые участники будут автоматически получать роль {role.mention}!",
            color=Config.COLORS['success']
        )
        embed.add_field(
            name="⚠️ Важно:",
            value="• Убедитесь, что моя роль выше настроенной авто-роли\n• Роль будет выдаваться только новым участникам",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="mass_role", description="🎭 Массовое управление ролями")
    @app_commands.describe(role="Роль для массового действия", action="Действие: add (добавить) или remove (убрать)")
    @app_commands.default_permissions(manage_roles=True)
    async def mass_role(self, interaction: discord.Interaction, role: discord.Role, action: str):
        """Массово добавляет или убирает роль у всех участников"""
        if action.lower() not in ['add', 'remove', 'добавить', 'убрать']:
            await interaction.response.send_message("❌ Действие должно быть 'add' (добавить) или 'remove' (убрать)!", ephemeral=True)
            return
        
        # Проверяем иерархию ролей
        if role.position >= interaction.guild.me.top_role.position:
            await interaction.response.send_message("❌ Эта роль выше моей роли в иерархии!", ephemeral=True)
            return
        
        is_adding = action.lower() in ['add', 'добавить']
        action_text = "добавления" if is_adding else "удаления"
        
        # Подтверждение
        embed = discord.Embed(
            title="⚠️ Подтверждение массового действия",
            description=f"Вы уверены, что хотите **{action_text}** роль {role.mention} **всем участникам** сервера?\n\nЭто действие может занять время и его нельзя отменить!",
            color=Config.COLORS['warning']
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
        # Ждем подтверждения (упрощенно, в реальном боте лучше использовать View с кнопками)
        try:
            def check(m):
                return m.author == interaction.user and m.channel == interaction.channel
            
            await interaction.followup.send("Напишите 'да' для подтверждения или 'нет' для отмены:", ephemeral=True)
            msg = await self.bot.wait_for('message', check=check, timeout=30.0)
            
            if msg.content.lower() not in ['да', 'yes', 'y']:
                await interaction.followup.send("❌ Действие отменено.", ephemeral=True)
                return
                
        except asyncio.TimeoutError:
            await interaction.followup.send("❌ Время ожидания истекло. Действие отменено.", ephemeral=True)
            return
        
        # Выполняем массовое действие
        await interaction.followup.send(f"🔄 Начинаю массовое {action_text} роли...", ephemeral=True)
        
        success_count = 0
        error_count = 0
        
        for member in interaction.guild.members:
            if member.bot:
                continue
                
            try:
                if is_adding and role not in member.roles:
                    await member.add_roles(role, reason=f"Массовое добавление роли от {interaction.user}")
                    success_count += 1
                elif not is_adding and role in member.roles:
                    await member.remove_roles(role, reason=f"Массовое удаление роли от {interaction.user}")
                    success_count += 1
                
                # Небольшая задержка чтобы не попасть в rate limit
                await asyncio.sleep(0.1)
                
            except discord.Forbidden:
                error_count += 1
            except Exception:
                error_count += 1
        
        result_embed = discord.Embed(
            title="✅ Массовое действие завершено",
            description=f"**Роль:** {role.mention}\n**Действие:** {action_text.title()}\n**Успешно:** {success_count}\n**Ошибок:** {error_count}",
            color=Config.COLORS['success']
        )
        
        await interaction.followup.send(embed=result_embed)
    
    @app_commands.command(name="purge_bots", description="🤖 Удалить всех ботов с сервера")
    @app_commands.default_permissions(kick_members=True)
    async def purge_bots(self, interaction: discord.Interaction):
        """Удаляет всех ботов с сервера (кроме этого бота)"""
        bots = [member for member in interaction.guild.members if member.bot and member.id != self.bot.user.id]
        
        if not bots:
            await interaction.response.send_message("❌ На сервере нет ботов для удаления!", ephemeral=True)
            return
        
        # Подтверждение
        embed = discord.Embed(
            title="⚠️ Подтверждение удаления ботов",
            description=f"Найдено **{len(bots)}** ботов для удаления.\n\nВы уверены? Это действие нельзя отменить!",
            color=Config.COLORS['warning']
        )
        
        bot_list = "\n".join([f"• {bot.display_name}" for bot in bots[:10]])
        if len(bots) > 10:
            bot_list += f"\n... и ещё {len(bots) - 10} ботов"
        
        embed.add_field(name="🤖 Боты для удаления:", value=bot_list, inline=False)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
        # Ждем подтверждения
        try:
            def check(m):
                return m.author == interaction.user and m.channel == interaction.channel
            
            await interaction.followup.send("Напишите 'да' для подтверждения или 'нет' для отмены:", ephemeral=True)
            msg = await self.bot.wait_for('message', check=check, timeout=30.0)
            
            if msg.content.lower() not in ['да', 'yes', 'y']:
                await interaction.followup.send("❌ Действие отменено.", ephemeral=True)
                return
                
        except asyncio.TimeoutError:
            await interaction.followup.send("❌ Время ожидания истекло. Действие отменено.", ephemeral=True)
            return
        
        # Удаляем ботов
        await interaction.followup.send("🔄 Начинаю удаление ботов...", ephemeral=True)
        
        success_count = 0
        error_count = 0
        
        for bot in bots:
            try:
                await bot.kick(reason=f"Массовое удаление ботов от {interaction.user}")
                success_count += 1
                await asyncio.sleep(0.5)  # Задержка для избежания rate limit
            except:
                error_count += 1
        
        result_embed = discord.Embed(
            title="✅ Удаление ботов завершено",
            description=f"**Успешно удалено:** {success_count}\n**Ошибок:** {error_count}",
            color=Config.COLORS['success']
        )
        
        await interaction.followup.send(embed=result_embed)
    
    @app_commands.command(name="backup_roles", description="💾 Создать резервную копию ролей")
    @app_commands.default_permissions(manage_guild=True)
    async def backup_roles(self, interaction: discord.Interaction):
        """Создает резервную копию структуры ролей сервера"""
        guild = interaction.guild
        roles_data = []
        
        for role in guild.roles:
            if role.name == "@everyone":
                continue
                
            role_info = {
                'name': role.name,
                'color': str(role.color),
                'permissions': role.permissions.value,
                'hoist': role.hoist,
                'mentionable': role.mentionable,
                'position': role.position,
                'members_count': len(role.members)
            }
            roles_data.append(role_info)
        
        # Создаем красивый отчет
        embed = discord.Embed(
            title="💾 Резервная копия ролей создана",
            description=f"Сохранено **{len(roles_data)}** ролей с сервера **{guild.name}**",
            color=Config.COLORS['success']
        )
        
        embed.add_field(
            name="📊 Статистика:",
            value=f"• Всего ролей: {len(roles_data)}\n• Дата создания: {datetime.now().strftime('%d.%m.%Y %H:%M')}\n• Создал: {interaction.user.mention}",
            inline=False
        )
        
        # Топ-5 ролей по количеству участников
        top_roles = sorted(roles_data, key=lambda x: x['members_count'], reverse=True)[:5]
        top_roles_text = "\n".join([f"• {role['name']}: {role['members_count']} участников" for role in top_roles])
        
        embed.add_field(
            name="👑 Топ ролей по участникам:",
            value=top_roles_text,
            inline=False
        )
        
        embed.set_footer(text="💾 Данные сохранены в памяти бота")
        
        # Сохраняем данные в настройках сервера
        guild_id = interaction.guild.id
        if guild_id not in server_settings:
            server_settings[guild_id] = {}
        
        server_settings[guild_id]['roles_backup'] = {
            'data': roles_data,
            'created_at': datetime.now().isoformat(),
            'created_by': interaction.user.id
        }
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="server_stats", description="📊 Расширенная статистика сервера")
    @app_commands.default_permissions(manage_guild=True)
    async def server_stats(self, interaction: discord.Interaction):
        """Показывает расширенную статистику сервера для администраторов"""
        guild = interaction.guild
        
        # Подробная статистика участников
        total_members = guild.member_count
        humans = len([m for m in guild.members if not m.bot])
        bots = total_members - humans
        
        # Статусы
        online = len([m for m in guild.members if m.status == discord.Status.online])
        idle = len([m for m in guild.members if m.status == discord.Status.idle])
        dnd = len([m for m in guild.members if m.status == discord.Status.dnd])
        offline = total_members - online - idle - dnd
        
        # Роли и права
        admin_roles = len([r for r in guild.roles if r.permissions.administrator])
        mod_roles = len([r for r in guild.roles if r.permissions.manage_messages and not r.permissions.administrator])
        
        # Каналы
        text_channels = len(guild.text_channels)
        voice_channels = len(guild.voice_channels)
        categories = len(guild.categories)
        
        # Активность
        active_members = len([m for m in guild.members if m.activity is not None])
        
        embed = discord.Embed(
            title=f"📊 Расширенная статистика: {guild.name}",
            color=Config.COLORS['info']
        )
        
        embed.add_field(
            name="👥 Участники",
            value=f"**Всего:** {total_members}\n**Людей:** {humans}\n**Ботов:** {bots}\n**С активностью:** {active_members}",
            inline=True
        )
        
        embed.add_field(
            name="📊 Статусы",
            value=f"🟢 Онлайн: {online}\n🟡 Отошел: {idle}\n🔴 Не беспокоить: {dnd}\n⚫ Оффлайн: {offline}",
            inline=True
        )
        
        embed.add_field(
            name="📺 Каналы",
            value=f"**Всего:** {text_channels + voice_channels}\n**Текстовых:** {text_channels}\n**Голосовых:** {voice_channels}\n**Категорий:** {categories}",
            inline=True
        )
        
        embed.add_field(
            name="🎭 Роли",
            value=f"**Всего:** {len(guild.roles) - 1}\n**Админ ролей:** {admin_roles}\n**Мод ролей:** {mod_roles}",
            inline=True
        )
        
        embed.add_field(
            name="🚀 Буст",
            value=f"**Уровень:** {guild.premium_tier}\n**Бустеров:** {guild.premium_subscription_count}\n**Макс участников:** {guild.max_members or 'Неограничено'}",
            inline=True
        )
        
        # Возраст сервера
        days_old = (datetime.now() - guild.created_at.replace(tzinfo=None)).days
        embed.add_field(
            name="📅 Возраст",
            value=f"{days_old} дней\n({guild.created_at.strftime('%d.%m.%Y')})",
            inline=True
        )
        
        # Настройки безопасности
        verification_levels = {
            discord.VerificationLevel.none: "Отсутствует",
            discord.VerificationLevel.low: "Низкий",
            discord.VerificationLevel.medium: "Средний", 
            discord.VerificationLevel.high: "Высокий",
            discord.VerificationLevel.highest: "Максимальный"
        }
        
        embed.add_field(
            name="🔒 Безопасность",
            value=f"**Верификация:** {verification_levels.get(guild.verification_level, 'Неизвестно')}\n**Фильтр контента:** {'Включен' if guild.explicit_content_filter != discord.ContentFilter.disabled else 'Отключен'}",
            inline=False
        )
        
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        
        embed.timestamp = datetime.now()
        embed.set_footer(text=f"ID: {guild.id} | Запросил: {interaction.user.display_name}")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="nickname_all", description="📛 Массовое изменение никнеймов")
    @app_commands.describe(nickname="Новый никнейм (используйте {user} для имени пользователя)")
    @app_commands.default_permissions(manage_nicknames=True)
    async def nickname_all(self, interaction: discord.Interaction, nickname: str):
        """Массово изменяет никнеймы участников"""
        if len(nickname) > 32:
            await interaction.response.send_message("❌ Никнейм не может быть длиннее 32 символов!", ephemeral=True)
            return
        
        # Подтверждение
        preview = nickname.replace("{user}", interaction.user.display_name)
        
        embed = discord.Embed(
            title="⚠️ Подтверждение массового изменения никнеймов",
            description=f"Вы уверены, что хотите изменить никнеймы **всех участников**?\n\n**Шаблон:** `{nickname}`\n**Пример:** `{preview}`\n\nИспользуйте `{user}` для подстановки имени пользователя.",
            color=Config.COLORS['warning']
        )
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
        # Ждем подтверждения
        try:
            def check(m):
                return m.author == interaction.user and m.channel == interaction.channel
            
            await interaction.followup.send("Напишите 'да' для подтверждения или 'нет' для отмены:", ephemeral=True)
            msg = await self.bot.wait_for('message', check=check, timeout=30.0)
            
            if msg.content.lower() not in ['да', 'yes', 'y']:
                await interaction.followup.send("❌ Действие отменено.", ephemeral=True)
                return
                
        except asyncio.TimeoutError:
            await interaction.followup.send("❌ Время ожидания истекло. Действие отменено.", ephemeral=True)
            return
        
        # Выполняем массовое изменение
        await interaction.followup.send("🔄 Начинаю массовое изменение никнеймов...", ephemeral=True)
        
        success_count = 0
        error_count = 0
        
        for member in interaction.guild.members:
            if member.bot or member.id == interaction.guild.owner_id:
                continue
                
            try:
                new_nickname = nickname.replace("{user}", member.display_name)
                await member.edit(nick=new_nickname, reason=f"Массовое изменение никнеймов от {interaction.user}")
                success_count += 1
                await asyncio.sleep(0.2)  # Задержка для избежания rate limit
                
            except discord.Forbidden:
                error_count += 1
            except Exception:
                error_count += 1
        
        result_embed = discord.Embed(
            title="✅ Массовое изменение никнеймов завершено",
            description=f"**Успешно изменено:** {success_count}\n**Ошибок:** {error_count}",
            color=Config.COLORS['success']
        )
        
        await interaction.followup.send(embed=result_embed)
    
    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Обработка присоединения нового участника"""
        guild_id = member.guild.id
        
        if guild_id not in server_settings:
            return
        
        settings = server_settings[guild_id]
        
        # Приветствие
        if 'welcome_channel' in settings:
            channel = self.bot.get_channel(settings['welcome_channel'])
            if channel:
                embed = discord.Embed(
                    title="👋 Добро пожаловать!",
                    description=f"Привет, {member.mention}! Добро пожаловать на сервер **{member.guild.name}**!",
                    color=Config.COLORS['success']
                )
                embed.add_field(
                    name="🎉 Информация",
                    value=f"Вы участник номер **{member.guild.member_count}**!",
                    inline=True
                )
                embed.add_field(
                    name="📋 Совет",
                    value="Ознакомьтесь с правилами сервера!",
                    inline=True
                )
                embed.set_thumbnail(url=member.display_avatar.url)
                embed.timestamp = datetime.now()
                
                await channel.send(embed=embed)
        
        # Авто-роль
        if 'autorole' in settings:
            role = member.guild.get_role(settings['autorole'])
            if role:
                try:
                    await member.add_roles(role, reason="Автоматическая выдача роли новому участнику")
                except:
                    pass
    
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        """Обработка покидания участника"""
        guild_id = member.guild.id
        
        if guild_id not in server_settings:
            return
        
        settings = server_settings[guild_id]
        
        # Сообщение о покидании
        if 'leave_channel' in settings:
            channel = self.bot.get_channel(settings['leave_channel'])
            if channel:
                embed = discord.Embed(
                    title="👋 Пользователь покинул сервер",
                    description=f"**{member.display_name}** покинул сервер.",
                    color=Config.COLORS['warning']
                )
                embed.add_field(
                    name="📊 Статистика",
                    value=f"Участников осталось: **{member.guild.member_count}**",
                    inline=True
                )
                embed.set_thumbnail(url=member.display_avatar.url)
                embed.timestamp = datetime.now()
                
                await channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(ServerManagement(bot))
