import discord
from discord.ext import commands
import asyncio
import os
from config import Config

# Настройка интентов
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

# Создание бота
bot = commands.Bot(command_prefix='!', intents=intents, help_command=None)

@bot.event
async def on_ready():
    """Событие при готовности бота"""
    print(f'{bot.user} подключился к Discord!')
    try:
        synced = await bot.tree.sync()
        print(f'Синхронизировано {len(synced)} slash команд')
    except Exception as e:
        print(f'Ошибка синхронизации команд: {e}')

@bot.event
async def on_command_error(ctx, error):
    """Обработка ошибок команд"""
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("❌ Команда не найдена. Используйте `/help` для списка команд.")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ У вас недостаточно прав для выполнения этой команды.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Не хватает обязательных аргументов для команды.")
    else:
        await ctx.send(f"❌ Произошла ошибка: {str(error)}")

@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error):
    """Обработка ошибок slash команд"""
    try:
        if isinstance(error, discord.app_commands.MissingPermissions):
            message = "❌ У вас недостаточно прав для выполнения этой команды."
        else:
            message = f"❌ Произошла ошибка: {str(error)}"
        
        # Проверяем, был ли ответ уже отправлен
        if not interaction.response.is_done():
            await interaction.response.send_message(message, ephemeral=True)
        else:
            await interaction.followup.send(message, ephemeral=True)
    except Exception:
        # Игнорируем ошибки обработки ошибок
        pass

