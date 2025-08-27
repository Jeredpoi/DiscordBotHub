import discord
from discord.ext import commands
from discord import app_commands
import random
import hashlib
from config import Config

class LoveCalculator(commands.Cog):
    """Команды любви и совместимости"""
    
    def __init__(self, bot):
        self.bot = bot
    
    def calculate_love_percentage(self, name1: str, name2: str) -> int:
        """Вычисляет процент совместимости на основе имен"""
        # Нормализуем имена
        name1 = name1.lower().strip()
        name2 = name2.lower().strip()
        
        # Создаем уникальный хеш для пары
        combined = "".join(sorted([name1, name2]))
        hash_value = int(hashlib.md5(combined.encode()).hexdigest()[:8], 16)
        
        # Конвертируем в процент (0-100)
        percentage = hash_value % 101
        
        return percentage
    
    def get_love_description(self, percentage: int) -> tuple:
        """Возвращает описание и цвет для процента любви"""
        if percentage >= 90:
            return ("💕 Идеальная пара! Вы созданы друг для друга! Ваша любовь как сказка!", Config.COLORS['success'])
        elif percentage >= 75:
            return ("❤️ Отличная совместимость! У вас прекрасные отношения и светлое будущее!", Config.COLORS['success'])
        elif percentage >= 60:
            return ("💗 Хорошая пара! Ваши отношения полны любви и понимания!", Config.COLORS['info'])
        elif percentage >= 45:
            return ("💛 Средняя совместимость. Вам нужно больше работать над отношениями!", Config.COLORS['warning'])
        elif percentage >= 30:
            return ("🧡 Низкая совместимость. Отношения требуют много усилий с обеих сторон.", Config.COLORS['warning'])
        elif percentage >= 15:
            return ("💔 Очень низкая совместимость. Возможно, вы лучше подходите как друзья.", Config.COLORS['error'])
        else:
            return ("💥 Практически несовместимы! Но помните - любовь может творить чудеса!", Config.COLORS['error'])
    
    def create_love_bar(self, percentage: int) -> str:
        """Создает визуальную полосу любви"""
        filled = "💖" * (percentage // 10)
        empty = "🤍" * (10 - (percentage // 10))
        return filled + empty
    
    @app_commands.command(name="love", description="💕 Калькулятор любви и совместимости")
    @app_commands.describe(person1="Первое имя или пользователь", person2="Второе имя или пользователь")
    async def love_calculator(self, interaction: discord.Interaction, person1: str, person2: str = None):
        """Вычисляет процент совместимости между двумя людьми"""
        # Если второй параметр не указан, используем автора команды
        if person2 is None:
            person2 = interaction.user.display_name
        
        # Очищаем имена от упоминаний Discord
        name1 = person1.replace('<@', '').replace('>', '').replace('!', '')
        name2 = person2.replace('<@', '').replace('>', '').replace('!', '')
        
        # Пытаемся получить имена пользователей если это ID
        try:
            if name1.isdigit():
                user1 = await self.bot.fetch_user(int(name1))
                name1 = user1.display_name
        except:
            pass
        
        try:
            if name2.isdigit():
                user2 = await self.bot.fetch_user(int(name2))
                name2 = user2.display_name
        except:
            pass
        
        # Вычисляем совместимость
        percentage = self.calculate_love_percentage(name1, name2)
        description, color = self.get_love_description(percentage)
        love_bar = self.create_love_bar(percentage)
        
        embed = discord.Embed(
            title="💕 Калькулятор любви",
            color=color
        )
        
        embed.add_field(
            name="👫 Пара",
            value=f"**{name1}** 💕 **{name2}**",
            inline=False
        )
        
        embed.add_field(
            name="💯 Совместимость",
            value=f"**{percentage}%**",
            inline=True
        )
        
        embed.add_field(
            name="📊 Прогресс",
            value=love_bar,
            inline=False
        )
        
        embed.add_field(
            name="💭 Описание",
            value=description,
            inline=False
        )
        
        # Добавляем забавные комментарии
        if percentage == 69:
            embed.add_field(name="😏", value="Ну ничего себе число! 😉", inline=False)
        elif percentage == 100:
            embed.add_field(name="✨", value="Абсолютное совершенство! Редкая удача! 🌟", inline=False)
        elif percentage == 0:
            embed.add_field(name="💥", value="Даже математика против этого союза! 😅", inline=False)
        
        embed.set_footer(text="💕 Любовь не измеряется числами, но это весело! 💕")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="crush", description="💘 Узнать своего тайного поклонника")
    async def crush(self, interaction: discord.Interaction):
        """Выбирает случайного участника сервера как тайного поклонника"""
        guild = interaction.guild
        
        # Получаем всех участников кроме ботов и самого пользователя
        potential_crushes = [
            member for member in guild.members 
            if not member.bot and member.id != interaction.user.id
        ]
        
        if not potential_crushes:
            await interaction.response.send_message("❌ На сервере недостаточно участников для поиска поклонника!", ephemeral=True)
            return
        
        # Выбираем случайного поклонника (детерминированно на основе ID пользователя)
        user_id_str = str(interaction.user.id)
        random.seed(int(user_id_str[-6:]))  # Используем последние 6 цифр ID как seed
        crush = random.choice(potential_crushes)
        random.seed()  # Сбрасываем seed
        
        # Генерируем романтические сообщения
        romantic_messages = [
            f"тайно восхищается вашей харизмой",
            f"думает о вас каждый день",
            f"считает вас самым особенным человеком на сервере",
            f"мечтает провести с вами время",
            f"находит ваше чувство юмора неотразимым",
            f"втайне надеется на ваше внимание",
            f"считает вас невероятно привлекательным",
            f"мечтает о совместном будущем"
        ]
        
        message = random.choice(romantic_messages)
        
        embed = discord.Embed(
            title="💘 Ваш тайный поклонник!",
            description=f"**{crush.display_name}** {message}! 💕",
            color=Config.COLORS['entertainment']
        )
        
        embed.set_thumbnail(url=crush.display_avatar.url)
        
        embed.add_field(
            name="💌 Совет",
            value="Может быть, стоит начать разговор? 😉",
            inline=False
        )
        
        embed.set_footer(text="💕 Это всего лишь игра! Не принимайте всерьез! 💕")
        
        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @app_commands.command(name="marry", description="💒 Сделать предложение пользователю")
    @app_commands.describe(user="Пользователь, которому хотите сделать предложение")
    async def marry(self, interaction: discord.Interaction, user: discord.Member):
        """Делает романтическое предложение пользователю"""
        if user.id == interaction.user.id:
            await interaction.response.send_message("❌ Вы не можете жениться на самом себе! 😅", ephemeral=True)
            return
        
        if user.bot:
            await interaction.response.send_message("❌ Боты не умеют любить... пока что! 🤖💔", ephemeral=True)
            return
        
        proposals = [
            f"💍 **{interaction.user.display_name}** делает предложение **{user.display_name}**!\n\n*'Хочешь провести со мной всю оставшуюся жизнь?'* 💕",
            f"💒 **{interaction.user.display_name}** встает на одно колено перед **{user.display_name}**!\n\n*'Будешь моей половинкой навсегда?'* 🌹",
            f"💎 **{interaction.user.display_name}** достает кольцо для **{user.display_name}**!\n\n*'Хочешь стать моим спутником жизни?'* ✨",
            f"👰‍♀️🤵‍♂️ **{interaction.user.display_name}** просит руки **{user.display_name}**!\n\n*'Давай создадим семью вместе!'* 💖"
        ]
        
        proposal = random.choice(proposals)
        
        embed = discord.Embed(
            title="💒 Предложение!",
            description=proposal,
            color=Config.COLORS['entertainment']
        )
        
        # Добавляем романтическую статистику
        compatibility = self.calculate_love_percentage(interaction.user.display_name, user.display_name)
        embed.add_field(
            name="💕 Совместимость",
            value=f"{compatibility}%",
            inline=True
        )
        
        responses = [
            "Скажет ли 'Да'? 💕",
            "Какой будет ответ? 💭",
            "Момент истины! 💎",
            "Сердце замирает в ожидании... 💓"
        ]
        
        embed.add_field(
            name="💭 Ожидание",
            value=random.choice(responses),
            inline=True
        )
        
        embed.set_footer(text="💕 Это романтическая игра! Наслаждайтесь моментом! 💕")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="ship", description="🚢 Создать пару из двух пользователей")
    @app_commands.describe(user1="Первый пользователь", user2="Второй пользователь")
    async def ship(self, interaction: discord.Interaction, user1: discord.Member, user2: discord.Member):
        """Создает 'корабль' (пару) из двух пользователей"""
        if user1.id == user2.id:
            await interaction.response.send_message("❌ Нельзя создать пару из одного человека! 😅", ephemeral=True)
            return
        
        if user1.bot or user2.bot:
            await interaction.response.send_message("❌ Боты не участвуют в романтических отношениях! 🤖", ephemeral=True)
            return
        
        # Создаем название пары (ship name)
        name1 = user1.display_name
        name2 = user2.display_name
        
        # Несколько вариантов создания ship name
        ship_options = [
            name1[:len(name1)//2] + name2[len(name2)//2:],
            name1[:3] + name2[-3:],
            name2[:len(name2)//2] + name1[len(name1)//2:],
            name2[:3] + name1[-3:]
        ]
        
        ship_name = random.choice(ship_options)
        
        # Вычисляем совместимость
        compatibility = self.calculate_love_percentage(name1, name2)
        description, color = self.get_love_description(compatibility)
        love_bar = self.create_love_bar(compatibility)
        
        embed = discord.Embed(
            title="🚢 Новый корабль отплывает!",
            color=color
        )
        
        embed.add_field(
            name="💕 Пара",
            value=f"**{user1.display_name}** × **{user2.display_name}**",
            inline=False
        )
        
        embed.add_field(
            name="🏷️ Название пары",
            value=f"**#{ship_name}**",
            inline=True
        )
        
        embed.add_field(
            name="💯 Совместимость",
            value=f"**{compatibility}%**",
            inline=True
        )
        
        embed.add_field(
            name="📊 Полоса любви",
            value=love_bar,
            inline=False
        )
        
        embed.add_field(
            name="💭 Прогноз",
            value=description,
            inline=False
        )
        
        # Добавляем забавные предсказания
        predictions = [
            "Их первое свидание будет в кафе ☕",
            "Они поженятся через 2 года 💒",
            "У них будет 3 детей 👶",
            "Они будут путешествовать вместе 🌍",
            "Их любимой песней станет романтическая баллада 🎵",
            "Они заведут милого домашнего питомца 🐱",
            "Их отношения будут полны смеха 😂",
            "Они будут готовить ужин вместе каждый день 🍽️"
        ]
        
        embed.add_field(
            name="🔮 Предсказание",
            value=random.choice(predictions),
            inline=False
        )
        
        embed.set_footer(text="🚢 Это игра в создание пар! Развлекайтесь! 🚢")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="valentine", description="💌 Отправить валентинку")
    @app_commands.describe(user="Пользователь для отправки валентинки")
    async def valentine(self, interaction: discord.Interaction, user: discord.Member):
        """Отправляет романтическую валентинку пользователю"""
        if user.id == interaction.user.id:
            await interaction.response.send_message("❌ Отправлять валентинки самому себе... интересно, но грустно! 💔", ephemeral=True)
            return
        
        if user.bot:
            await interaction.response.send_message("❌ Боты не понимают романтику... пока что! 🤖💔", ephemeral=True)
            return
        
        valentine_messages = [
            "🌹 Розы красные, фиалки синие, ты особенный, и это правда! 🌹",
            "💖 Ты делаешь мой день ярче каждый раз, когда появляешься онлайн! 💖",
            "✨ Если бы я мог переименовать красоту, я бы назвал её твоим именем! ✨",
            "🌟 Ты - звезда в моем Discord сервере! 🌟",
            "💕 Мое сердце делает 'пинг' каждый раз, когда вижу твое сообщение! 💕",
            "🦋 Ты даешь мне бабочек в животе, даже через интернет! 🦋",
            "🌈 Ты добавляешь цвета в мой серый мир! 🌈",
            "💎 Ты драгоценнее всех эмодзи в Discord! 💎"
        ]
        
        valentine_message = random.choice(valentine_messages)
        
        embed = discord.Embed(
            title="💌 Валентинка доставлена!",
            description=f"**От:** {interaction.user.mention}\n**Для:** {user.mention}\n\n{valentine_message}",
            color=0xff1493  # Deep pink
        )
        
        # Добавляем случайные романтические элементы
        romantic_elements = [
            "💕💖💗💓💝💘💞💟",
            "🌹🌷🌺🌸🌼🌻🌛⭐",
            "✨💫⭐🌟💖💕💗💓",
            "🦋🌈💎👑💝🎁💌💐"
        ]
        
        embed.add_field(
            name="💖",
            value=random.choice(romantic_elements),
            inline=False
        )
        
        # Добавляем романтический совет
        romantic_tips = [
            "Любовь начинается с дружбы! 💫",
            "Улыбка - лучший макияж! 😊",
            "Будьте собой - это привлекательно! ✨",
            "Добрые слова творят чудеса! 🌟",
            "Любовь делает мир ярче! 🌈"
        ]
        
        embed.add_field(
            name="💡 Совет дня",
            value=random.choice(romantic_tips),
            inline=False
        )
        
        embed.set_footer(text="💕 Распространяйте любовь и позитив! 💕")
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(LoveCalculator(bot))
