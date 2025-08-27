import discord
from discord.ext import commands
from discord import app_commands
import random
import asyncio
from config import Config

class Entertainment(commands.Cog):
    """Развлекательные команды бота"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="joke", description="🎭 Случайный анекдот или шутка")
    async def joke(self, interaction: discord.Interaction):
        """Отправляет случайный анекдот"""
        joke = random.choice(Config.JOKES)
        
        embed = discord.Embed(
            title="😂 Анекдот",
            description=joke,
            color=Config.COLORS['entertainment']
        )
        embed.set_footer(text="Надеемся, вам понравилось! 🎭")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="quote", description="💭 Мотивационная цитата")
    async def quote(self, interaction: discord.Interaction):
        """Отправляет мотивационную цитату"""
        quote = random.choice(Config.QUOTES)
        
        embed = discord.Embed(
            title="💡 Мотивационная цитата",
            description=f"*{quote}*",
            color=Config.COLORS['info']
        )
        embed.set_footer(text="Будьте вдохновлены! ✨")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="fact", description="🧠 Интересный факт")
    async def fact(self, interaction: discord.Interaction):
        """Отправляет интересный факт"""
        fact = random.choice(Config.FACTS)
        
        embed = discord.Embed(
            title="🎓 Интересный факт",
            description=fact,
            color=Config.COLORS['utility']
        )
        embed.set_footer(text="Знания - сила! 🚀")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="flip", description="🪙 Подбросить монетку")
    async def flip(self, interaction: discord.Interaction):
        """Подбрасывает монетку"""
        result = random.choice(["Орёл", "Решка"])
        
        embed = discord.Embed(
            title="🪙 Подбрасывание монетки",
            description=f"**Результат: {result}!**",
            color=Config.COLORS['entertainment']
        )
        embed.set_footer(text="Удача решает всё! 🍀")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="dice", description="🎲 Бросить кубик")
    @app_commands.describe(sides="Количество сторон кубика (по умолчанию 6)")
    async def dice(self, interaction: discord.Interaction, sides: int = 6):
        """Бросает кубик с заданным количеством сторон"""
        if sides < 2:
            await interaction.response.send_message("❌ Кубик должен иметь минимум 2 стороны!", ephemeral=True)
            return
        
        if sides > 1000:
            await interaction.response.send_message("❌ Слишком много сторон! Максимум 1000.", ephemeral=True)
            return
        
        result = random.randint(1, sides)
        
        embed = discord.Embed(
            title="🎲 Бросок кубика",
            description=f"**Кубик с {sides} сторонами**\n**Результат: {result}**",
            color=Config.COLORS['entertainment']
        )
        embed.set_footer(text="Пусть удача будет с вами! 🎯")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="8ball", description="🔮 Магический шар предсказаний")
    @app_commands.describe(question="Ваш вопрос для магического шара")
    async def eight_ball(self, interaction: discord.Interaction, question: str):
        """Магический шар отвечает на ваш вопрос"""
        responses = [
            "Определенно да", "Без сомнения", "Да, конечно", "Можешь быть уверен(а)",
            "Скорее всего", "Хорошие перспективы", "Да", "Знаки указывают на да",
            "Ответ туманен, попробуй снова", "Спроси позже", "Лучше не говорить тебе сейчас",
            "Не могу предсказать сейчас", "Сконцентрируйся и спроси снова",
            "Не рассчитывай на это", "Мой ответ - нет", "Мои источники говорят нет",
            "Перспективы не очень хорошие", "Весьма сомнительно"
        ]
        
        answer = random.choice(responses)
        
        embed = discord.Embed(
            title="🔮 Магический шар",
            color=Config.COLORS['entertainment']
        )
        embed.add_field(name="❓ Вопрос:", value=question, inline=False)
        embed.add_field(name="🔮 Ответ:", value=f"*{answer}*", inline=False)
        embed.set_footer(text="Магический шар знает всё! ✨")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="choose", description="🤔 Выбрать из вариантов")
    @app_commands.describe(options="Варианты для выбора (разделите запятыми)")
    async def choose(self, interaction: discord.Interaction, options: str):
        """Выбирает случайный вариант из предложенных"""
        choices = [choice.strip() for choice in options.split(",")]
        
        if len(choices) < 2:
            await interaction.response.send_message("❌ Укажите минимум 2 варианта, разделенных запятыми!", ephemeral=True)
            return
        
        chosen = random.choice(choices)
        
        embed = discord.Embed(
            title="🎯 Выбор сделан!",
            description=f"**Я выбираю: {chosen}**",
            color=Config.COLORS['entertainment']
        )
        embed.add_field(
            name="Варианты были:",
            value="\n".join([f"• {choice}" for choice in choices]),
            inline=False
        )
        embed.set_footer(text="Решение принято! 🎲")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="meme", description="😂 Случайный мем")
    async def meme(self, interaction: discord.Interaction):
        """Отправляет случайный мем"""
        memes = [
            "Когда код работает с первого раза... 🤔 Подозрительно...",
            "Программист: Это невозможно исправить!\n*Исправляет добавлением одной точки с запятой*",
            "99 проблем в коде, исправил одну - стало 117 проблем",
            "Комментарии в коде:\n// Это временное решение\n*код написан 3 года назад*",
            "Когда говоришь, что исправишь баг за 5 минут... *4 часа спустя*",
            "Ctrl+C, Ctrl+V - лучшие друзья программиста",
            "Документация? А что это такое? 🤷‍♂️",
            "Работает на моей машине ¯\\_(ツ)_/¯",
            "Тестирование? Мы тестируем в продакшене!",
            "git commit -m 'исправил всё'"
        ]
        
        meme = random.choice(memes)
        
        embed = discord.Embed(
            title="😂 Мем дня",
            description=meme,
            color=Config.COLORS['entertainment']
        )
        embed.set_footer(text="Смех продлевает жизнь! 🎭")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="compliment", description="🌸 Сделать комплимент")
    @app_commands.describe(user="Пользователь, которому хотите сделать комплимент")
    async def compliment(self, interaction: discord.Interaction, user: discord.Member = None):
        """Делает комплимент пользователю"""
        if user is None:
            user = interaction.user
        
        compliments = [
            "выглядит потрясающе сегодня!",
            "имеет прекрасное чувство юмора!",
            "очень талантлив(а)!",
            "делает мир лучше одним своим присутствием!",
            "имеет доброе сердце!",
            "вдохновляет окружающих!",
            "обладает невероятной харизмой!",
            "умеет поднять настроение!",
            "очень творческая личность!",
            "настоящий друг!"
        ]
        
        compliment = random.choice(compliments)
        
        embed = discord.Embed(
            title="🌸 Комплимент",
            description=f"**{user.mention} {compliment}**",
            color=Config.COLORS['success']
        )
        embed.set_footer(text="Делитесь позитивом! ✨")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="roast", description="🔥 Дружеская шутка")
    @app_commands.describe(user="Пользователь для дружеской шутки")
    async def roast(self, interaction: discord.Interaction, user: discord.Member = None):
        """Делает дружескую шутку над пользователем"""
        if user is None:
            user = interaction.user
        
        roasts = [
            "код настолько чистый, что его можно есть!",
            "программирует так хорошо, что компьютеры плачут от счастья!",
            "настолько крут(а), что баги исправляются сами!",
            "такой(ая) умный(ая), что Google спрашивает у них совета!",
            "код работает даже когда не должен!",
            "настолько хорош(а) в отладке, что баги извиняются!",
            "пишет такой элегантный код, что это искусство!",
            "такой(ая) продуктивный(ая), что IDE устаёт!",
            "настолько опытный(ая), что может программировать во сне!",
            "код настолько оптимизирован, что работает быстрее света!"
        ]
        
        roast = random.choice(roasts)
        
        embed = discord.Embed(
            title="🔥 Дружеская шутка",
            description=f"**{user.mention}, ваш {roast}**",
            color=Config.COLORS['warning']
        )
        embed.set_footer(text="Всё в шутку! 😄")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="random_number", description="🎲 Случайное число")
    @app_commands.describe(minimum="Минимальное значение", maximum="Максимальное значение")
    async def random_number(self, interaction: discord.Interaction, minimum: int = 1, maximum: int = 100):
        """Генерирует случайное число в заданном диапазоне"""
        if minimum > maximum:
            await interaction.response.send_message("❌ Минимальное значение не может быть больше максимального!", ephemeral=True)
            return
        
        if maximum - minimum > 10000000:
            await interaction.response.send_message("❌ Слишком большой диапазон! Максимум 10,000,000.", ephemeral=True)
            return
        
        number = random.randint(minimum, maximum)
        
        embed = discord.Embed(
            title="🎲 Случайное число",
            description=f"**Диапазон:** {minimum} - {maximum}\n**Результат: {number}**",
            color=Config.COLORS['entertainment']
        )
        embed.set_footer(text="Удача в числах! 🍀")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="avatar", description="🖼️ Показать аватар пользователя")
    @app_commands.describe(user="Пользователь, чей аватар показать")
    async def avatar(self, interaction: discord.Interaction, user: discord.Member = None):
        """Показывает аватар пользователя"""
        if user is None:
            user = interaction.user
        
        embed = discord.Embed(
            title=f"🖼️ Аватар {user.display_name}",
            color=Config.COLORS['info']
        )
        embed.set_image(url=user.display_avatar.url)
        embed.set_footer(text=f"Запросил: {interaction.user.display_name}")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="wisdom", description="🧙‍♂️ Мудрые мысли")
    async def wisdom(self, interaction: discord.Interaction):
        """Отправляет мудрые мысли"""
        wisdom_quotes = [
            "Лучший способ предсказать будущее - создать его.",
            "Не бойтесь делать ошибки. Бойтесь не учиться на них.",
            "Знание - это не то, что вы знаете, а то, что вы делаете с тем, что знаете.",
            "Путешествие длиною в тысячу миль начинается с первого шага.",
            "Успех - это не конечная цель, неудача - не смертельна: важна смелость продолжать.",
            "Время - самый ценный ресурс. Используйте его мудро.",
            "Простота - высшая степень изощренности.",
            "Лучший учитель - опыт. Худший - сожаление.",
            "Инвестируйте в себя. Это лучшая инвестиция в жизни.",
            "Не ждите возможности. Создавайте её."
        ]
        
        wisdom = random.choice(wisdom_quotes)
        
        embed = discord.Embed(
            title="🧙‍♂️ Мудрая мысль",
            description=f"*{wisdom}*",
            color=Config.COLORS['utility']
        )
        embed.set_footer(text="Мудрость веков! 📚")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="riddle", description="🤔 Загадка с ответом")
    async def riddle(self, interaction: discord.Interaction):
        """Отправляет загадку с отложенным ответом"""
        riddles = [
            {
                "question": "Что можно поймать, но нельзя бросить?",
                "answer": "Простуду"
            },
            {
                "question": "Что становится больше, когда его ставят вверх ногами?",
                "answer": "Число 6"
            },
            {
                "question": "У меня есть города, но нет домов. У меня есть горы, но нет деревьев. У меня есть вода, но нет рыбы. Что я?",
                "answer": "Карта"
            },
            {
                "question": "Что можно увидеть один раз в году, два раза в неделю, но никогда в день?",
                "answer": "Букву 'е'"
            },
            {
                "question": "Чем больше из этого берёшь, тем больше оставляешь позади. Что это?",
                "answer": "Следы"
            }
        ]
        
        riddle_data = random.choice(riddles)
        
        embed = discord.Embed(
            title="🤔 Загадка",
            description=riddle_data["question"],
            color=Config.COLORS['warning']
        )
        embed.set_footer(text="Подумайте... Ответ появится через 30 секунд! ⏰")
        
        await interaction.response.send_message(embed=embed)
        
        # Ожидание 30 секунд перед показом ответа
        await asyncio.sleep(30)
        
        answer_embed = discord.Embed(
            title="💡 Ответ на загадку",
            description=f"**Ответ: {riddle_data['answer']}**",
            color=Config.COLORS['success']
        )
        answer_embed.set_footer(text="Угадали? 🎯")
        
        await interaction.followup.send(embed=answer_embed)
    
    @app_commands.command(name="color", description="🎨 Случайный цвет")
    async def color(self, interaction: discord.Interaction):
        """Показывает случайный цвет с кодами"""
        color_value = random.randint(0, 0xFFFFFF)
        hex_color = f"#{color_value:06X}"
        rgb_color = f"RGB({(color_value >> 16) & 255}, {(color_value >> 8) & 255}, {color_value & 255})"
        
        embed = discord.Embed(
            title="🎨 Случайный цвет",
            color=color_value
        )
        embed.add_field(name="HEX", value=hex_color, inline=True)
        embed.add_field(name="RGB", value=rgb_color, inline=True)
        embed.add_field(name="DEC", value=str(color_value), inline=True)
        embed.set_footer(text="Красота в простоте! ✨")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="inspire", description="✨ Вдохновляющая цитата")
    async def inspire(self, interaction: discord.Interaction):
        """Отправляет вдохновляющую цитату"""
        inspirational_quotes = [
            "Ваше время ограничено, не тратьте его, живя чужой жизнью. - Стив Джобс",
            "Единственный способ делать отличную работу - любить то, что делаешь. - Стив Джобс", 
            "Жизнь - это то, что с вами происходит, пока вы строите другие планы. - Джон Леннон",
            "Будьте собой; все остальные уже заняты. - Оскар Уайльд",
            "Два самых важных дня в жизни - день рождения и день, когда вы понимаете зачем. - Марк Твен",
            "Будущее принадлежит тем, кто верит в красоту своих мечтаний. - Элеонора Рузвельт",
            "Невозможно - это не факт. Это мнение. - Пауло Коэльо",
            "Не бойтесь отказаться от хорошего ради великолепного. - Джон Рокфеллер",
            "Успех - это способность идти от неудачи к неудаче, не теряя энтузиазма. - Уинстон Черчилль",
            "Мечты не имеют срока годности. - Коко Шанель"
        ]
        
        quote = random.choice(inspirational_quotes)
        
        embed = discord.Embed(
            title="✨ Вдохновение",
            description=f"*{quote}*",
            color=Config.COLORS['success']
        )
        embed.set_footer(text="Пусть это вдохновляет вас! 🌟")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="entertainment_help", description="❓ Помощь по развлекательным командам")
    async def entertainment_help(self, interaction: discord.Interaction):
        """Показывает помощь по развлекательным командам"""
        embed = discord.Embed(
            title="🎮 Развлекательные команды",
            description="Полный список команд для развлечения и веселья!",
            color=Config.COLORS['entertainment']
        )
        
        commands_list = [
            "`/joke` - Случайные анекдоты",
            "`/quote` - Мотивационные цитаты", 
            "`/fact` - Интересные факты",
            "`/flip` - Подбросить монетку",
            "`/dice [стороны]` - Бросить кубик",
            "`/8ball [вопрос]` - Магический шар",
            "`/choose [варианты]` - Выбрать вариант",
            "`/meme` - Случайные мемы",
            "`/compliment [@пользователь]` - Комплимент",
            "`/roast [@пользователь]` - Дружеская шутка",
            "`/random_number [мин] [макс]` - Случайное число",
            "`/avatar [@пользователь]` - Показать аватар",
            "`/wisdom` - Мудрые мысли",
            "`/riddle` - Загадки с ответами",
            "`/color` - Случайный цвет",
            "`/inspire` - Вдохновляющие цитаты"
        ]
        
        embed.add_field(
            name="📋 Команды:",
            value="\n".join(commands_list),
            inline=False
        )
        
        embed.set_footer(text="Используйте эти команды для развлечения! 🎉")
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Entertainment(bot))