class HelpView(discord.ui.View):
    """Интерактивное меню помощи с кнопками"""
    
    def __init__(self):
        super().__init__(timeout=300)  # 5 минут
    
    @discord.ui.button(label="🎮 Развлечения", style=discord.ButtonStyle.primary, row=0)
    async def entertainment_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        commands = [
            "`/joke` - Случайные анекдоты и шутки",
            "`/quote` - Мотивационные цитаты",
            "`/fact` - Интересные факты", 
            "`/flip` - Подбросить монетку",
            "`/dice [стороны]` - Бросить кубик",
            "`/8ball [вопрос]` - Магический шар предсказаний",
            "`/choose [варианты]` - Выбрать из вариантов",
            "`/meme` - Случайные мемы",
            "`/compliment [@пользователь]` - Сделать комплимент",
            "`/roast [@пользователь]` - Дружеская шутка",
            "`/random_number [мин] [макс]` - Случайное число",
            "`/avatar [@пользователь]` - Показать аватар",
            "`/wisdom` - Мудрые мысли",
            "`/riddle` - Загадки с ответами",
            "`/color` - Случайный цвет с кодами",
            "`/inspire` - Вдохновляющие цитаты"
        ]
        
        embed = discord.Embed(
            title="🎮 Команды развлечений (16)",
            description="\n".join(commands),
            color=0xff69b4
        )
        embed.set_footer(text="Развлекайтесь и веселитесь!")
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="🎯 Игры", style=discord.ButtonStyle.primary, row=0)
    async def games_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        commands = [
            "`/guess_number [макс]` - Угадай загаданное число",
            "`/rps [выбор]` - Камень, ножницы, бумага",
            "`/trivia` - Викторина с вопросами", 
            "`/word_chain` - Игра в цепочку слов",
            "`/memory_game` - Тренировка памяти",
            "`/coin_battle [@пользователь]` - Битва монеток",
            "`/stop_game` - Остановить активную игру",
            "`/games_help` - Помощь по играм"
        ]
        
        embed = discord.Embed(
            title="🎯 Игровые команды (8)",
            description="\n".join(commands),
            color=0x32cd32
        )
        embed.set_footer(text="Играйте и соревнуйтесь с друзьями!")
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="💕 Любовь", style=discord.ButtonStyle.primary, row=0)
    async def love_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        commands = [
            "`/love [имя1] [имя2]` - Калькулятор совместимости",
            "`/crush` - Узнать тайного поклонника на сервере", 
            "`/marry [@пользователь]` - Сделать предложение",
            "`/ship [@пользователь1] [@пользователь2]` - Создать пару",
            "`/valentine [@пользователь]` - Отправить валентинку"
        ]
        
        embed = discord.Embed(
            title="💕 Команды любви (5)",
            description="\n".join(commands),
            color=0xff1493
        )
        embed.set_footer(text="Любовь - это прекрасно!")
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="🛡️ Модерация", style=discord.ButtonStyle.secondary, row=1)
    async def moderation_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        commands = [
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
            "`/unlock` - Разблокировать канал",
            "`/moderation_help` - Помощь по модерации"
        ]
        
        embed = discord.Embed(
            title="🛡️ Команды модерации (13)",
            description="\n".join(commands),
            color=0xff4500
        )
        embed.set_footer(text="Требуются соответствующие права!")
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="🔧 Утилиты", style=discord.ButtonStyle.secondary, row=1)
    async def utility_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        commands = [
            "`/ping` - Проверить задержку бота",
            "`/serverinfo` - Подробная информация о сервере",
            "`/userinfo [@пользователь]` - Информация о пользователе",
            "`/botinfo` - Статистика и информация о боте",
            "`/uptime` - Время работы системы",
            "`/invite` - Пригласить бота на сервер",
            "`/channelinfo` - Информация о текущем канале", 
            "`/roleinfo [роль]` - Детали роли и права",
            "`/emoji_list` - Список эмодзи сервера",
            "`/timestamp [формат]` - Генератор временных меток",
            "`/stats` - Расширенная статистика сервера",
            "`/utility_help` - Помощь по утилитам"
        ]
        
        embed = discord.Embed(
            title="🔧 Утилитарные команды (12)",
            description="\n".join(commands),
            color=0x4169e1
        )
        embed.set_footer(text="Полезные инструменты для сервера!")
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="⚙️ Управление", style=discord.ButtonStyle.secondary, row=1)
    async def management_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        commands = [
            "`/set_welcome [#канал]` - Настроить канал приветствия",
            "`/set_leave [#канал]` - Настроить канал прощания",
            "`/set_autorole [@роль]` - Авто-выдача роли новичкам",
            "`/mass_role [@роль] [действие]` - Массовое управление ролями",
            "`/purge_bots` - Удалить всех ботов с сервера",
            "`/backup_roles` - Создать резервную копию ролей",
            "`/server_stats` - Расширенная статистика сервера",
            "`/nickname_all [никнейм]` - Массовое изменение никнеймов"
        ]
        
        embed = discord.Embed(
            title="⚙️ Управление сервером (8)",
            description="\n".join(commands),
            color=0x9932cc
        )
        embed.set_footer(text="Требуются права администратора!")
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="📋 Логи", style=discord.ButtonStyle.success, row=2)
    async def logs_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        commands = [
            "`/set_log_channel [#канал]` - Настроить канал для логов"
        ]
        
        events = [
            "• Удаление и изменение сообщений",
            "• Изменения участников (роли, никнеймы)",
            "• Создание/удаление каналов и ролей",
            "• Баны и разбаны пользователей",
            "• Активность в голосовых каналах",
            "• Изменения аватаров пользователей"
        ]
        
        embed = discord.Embed(
            title="📋 Система логирования (1 команда + автособытия)",
            description="\n".join(commands),
            color=0x00bfff
        )
        embed.add_field(
            name="Автоматически отслеживаемые события:",
            value="\n".join(events),
            inline=False
        )
        embed.set_footer(text="Полное отслеживание активности сервера!")
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="🏠 Приватные комнаты", style=discord.ButtonStyle.success, row=2)
    async def private_rooms_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        commands = [
            "`/setup_private_rooms [категория] [канал_входа]` - Настроить систему",
            "`/private_room_settings [действие] [@пользователь]` - Управление комнатой",
            "`/rename_room [название]` - Переименовать свою комнату",
            "`/room_limit [число]` - Установить лимит участников"
        ]
        
        features = [
            "• Автосоздание личных каналов при входе",
            "• Голосовой + текстовый канал для каждого",
            "• Полное управление доступом к комнате",
            "• Автоудаление при покидании всех участников"
        ]
        
        embed = discord.Embed(
            title="🏠 Приватные комнаты (4)",
            description="\n".join(commands),
            color=0x8a2be2
        )
        embed.add_field(
            name="Возможности системы:",
            value="\n".join(features),
            inline=False
        )
        embed.set_footer(text="Создавайте личные пространства для общения!")
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="🎲 Дополнительные", style=discord.ButtonStyle.success, row=2)
    async def extended_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        commands = [
            "`/fortune` - Предсказание судьбы на день",
            "`/horoscope [знак]` - Персональный гороскоп",
            "`/magic_quote` - Вдохновляющая цитата дня",
            "`/dream_meaning [сон]` - Толкование снов",
            "`/poll [вопрос] [варианты]` - Создать голосование",
            "`/remind [минуты] [текст]` - Установить напоминание",
            "`/would_you_rather` - Игра 'Что бы вы выбрали?'",
            "`/weather_mood [погода]` - Настроение по погоде",
            "`/tech_fact` - Факт о технологиях",
            "`/random_fact` - Случайный интересный факт",
            "`/calculate [выражение]` - Математический калькулятор",
            "`/word_association [слово]` - Игра в ассоциации"
        ]
        
        embed = discord.Embed(
            title="🎲 Дополнительные команды (12)",
            description="\n".join(commands),
            color=0xffa500
        )
        embed.set_footer(text="Разнообразные полезные функции!")
        await interaction.response.edit_message(embed=embed, view=self)
    
    @discord.ui.button(label="🏠 Главное меню", style=discord.ButtonStyle.danger, row=3)
    async def home_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="🤖 Справка по командам бота",
            description="**Добро пожаловать в систему помощи!**\n\nВыберите категорию команд, чтобы увидеть подробную информацию:",
            color=0x00ff00
        )
        
        categories = [
            "🎮 **Развлечения (16)** - шутки, мемы, загадки, цвета",
            "🎯 **Игры (8)** - викторины, угадайки, соревнования",
            "💕 **Любовь (5)** - совместимость, романтика, свадьбы",
            "🛡️ **Модерация (13)** - управление участниками и каналами",
            "🔧 **Утилиты (12)** - информация, статистика, инструменты",
            "⚙️ **Управление (8)** - настройка сервера, автоматизация",
            "📋 **Логи (1 + события)** - отслеживание активности",
            "🏠 **Приватные комнаты (4)** - личные каналы",
            "🎲 **Дополнительные (12)** - гороскопы, калькуляторы, факты"
        ]
        
        embed.add_field(
            name="📊 Всего команд: 82+",
            value="\n".join(categories),
            inline=False
        )
        
        embed.add_field(
            name="ℹ️ Как пользоваться:",
            value="• Нажмите на кнопку нужной категории\n• Изучите доступные команды\n• Используйте команды начиная с `/`",
            inline=False
        )
        
        embed.set_footer(text="Нажмите на кнопки ниже для просмотра команд по категориям")
        await interaction.response.edit_message(embed=embed, view=self)

