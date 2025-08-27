import discord
from discord.ext import commands
from discord import app_commands
import psutil
import platform
from datetime import datetime
import time
from config import Config

class Utility(commands.Cog):
    """Утилитарные команды бота"""
    
    def __init__(self, bot):
        self.bot = bot
        self.start_time = time.time()
    
    @app_commands.command(name="ping", description="🏓 Проверить задержку бота")
    async def ping(self, interaction: discord.Interaction):
        """Показывает задержку бота"""
        start_time = time.time()
        
        embed = discord.Embed(
            title="🏓 Пинг",
            description="Измеряю задержку...",
            color=Config.COLORS['info']
        )
        
        await interaction.response.send_message(embed=embed)
        
        end_time = time.time()
        response_time = round((end_time - start_time) * 1000)
        websocket_latency = round(self.bot.latency * 1000)
        
        # Определяем качество соединения
        if websocket_latency < 100:
            status = "Отличное"
            emoji = "🟢"
        elif websocket_latency < 200:
            status = "Хорошее"
            emoji = "🟡"
        else:
            status = "Плохое"
            emoji = "🔴"
        
        embed = discord.Embed(
            title="🏓 Результаты пинга",
            color=Config.COLORS['success']
        )
        embed.add_field(
            name="🌐 WebSocket задержка",
            value=f"{websocket_latency}ms",
            inline=True
        )
        embed.add_field(
            name="⚡ Время отклика",
            value=f"{response_time}ms",
            inline=True
        )
        embed.add_field(
            name="📊 Качество соединения",
            value=f"{emoji} {status}",
            inline=True
        )
        
        await interaction.edit_original_response(embed=embed)
    
    @app_commands.command(name="serverinfo", description="🏰 Информация о сервере")
    async def serverinfo(self, interaction: discord.Interaction):
        """Показывает подробную информацию о сервере"""
        guild = interaction.guild
        
        # Подсчет участников
        total_members = guild.member_count
        humans = len([m for m in guild.members if not m.bot])
        bots = total_members - humans
        
        # Подсчет каналов
        text_channels = len(guild.text_channels)
        voice_channels = len(guild.voice_channels)
        categories = len(guild.categories)
        
        # Статусы участников
        online = len([m for m in guild.members if m.status == discord.Status.online])
        idle = len([m for m in guild.members if m.status == discord.Status.idle])
        dnd = len([m for m in guild.members if m.status == discord.Status.dnd])
        offline = total_members - online - idle - dnd
        
        embed = discord.Embed(
            title=f"🏰 Информация о сервере {guild.name}",
            color=Config.COLORS['info']
        )
        
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        
        embed.add_field(
            name="👑 Владелец",
            value=guild.owner.mention if guild.owner else "Неизвестно",
            inline=True
        )
        embed.add_field(
            name="📅 Создан",
            value=guild.created_at.strftime("%d.%m.%Y"),
            inline=True
        )
        embed.add_field(
            name="🆔 ID сервера",
            value=str(guild.id),
            inline=True
        )
        
        embed.add_field(
            name=f"👥 Участники ({total_members})",
            value=f"👤 Людей: {humans}\n🤖 Ботов: {bots}",
            inline=True
        )
        embed.add_field(
            name=f"📊 Статусы",
            value=f"🟢 В сети: {online}\n🟡 Отошел: {idle}\n🔴 Не беспокоить: {dnd}\n⚫ Не в сети: {offline}",
            inline=True
        )
        embed.add_field(
            name=f"📝 Каналы ({text_channels + voice_channels})",
            value=f"💬 Текстовых: {text_channels}\n🔊 Голосовых: {voice_channels}\n📁 Категорий: {categories}",
            inline=True
        )
        
        embed.add_field(
            name="🎭 Роли",
            value=str(len(guild.roles)),
            inline=True
        )
        embed.add_field(
            name="😀 Эмодзи",
            value=str(len(guild.emojis)),
            inline=True
        )
        embed.add_field(
            name="🚀 Буст уровень",
            value=f"Уровень {guild.premium_tier} ({guild.premium_subscription_count} бустов)",
            inline=True
        )
        
        if guild.features:
            features = []
            feature_names = {
                'COMMUNITY': 'Сообщество',
                'PARTNERED': 'Партнёр Discord',
                'VERIFIED': 'Верифицирован',
                'VANITY_URL': 'Пользовательская ссылка',
                'BANNER': 'Баннер сервера',
                'ANIMATED_ICON': 'Анимированная иконка'
            }
            
            for feature in guild.features:
                if feature in feature_names:
                    features.append(feature_names[feature])
            
            if features:
                embed.add_field(
                    name="✨ Особенности",
                    value="\n".join(features),
                    inline=False
                )
        
        embed.timestamp = datetime.now()
        embed.set_footer(text=f"Запросил: {interaction.user.display_name}")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="userinfo", description="👤 Информация о пользователе")
    @app_commands.describe(user="Пользователь для получения информации")
    async def userinfo(self, interaction: discord.Interaction, user: discord.Member = None):
        """Показывает информацию о пользователе"""
        if user is None:
            user = interaction.user
        
        embed = discord.Embed(
            title=f"👤 Информация о {user.display_name}",
            color=user.color if user.color != discord.Color.default() else Config.COLORS['info']
        )
        
        embed.set_thumbnail(url=user.display_avatar.url)
        
        embed.add_field(
            name="🏷️ Имя пользователя",
            value=f"{user.name}#{user.discriminator}",
            inline=True
        )
        embed.add_field(
            name="📛 Никнейм",
            value=user.display_name,
            inline=True
        )
        embed.add_field(
            name="🆔 ID",
            value=str(user.id),
            inline=True
        )
        
        embed.add_field(
            name="📅 Аккаунт создан",
            value=user.created_at.strftime("%d.%m.%Y %H:%M"),
            inline=True
        )
        embed.add_field(
            name="📥 Присоединился",
            value=user.joined_at.strftime("%d.%m.%Y %H:%M") if user.joined_at else "Неизвестно",
            inline=True
        )
        embed.add_field(
            name="📊 Статус",
            value=str(user.status).title(),
            inline=True
        )
        
        if user.activity:
            activity_type = {
                discord.ActivityType.playing: "🎮 Играет в",
                discord.ActivityType.streaming: "📺 Стримит",
                discord.ActivityType.listening: "🎵 Слушает",
                discord.ActivityType.watching: "👀 Смотрит"
            }
            
            activity_name = activity_type.get(user.activity.type, "🔄 Занят")
            embed.add_field(
                name="🎯 Активность",
                value=f"{activity_name} {user.activity.name}",
                inline=False
            )
        
        roles = [role.mention for role in user.roles[1:]]  # Исключаем @everyone
        if roles:
            embed.add_field(
                name=f"🎭 Роли ({len(roles)})",
                value=" ".join(roles[:10]) + ("..." if len(roles) > 10 else ""),
                inline=False
            )
        
        permissions = []
        if user.guild_permissions.administrator:
            permissions.append("👑 Администратор")
        elif user.guild_permissions.manage_guild:
            permissions.append("⚙️ Управление сервером")
        elif user.guild_permissions.manage_messages:
            permissions.append("🛡️ Модератор")
        
        if permissions:
            embed.add_field(
                name="🔑 Ключевые права",
                value="\n".join(permissions),
                inline=True
            )
        
        if user.premium_since:
            embed.add_field(
                name="💎 Бустер с",
                value=user.premium_since.strftime("%d.%m.%Y"),
                inline=True
            )
        
        embed.timestamp = datetime.now()
        embed.set_footer(text=f"Запросил: {interaction.user.display_name}")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="botinfo", description="🤖 Информация о боте")
    async def botinfo(self, interaction: discord.Interaction):
        """Показывает информацию о боте"""
        bot_user = self.bot.user
        
        # Статистика
        total_guilds = len(self.bot.guilds)
        total_users = len(self.bot.users)
        total_commands = len([cmd for cmd in self.bot.tree.walk_commands()])
        
        # Системная информация
        cpu_percent = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        memory_used = round(memory.used / 1024 / 1024)
        memory_total = round(memory.total / 1024 / 1024)
        
        # Время работы
        uptime_seconds = int(time.time() - self.start_time)
        uptime_str = str(datetime.timedelta(seconds=uptime_seconds))
        
        embed = discord.Embed(
            title=f"🤖 Информация о {bot_user.display_name}",
            description="Многофункциональный Discord бот с 150+ командами!",
            color=Config.COLORS['info']
        )
        
        embed.set_thumbnail(url=bot_user.display_avatar.url)
        
        embed.add_field(
            name="📊 Статистика",
            value=f"🏰 Серверов: {total_guilds}\n👥 Пользователей: {total_users}\n⚡ Команд: {total_commands}",
            inline=True
        )
        embed.add_field(
            name="💻 Система",
            value=f"🖥️ ЦП: {cpu_percent}%\n🧠 ОЗУ: {memory_used}MB/{memory_total}MB\n🐍 Python: {platform.python_version()}",
            inline=True
        )
        embed.add_field(
            name="⏱️ Время работы",
            value=uptime_str,
            inline=True
        )
        
        embed.add_field(
            name="🔧 Версии",
            value=f"Discord.py: {discord.__version__}\nПлатформа: {platform.system()}",
            inline=True
        )
        embed.add_field(
            name="🏓 Задержка",
            value=f"{round(self.bot.latency * 1000)}ms",
            inline=True
        )
        embed.add_field(
            name="🆔 ID бота",
            value=str(bot_user.id),
            inline=True
        )
        
        # Проверка прав
        guild = interaction.guild
        bot_member = guild.get_member(self.bot.user.id)
        missing_perms = []
        
        required_perms = [
            ('send_messages', 'Отправка сообщений'),
            ('embed_links', 'Встраивание ссылок'),
            ('add_reactions', 'Добавление реакций'),
            ('manage_messages', 'Управление сообщениями'),
            ('kick_members', 'Исключение участников'),
            ('ban_members', 'Блокировка участников'),
            ('manage_channels', 'Управление каналами'),
            ('manage_roles', 'Управление ролями')
        ]
        
        for perm, name in required_perms:
            if not getattr(bot_member.guild_permissions, perm):
                missing_perms.append(name)
        
        if missing_perms:
            embed.add_field(
                name="⚠️ Отсутствующие права",
                value="\n".join(missing_perms),
                inline=False
            )
        else:
            embed.add_field(
                name="✅ Права",
                value="Все необходимые права предоставлены!",
                inline=False
            )
        
        embed.timestamp = datetime.now()
        embed.set_footer(text="Создан с ❤️ для Discord сообщества")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="uptime", description="⏰ Время работы системы")
    async def uptime(self, interaction: discord.Interaction):
        """Показывает время работы бота и системы"""
        # Время работы бота
        bot_uptime_seconds = int(time.time() - self.start_time)
        bot_uptime = str(datetime.timedelta(seconds=bot_uptime_seconds))
        
        # Время работы системы
        system_uptime_seconds = int(time.time() - psutil.boot_time())
        system_uptime = str(datetime.timedelta(seconds=system_uptime_seconds))
        
        embed = discord.Embed(
            title="⏰ Время работы",
            color=Config.COLORS['info']
        )
        
        embed.add_field(
            name="🤖 Бот запущен",
            value=bot_uptime,
            inline=True
        )
        embed.add_field(
            name="💻 Система запущена",
            value=system_uptime,
            inline=True
        )
        
        # Загрузка системы
        cpu_percent = psutil.cpu_percent(interval=1)
        memory_percent = psutil.virtual_memory().percent
        
        embed.add_field(
            name="📊 Загрузка системы",
            value=f"🖥️ ЦП: {cpu_percent}%\n🧠 ОЗУ: {memory_percent}%",
            inline=True
        )
        
        embed.timestamp = datetime.now()
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="invite", description="🔗 Пригласить бота на сервер")
    async def invite(self, interaction: discord.Interaction):
        """Генерирует ссылку-приглашение для бота"""
        bot_id = self.bot.user.id
        
        # Права, необходимые боту
        permissions = discord.Permissions(
            send_messages=True,
            embed_links=True,
            add_reactions=True,
            use_external_emojis=True,
            read_message_history=True,
            kick_members=True,
            ban_members=True,
            manage_messages=True,
            moderate_members=True,
            manage_channels=True,
            manage_roles=True,
            manage_nicknames=True,
            view_audit_log=True,
            connect=True,
            move_members=True
        )
        
        invite_url = discord.utils.oauth_url(bot_id, permissions=permissions, scopes=('bot', 'applications.commands'))
        
        embed = discord.Embed(
            title="🔗 Пригласить бота",
            description="Добавьте этого бота на свой сервер!",
            color=Config.COLORS['success']
        )
        
        embed.add_field(
            name="📋 Ссылка-приглашение",
            value=f"[Нажмите здесь для приглашения]({invite_url})",
            inline=False
        )
        
        embed.add_field(
            name="⚡ Возможности",
            value="• 150+ команд\n• Модерация сервера\n• Развлекательные игры\n• Система логирования\n• Приватные комнаты\n• Калькулятор любви",
            inline=True
        )
        
        embed.add_field(
            name="🔒 Права",
            value="• Отправка сообщений\n• Модерация участников\n• Управление каналами\n• Управление ролями\n• И другие...",
            inline=True
        )
        
        embed.set_footer(text="Спасибо за использование нашего бота! ❤️")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="channelinfo", description="📺 Информация о канале")
    async def channelinfo(self, interaction: discord.Interaction):
        """Показывает информацию о текущем канале"""
        channel = interaction.channel
        
        embed = discord.Embed(
            title=f"📺 Информация о канале #{channel.name}",
            color=Config.COLORS['info']
        )
        
        embed.add_field(
            name="🏷️ Название",
            value=channel.name,
            inline=True
        )
        embed.add_field(
            name="🆔 ID",
            value=str(channel.id),
            inline=True
        )
        embed.add_field(
            name="📝 Тип",
            value="Текстовый" if isinstance(channel, discord.TextChannel) else "Голосовой",
            inline=True
        )
        
        if isinstance(channel, discord.TextChannel):
            embed.add_field(
                name="📋 Описание",
                value=channel.topic or "Не установлено",
                inline=False
            )
            
            embed.add_field(
                name="⏰ Медленный режим",
                value=f"{channel.slowmode_delay} секунд" if channel.slowmode_delay else "Отключен",
                inline=True
            )
            
            embed.add_field(
                name="🔞 NSFW",
                value="Да" if channel.is_nsfw() else "Нет",
                inline=True
            )
        
        embed.add_field(
            name="📅 Создан",
            value=channel.created_at.strftime("%d.%m.%Y %H:%M"),
            inline=True
        )
        
        if channel.category:
            embed.add_field(
                name="📁 Категория",
                value=channel.category.name,
                inline=True
            )
        
        embed.add_field(
            name="👁️ Видимость",
            value="Публичный" if channel.permissions_for(interaction.guild.default_role).read_messages else "Приватный",
            inline=True
        )
        
        embed.timestamp = datetime.now()
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="roleinfo", description="🎭 Информация о роли")
    @app_commands.describe(role="Роль для получения информации")
    async def roleinfo(self, interaction: discord.Interaction, role: discord.Role):
        """Показывает информацию о роли"""
        embed = discord.Embed(
            title=f"🎭 Информация о роли {role.name}",
            color=role.color if role.color != discord.Color.default() else Config.COLORS['info']
        )
        
        embed.add_field(
            name="🏷️ Название",
            value=role.name,
            inline=True
        )
        embed.add_field(
            name="🆔 ID",
            value=str(role.id),
            inline=True
        )
        embed.add_field(
            name="👥 Участников",
            value=str(len(role.members)),
            inline=True
        )
        
        embed.add_field(
            name="🎨 Цвет",
            value=str(role.color),
            inline=True
        )
        embed.add_field(
            name="📅 Создана",
            value=role.created_at.strftime("%d.%m.%Y %H:%M"),
            inline=True
        )
        embed.add_field(
            name="📊 Позиция",
            value=str(role.position),
            inline=True
        )
        
        embed.add_field(
            name="🔧 Настройки",
            value=f"{'✅' if role.hoist else '❌'} Отображается отдельно\n"
                  f"{'✅' if role.mentionable else '❌'} Можно упоминать\n"
                  f"{'✅' if role.managed else '❌'} Управляется ботом",
            inline=True
        )
        
        # Ключевые права
        key_perms = []
        if role.permissions.administrator:
            key_perms.append("👑 Администратор")
        if role.permissions.manage_guild:
            key_perms.append("⚙️ Управление сервером")
        if role.permissions.manage_roles:
            key_perms.append("🎭 Управление ролями")
        if role.permissions.manage_channels:
            key_perms.append("📺 Управление каналами")
        if role.permissions.kick_members:
            key_perms.append("👢 Исключение участников")
        if role.permissions.ban_members:
            key_perms.append("🔨 Блокировка участников")
        
        if key_perms:
            embed.add_field(
                name="🔑 Ключевые права",
                value="\n".join(key_perms),
                inline=False
            )
        
        embed.timestamp = datetime.now()
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="emoji_list", description="😀 Список эмодзи сервера")
    async def emoji_list(self, interaction: discord.Interaction):
        """Показывает список эмодзи сервера"""
        guild = interaction.guild
        
        if not guild.emojis:
            embed = discord.Embed(
                title="😀 Эмодзи сервера",
                description="На этом сервере нет кастомных эмодзи.",
                color=Config.COLORS['warning']
            )
            await interaction.response.send_message(embed=embed)
            return
        
        # Разделяем эмодзи на обычные и анимированные
        static_emojis = [emoji for emoji in guild.emojis if not emoji.animated]
        animated_emojis = [emoji for emoji in guild.emojis if emoji.animated]
        
        embed = discord.Embed(
            title=f"😀 Эмодзи сервера ({len(guild.emojis)})",
            color=Config.COLORS['info']
        )
        
        if static_emojis:
            static_text = " ".join([str(emoji) for emoji in static_emojis[:20]])
            if len(static_emojis) > 20:
                static_text += f"\n... и ещё {len(static_emojis) - 20}"
            
            embed.add_field(
                name=f"😀 Обычные ({len(static_emojis)})",
                value=static_text,
                inline=False
            )
        
        if animated_emojis:
            animated_text = " ".join([str(emoji) for emoji in animated_emojis[:20]])
            if len(animated_emojis) > 20:
                animated_text += f"\n... и ещё {len(animated_emojis) - 20}"
            
            embed.add_field(
                name=f"✨ Анимированные ({len(animated_emojis)})",
                value=animated_text,
                inline=False
            )
        
        embed.set_footer(text="Показаны первые 20 эмодзи каждого типа")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="timestamp", description="⏰ Генератор временных меток Discord")
    @app_commands.describe(format="Формат времени (R - относительное, F - полное, D - дата)")
    async def timestamp(self, interaction: discord.Interaction, format: str = "R"):
        """Генерирует временные метки Discord"""
        current_time = int(datetime.now().timestamp())
        
        formats = {
            "t": ("Короткое время", f"<t:{current_time}:t>"),
            "T": ("Длинное время", f"<t:{current_time}:T>"),
            "d": ("Короткая дата", f"<t:{current_time}:d>"),
            "D": ("Длинная дата", f"<t:{current_time}:D>"),
            "f": ("Короткая дата/время", f"<t:{current_time}:f>"),
            "F": ("Длинная дата/время", f"<t:{current_time}:F>"),
            "R": ("Относительное время", f"<t:{current_time}:R>")
        }
        
        if format.upper() not in formats:
            format = "R"
        
        format = format.upper()
        format_name, timestamp_code = formats[format]
        
        embed = discord.Embed(
            title="⏰ Генератор временных меток",
            color=Config.COLORS['info']
        )
        
        embed.add_field(
            name="📋 Выбранный формат",
            value=f"**{format_name}** (`{format}`)",
            inline=False
        )
        
        embed.add_field(
            name="✨ Результат",
            value=timestamp_code,
            inline=False
        )
        
        embed.add_field(
            name="📝 Код для копирования",
            value=f"`{timestamp_code}`",
            inline=False
        )
        
        all_formats = []
        for fmt, (name, code) in formats.items():
            all_formats.append(f"`{fmt}` - {name}")
        
        embed.add_field(
            name="📋 Все форматы",
            value="\n".join(all_formats),
            inline=False
        )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="stats", description="📊 Расширенная статистика сервера")
    async def stats(self, interaction: discord.Interaction):
        """Показывает расширенную статистику сервера"""
        guild = interaction.guild
        
        # Подсчеты
        total_members = guild.member_count
        humans = len([m for m in guild.members if not m.bot])
        bots = total_members - humans
        
        # Активность участников
        online_members = len([m for m in guild.members if m.status != discord.Status.offline])
        
        # Каналы
        text_channels = len(guild.text_channels)
        voice_channels = len(guild.voice_channels)
        
        # Роли
        roles_count = len(guild.roles) - 1  # Исключаем @everyone
        
        # Эмодзи
        emojis_count = len(guild.emojis)
        animated_emojis = len([e for e in guild.emojis if e.animated])
        
        # Бусты
        boost_level = guild.premium_tier
        boost_count = guild.premium_subscription_count
        
        embed = discord.Embed(
            title=f"📊 Статистика сервера {guild.name}",
            color=Config.COLORS['info']
        )
        
        embed.add_field(
            name="👥 Участники",
            value=f"**Всего:** {total_members}\n**Людей:** {humans}\n**Ботов:** {bots}\n**Онлайн:** {online_members}",
            inline=True
        )
        
        embed.add_field(
            name="📺 Каналы",
            value=f"**Всего:** {text_channels + voice_channels}\n**Текстовых:** {text_channels}\n**Голосовых:** {voice_channels}",
            inline=True
        )
        
        embed.add_field(
            name="🎭 Роли и эмодзи",
            value=f"**Ролей:** {roles_count}\n**Эмодзи:** {emojis_count}\n**Анимированных:** {animated_emojis}",
            inline=True
        )
        
        embed.add_field(
            name="🚀 Буст статус",
            value=f"**Уровень:** {boost_level}\n**Бустов:** {boost_count}",
            inline=True
        )
        
        # Проценты
        if total_members > 0:
            human_percent = round((humans / total_members) * 100)
            online_percent = round((online_members / total_members) * 100)
            
            embed.add_field(
                name="📈 Проценты",
                value=f"**Людей:** {human_percent}%\n**Онлайн:** {online_percent}%",
                inline=True
            )
        
        # Дата создания
        days_old = (datetime.now() - guild.created_at.replace(tzinfo=None)).days
        embed.add_field(
            name="📅 Возраст сервера",
            value=f"{days_old} дней",
            inline=True
        )
        
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        
        embed.timestamp = datetime.now()
        embed.set_footer(text=f"ID сервера: {guild.id}")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="utility_help", description="❓ Помощь по утилитарным командам")
    async def utility_help(self, interaction: discord.Interaction):
        """Показывает помощь по утилитарным командам"""
        embed = discord.Embed(
            title="🔧 Утилитарные команды",
            description="Полезные инструменты для сервера и пользователей",
            color=Config.COLORS['utility']
        )
        
        commands_list = [
            "`/ping` - Проверить задержку бота",
            "`/serverinfo` - Подробная информация о сервере",
            "`/userinfo [@пользователь]` - Информация о пользователе",
            "`/botinfo` - Статистика и информация о боте",
            "`/uptime` - Время работы бота и системы",
            "`/invite` - Ссылка для приглашения бота",
            "`/channelinfo` - Информация о текущем канале",
            "`/roleinfo [роль]` - Детали роли и права",
            "`/emoji_list` - Список эмодзи сервера",
            "`/timestamp [формат]` - Генератор временных меток",
            "`/stats` - Расширенная статистика сервера"
        ]
        
        embed.add_field(
            name="📋 Команды:",
            value="\n".join(commands_list),
            inline=False
        )
        
        embed.add_field(
            name="⏰ Форматы времени:",
            value="`t` - Короткое время\n`T` - Длинное время\n`d` - Короткая дата\n`D` - Длинная дата\n`f` - Короткая дата/время\n`F` - Длинная дата/время\n`R` - Относительное время",
            inline=False
        )
        
        embed.set_footer(text="Эти команды помогут вам получить полезную информацию! 📊")
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Utility(bot))