@bot.tree.command(name="help", description="Показать интерактивную справку по командам")
async def help_command(interaction: discord.Interaction):
    """Главная команда помощи с интерактивными кнопками"""
    try:
        embed = discord.Embed(
            title="🤖 Справка по командам бота",
            description="**Добро пожаловать в систему помощи!**\n\nВыберите категорию команд, чтобы увидеть подробную информацию:",
            color=0x00ff00
        )
        
        categories = [
            "🎮 **Развлечения (16)** - шутки, мемы, загадки, цвета",
            "🎯 **Игры (8)** - викторины, угадайки, соревнования", 
            "💕 **Любовь (5)** - совместимость, романтика, свадьбы",
            "🛡️ **Модерация (13)** - управление участниками и каналами",
            "🔧 **Утилиты (12)** - информация, статистика, инструменты",
            "⚙️ **Управление (8)** - настройка сервера, автоматизация",
            "📋 **Логи (1 + события)** - отслеживание активности",
            "🏠 **Приватные комнаты (4)** - личные каналы",
            "🎲 **Дополнительные (12)** - гороскопы, калькуляторы, факты"
        ]
        
        embed.add_field(
            name="📊 Всего команд: 82+",
            value="\n".join(categories),
            inline=False
        )
        
        embed.add_field(
            name="ℹ️ Как пользоваться:",
            value="• Нажмите на кнопку нужной категории\n• Изучите доступные команды\n• Используйте команды начиная с `/`",
            inline=False
        )
        
        embed.set_footer(text="Нажмите на кнопки ниже для просмотра команд по категориям")
        
        view = HelpView()
        await interaction.response.send_message(embed=embed, view=view)
        
    except Exception as e:
        # Упрощенный fallback без embed и кнопок
        commands_text = """**🤖 Справка по командам бота (82+):**

Основные категории команд:

🎮 **Развлечения:** /joke /quote /fact /flip /dice /8ball /choose /meme /compliment /roast /random_number /avatar /wisdom /riddle /color /inspire

🎯 **Игры:** /guess_number /rps /trivia /word_chain /memory_game /coin_battle /stop_game

💕 **Любовь:** /love /crush /marry /ship /valentine

🛡️ **Модерация:** /kick /ban /unban /mute /unmute /warn /check_warnings /clear_warnings /clear /slowmode /lock /unlock

🔧 **Утилиты:** /ping /serverinfo /userinfo /botinfo /uptime /invite /channelinfo /roleinfo /emoji_list /timestamp /stats

⚙️ **Управление:** /set_welcome /set_autorole /mass_role /server_stats /backup_roles

📋 **Логи:** /set_log_channel

🏠 **Приватные комнаты:** /setup_private_rooms /private_room_settings /rename_room /room_limit

🎲 **Дополнительные:** /fortune /horoscope /poll /remind /calculate /weather_mood /tech_fact /random_fact /dream_meaning /would_you_rather

Всего 82+ команды в 9 категориях для всех ваших нужд!"""
        
        await interaction.response.send_message(commands_text)

async def load_cogs():
    """Загрузка всех расширений"""
    cogs = [
        'cogs.entertainment',
        'cogs.moderation', 
        'cogs.utility',
        'cogs.games',
        'cogs.love_calculator',
        'cogs.server_management',
        'cogs.server_logs',
        'cogs.private_rooms',
        'cogs.extended_commands'
    ]
    
    for cog in cogs:
        try:
            await bot.load_extension(cog)
            print(f'Загружен модуль: {cog}')
        except Exception as e:
            print(f'Ошибка загрузки модуля {cog}: {e}')

async def main():
    """Основная функция запуска бота"""
    async with bot:
        await load_cogs()
        token = os.getenv('DISCORD_TOKEN', 'YOUR_BOT_TOKEN_HERE')
        await bot.start(token)

if __name__ == '__main__':
    asyncio.run(main())
