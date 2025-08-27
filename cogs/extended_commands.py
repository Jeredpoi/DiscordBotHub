import discord
from discord.ext import commands
from discord import app_commands
import random
import asyncio
import re
from datetime import datetime, timedelta
from config import Config

class ExtendedCommands(commands.Cog):
    """Расширенные команды бота"""
    
    def __init__(self, bot):
        self.bot = bot
        self.active_polls = {}
        self.reminders = {}
    
    @app_commands.command(name="fortune", description="🔮 Предсказание судьбы")
    async def fortune(self, interaction: discord.Interaction):
        """Предсказывает судьбу пользователя"""
        fortunes = [
            "🌟 Впереди вас ждет невероятная удача! Будьте готовы к неожиданным возможностям.",
            "💰 Финансовое благополучие приближается. Инвестиции принесут прибыль.",
            "❤️ Любовь найдет вас в самом неожиданном месте. Откройте свое сердце.",
            "🎯 Ваши цели скоро будут достигнуты. Продолжайте двигаться вперед.",
            "🌈 После бури всегда приходит радуга. Трудности скоро закончатся.",
            "🎓 Новые знания откроют перед вами двери возможностей.",
            "🤝 Важная встреча изменит ваш жизненный путь к лучшему.",
            "🏆 Успех в делах принесет вам признание и уважение.",
            "🌅 Новый день принесет новые надежды и свершения.",
            "✨ Магия случится в вашей жизни, когда вы меньше всего этого ожидаете.",
            "🎪 Приключение, которое изменит ваш взгляд на мир, уже близко.",
            "🎨 Творческие проекты принесут вам удовлетворение и успех.",
            "🌍 Путешествие расширит ваши горизонты и подарит новых друзей.",
            "💎 Ваша истинная ценность скоро будет признана окружающими.",
            "🔑 Ключ к решению долгой проблемы находится в ваших руках."
        ]
        
        fortune_text = random.choice(fortunes)
        
        # Добавляем случайные элементы предсказания
        elements = [
            "🌙 Луна благоволит вашим начинаниям",
            "⭐ Звезды выстроились в вашу пользу", 
            "🔮 Кристальный шар показывает ясный путь",
            "🃏 Карты Таро говорят о переменах",
            "🌿 Силы природы поддержат вас"
        ]
        
        element = random.choice(elements)
        
        embed = discord.Embed(
            title="🔮 Предсказание судьбы",
            description=f"**{fortune_text}**",
            color=Config.COLORS['entertainment']
        )
        
        embed.add_field(
            name="✨ Магический элемент",
            value=element,
            inline=False
        )
        
        embed.add_field(
            name="🎯 Совет дня",
            value="Верьте в себя и свои возможности!",
            inline=False
        )
        
        embed.set_footer(text="🌟 Будущее создается сегодняшними действиями!")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="horoscope", description="♈ Гороскоп на день")
    @app_commands.describe(sign="Знак зодиака")
    async def horoscope(self, interaction: discord.Interaction, sign: str):
        """Показывает гороскоп для знака зодиака"""
        zodiac_signs = {
            "овен": {"emoji": "♈", "dates": "21.03 - 20.04"},
            "телец": {"emoji": "♉", "dates": "21.04 - 21.05"},
            "близнецы": {"emoji": "♊", "dates": "22.05 - 21.06"},
            "рак": {"emoji": "♋", "dates": "22.06 - 22.07"},
            "лев": {"emoji": "♌", "dates": "23.07 - 21.08"},
            "дева": {"emoji": "♍", "dates": "22.08 - 23.09"},
            "весы": {"emoji": "♎", "dates": "24.09 - 23.10"},
            "скорпион": {"emoji": "♏", "dates": "24.10 - 22.11"},
            "стрелец": {"emoji": "♐", "dates": "23.11 - 22.12"},
            "козерог": {"emoji": "♑", "dates": "23.12 - 20.01"},
            "водолей": {"emoji": "♒", "dates": "21.01 - 19.02"},
            "рыбы": {"emoji": "♓", "dates": "20.02 - 20.03"}
        }
        
        sign_lower = sign.lower()
        if sign_lower not in zodiac_signs:
            await interaction.response.send_message("❌ Неизвестный знак зодиака! Доступные знаки: " + ", ".join(zodiac_signs.keys()), ephemeral=True)
            return
        
        sign_data = zodiac_signs[sign_lower]
        
        horoscopes = [
            "Сегодня звезды благоволят новым начинаниям. Отличный день для важных решений!",
            "Будьте внимательны к деталям - они могут оказаться ключевыми для успеха.",
            "Ваша интуиция сегодня особенно сильна. Доверьтесь внутреннему голосу.",
            "День принесет приятные сюрпризы в личной жизни. Откройтесь для новых знакомств.",
            "Финансовые вопросы требуют осторожности. Избегайте импульсивных трат.",
            "Творческая энергия на пике! Идеальное время для воплощения идей в жизнь.",
            "Сегодня важно найти баланс между работой и отдыхом.",
            "Коммуникация с близкими принесет понимание и гармонию.",
            "Неожиданная возможность может изменить ваши планы к лучшему.",
            "День благоприятен для обучения и получения новых знаний.",
            "Ваше терпение будет вознаграждено. Не торопите события.",
            "Старые связи могут возобновиться и принести радость."
        ]
        
        predictions = {
            "любовь": ["💕 Романтические возможности", "💖 Гармония в отношениях", "💘 Новые знакомства", "💝 Примирение"],
            "карьера": ["🚀 Профессиональный рост", "💼 Новые проекты", "📈 Повышение доходов", "🎯 Достижение целей"],
            "здоровье": ["💪 Прилив энергии", "🧘 Внутренняя гармония", "🏃 Активность принесет пользу", "😌 Покой и восстановление"],
            "финансы": ["💰 Улучшение положения", "💳 Разумные траты", "📊 Выгодные инвестиции", "🎁 Неожиданная прибыль"]
        }
        
        horoscope_text = random.choice(horoscopes)
        
        embed = discord.Embed(
            title=f"{sign_data['emoji']} Гороскоп для {sign.title()}",
            description=f"**{horoscope_text}**",
            color=Config.COLORS['info']
        )
        
        embed.add_field(
            name="📅 Период",
            value=sign_data['dates'],
            inline=True
        )
        
        for sphere, options in predictions.items():
            prediction = random.choice(options)
            embed.add_field(
                name=f"{sphere.title()}:",
                value=prediction,
                inline=True
            )
        
        embed.add_field(
            name="🍀 Счастливое число",
            value=str(random.randint(1, 99)),
            inline=True
        )
        
        embed.add_field(
            name="🎨 Счастливый цвет",
            value=random.choice(["Красный", "Синий", "Зеленый", "Золотой", "Фиолетовый", "Серебряный"]),
            inline=True
        )
        
        embed.set_footer(text=f"Гороскоп на {datetime.now().strftime('%d.%m.%Y')} ✨")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="magic_quote", description="✨ Магические цитаты дня")
    async def magic_quote(self, interaction: discord.Interaction):
        """Отправляет магическую цитату дня"""
        magic_quotes = [
            "Магия начинается с веры в невозможное. ✨",
            "Каждый день - это новое заклинание, которое вы создаете своими действиями. 🔮",
            "Самая сильная магия - это магия доброты и понимания. 💫",
            "Ваши мысли имеют силу изменять реальность. Думайте позитивно! 🌟",
            "Магия не в том, чтобы изменить мир, а в том, чтобы изменить себя. 🦋",
            "Верьте в чудеса, и они обязательно произойдут. 🌈",
            "Самое волшебное место на земле - это место, где вы чувствуете себя дома. 🏠",
            "Магия любви сильнее любого заклинания. 💖",
            "Ваша уникальность - это ваша суперсила. 🦸‍♀️",
            "Мечты - это семена будущих реальностей. 🌱",
            "Каждый закат - это обещание нового рассвета. 🌅",
            "Магия случается, когда вы выходите из зоны комфорта. 🚀"
        ]
        
        quote = random.choice(magic_quotes)
        
        # Случайный магический элемент
        magic_elements = [
            "🔮 Кристальные видения",
            "⭐ Звездная пыль",
            "🌙 Лунный свет",
            "🔥 Священное пламя",
            "💎 Драгоценные камни",
            "🌿 Травяная магия",
            "❄️ Кристальный лед",
            "🌺 Цветочная эссенция"
        ]
        
        element = random.choice(magic_elements)
        
        embed = discord.Embed(
            title="✨ Магическая цитата дня",
            description=f"*{quote}*",
            color=0x9932cc  # Фиолетовый цвет для магии
        )
        
        embed.add_field(
            name="🔮 Источник силы",
            value=element,
            inline=True
        )
        
        embed.add_field(
            name="🎯 Магический совет",
            value="Носите с собой позитивную энергию!",
            inline=True
        )
        
        embed.set_footer(text="✨ Пусть магия будет с вами! ✨")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="dream_meaning", description="😴 Толкование снов")
    @app_commands.describe(dream="Опишите ваш сон")
    async def dream_meaning(self, interaction: discord.Interaction, dream: str):
        """Толкует значение сна"""
        # Ключевые слова и их толкования
        dream_meanings = {
            "вода": "Символ эмоций и подсознания. Чистая вода - к удаче, мутная - к проблемам.",
            "огонь": "Страсть, энергия, трансформация. Может означать как разрушение, так и обновление.",
            "лететь": "Свобода, освобождение от ограничений, стремление к высоким целям.",
            "животные": "Инстинкты, природная мудрость, скрытые аспекты личности.",
            "дом": "Ваше внутреннее 'я', семья, безопасность, корни.",
            "дорога": "Жизненный путь, выбор, поиск направления.",
            "смерть": "Конец одного этапа и начало нового, трансформация.",
            "деньги": "Самооценка, власть, материальная безопасность.",
            "дети": "Новые начинания, невинность, творческий потенциал.",
            "зеркало": "Самопознание, рефлексия, внутренний мир."
        }
        
        # Ищем ключевые слова в описании сна
        found_meanings = []
        dream_lower = dream.lower()
        
        for keyword, meaning in dream_meanings.items():
            if keyword in dream_lower:
                found_meanings.append((keyword, meaning))
        
        embed = discord.Embed(
            title="😴 Толкование вашего сна",
            color=Config.COLORS['info']
        )
        
        embed.add_field(
            name="💭 Ваш сон",
            value=dream[:200] + ("..." if len(dream) > 200 else ""),
            inline=False
        )
        
        if found_meanings:
            interpretations = []
            for keyword, meaning in found_meanings:
                interpretations.append(f"**{keyword.title()}:** {meaning}")
            
            embed.add_field(
                name="🔍 Найденные символы",
                value="\n\n".join(interpretations),
                inline=False
            )
        else:
            # Общее толкование если не найдены ключевые слова
            general_meanings = [
                "Ваш сон отражает внутренние переживания и подсознательные мысли.",
                "Сон может символизировать ваши текущие жизненные ситуации и эмоции.",
                "Образы из сна связаны с вашими страхами, желаниями или воспоминаниями.",
                "Сон указывает на необходимость принятия важного решения.",
                "Ваше подсознание обрабатывает информацию и ищет ответы на важные вопросы."
            ]
            
            embed.add_field(
                name="🔮 Общее толкование",
                value=random.choice(general_meanings),
                inline=False
            )
        
        # Добавляем рекомендации
        recommendations = [
            "Ведите дневник снов для лучшего понимания подсознания",
            "Обратите внимание на эмоции, которые вызвал сон",
            "Сон может быть подсказкой для решения текущих проблем",
            "Попробуйте медитацию перед сном для более ясных сновидений"
        ]
        
        embed.add_field(
            name="💡 Рекомендация",
            value=random.choice(recommendations),
            inline=False
        )
        
        embed.set_footer(text="😴 Сны - это мост между сознанием и подсознанием")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="poll", description="📊 Создать интерактивный опрос")
    @app_commands.describe(question="Вопрос для опроса", options="Варианты ответов (разделите |)")
    async def poll(self, interaction: discord.Interaction, question: str, options: str):
        """Создает интерактивный опрос с реакциями"""
        poll_options = [opt.strip() for opt in options.split("|")]
        
        if len(poll_options) < 2:
            await interaction.response.send_message("❌ Нужно минимум 2 варианта ответа, разделенных символом |", ephemeral=True)
            return
        
        if len(poll_options) > 10:
            await interaction.response.send_message("❌ Максимум 10 вариантов ответа!", ephemeral=True)
            return
        
        # Эмодзи для вариантов
        poll_emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
        
        embed = discord.Embed(
            title="📊 Опрос",
            description=f"**{question}**",
            color=Config.COLORS['info']
        )
        
        poll_text = []
        for i, option in enumerate(poll_options):
            poll_text.append(f"{poll_emojis[i]} {option}")
        
        embed.add_field(
            name="Варианты ответов:",
            value="\n".join(poll_text),
            inline=False
        )
        
        embed.add_field(
            name="📋 Как голосовать:",
            value="Нажмите на соответствующую реакцию ниже!",
            inline=False
        )
        
        embed.set_footer(text=f"Опрос создан: {interaction.user.display_name}")
        embed.timestamp = datetime.now()
        
        await interaction.response.send_message(embed=embed)
        message = await interaction.original_response()
        
        # Добавляем реакции
        for i in range(len(poll_options)):
            await message.add_reaction(poll_emojis[i])
        
        # Сохраняем опрос
        self.active_polls[message.id] = {
            'question': question,
            'options': poll_options,
            'creator': interaction.user.id,
            'created_at': datetime.now()
        }
    
    @app_commands.command(name="remind", description="⏰ Установить напоминание")
    @app_commands.describe(minutes="Через сколько минут напомнить", message="Текст напоминания")
    async def remind(self, interaction: discord.Interaction, minutes: int, message: str):
        """Устанавливает напоминание на определенное время"""
        if minutes < 1 or minutes > 10080:  # 7 дней максимум
            await interaction.response.send_message("❌ Время напоминания должно быть от 1 минуты до 7 дней (10080 минут)!", ephemeral=True)
            return
        
        remind_time = datetime.now() + timedelta(minutes=minutes)
        
        embed = discord.Embed(
            title="⏰ Напоминание установлено",
            description=f"Я напомню вам через **{minutes} минут**!",
            color=Config.COLORS['success']
        )
        
        embed.add_field(
            name="📝 Сообщение",
            value=message,
            inline=False
        )
        
        embed.add_field(
            name="🕐 Время напоминания",
            value=f"<t:{int(remind_time.timestamp())}:F>",
            inline=False
        )
        
        await interaction.response.send_message(embed=embed)
        
        # Сохраняем напоминание
        reminder_id = f"{interaction.user.id}_{int(remind_time.timestamp())}"
        self.reminders[reminder_id] = {
            'user_id': interaction.user.id,
            'channel_id': interaction.channel.id,
            'message': message,
            'time': remind_time
        }
        
        # Запускаем задачу напоминания
        self.bot.loop.create_task(self.send_reminder(reminder_id))
    
    async def send_reminder(self, reminder_id):
        """Отправляет напоминание через заданное время"""
        if reminder_id not in self.reminders:
            return
        
        reminder = self.reminders[reminder_id]
        
        # Ждем до времени напоминания
        wait_time = (reminder['time'] - datetime.now()).total_seconds()
        if wait_time > 0:
            await asyncio.sleep(wait_time)
        
        # Проверяем, что напоминание еще актуально
        if reminder_id not in self.reminders:
            return
        
        # Отправляем напоминание
        try:
            channel = self.bot.get_channel(reminder['channel_id'])
            user = self.bot.get_user(reminder['user_id'])
            
            if channel and user:
                embed = discord.Embed(
                    title="⏰ Напоминание!",
                    description=f"{user.mention}, вы просили напомнить:",
                    color=Config.COLORS['warning']
                )
                
                embed.add_field(
                    name="📝 Ваше сообщение",
                    value=reminder['message'],
                    inline=False
                )
                
                embed.set_footer(text="Напоминание выполнено! ✅")
                
                await channel.send(embed=embed)
        
        except Exception:
            pass  # Игнорируем ошибки отправки напоминаний
        
        finally:
            # Удаляем напоминание
            if reminder_id in self.reminders:
                del self.reminders[reminder_id]
    
    @app_commands.command(name="would_you_rather", description="🤔 Игра 'Что бы вы выбрали?'")
    async def would_you_rather(self, interaction: discord.Interaction):
        """Предлагает выбор между двумя интересными вариантами"""
        scenarios = [
            ("Уметь читать мысли", "Быть невидимым"),
            ("Путешествовать в прошлое", "Видеть будущее"),
            ("Жить без интернета", "Жить без музыки"),
            ("Быть очень умным", "Быть очень красивым"),
            ("Иметь неограниченные деньги", "Иметь неограниченное время"),
            ("Летать как птица", "Дышать под водой"),
            ("Знать все языки мира", "Уметь играть на любом инструменте"),
            ("Жить в большом городе", "Жить на необитаемом острове"),
            ("Быть знаменитым", "Быть влиятельным"),
            ("Иметь фотографическую память", "Уметь забывать плохие воспоминания"),
            ("Всегда говорить правду", "Всегда знать, когда лгут"),
            ("Быть лучшим в чем-то одном", "Быть хорошим во всем"),
            ("Жить 200 лет в прошлом", "Жить 200 лет в будущем"),
            ("Уметь разговаривать с животными", "Понимать все языки программирования"),
            ("Никогда не спать", "Никогда не есть")
        ]
        
        option1, option2 = random.choice(scenarios)
        
        embed = discord.Embed(
            title="🤔 Что бы вы выбрали?",
            description="Выберите один из двух вариантов!",
            color=Config.COLORS['entertainment']
        )
        
        embed.add_field(
            name="🅰️ Вариант A",
            value=f"**{option1}**",
            inline=True
        )
        
        embed.add_field(
            name="🅱️ Вариант B", 
            value=f"**{option2}**",
            inline=True
        )
        
        embed.add_field(
            name="📊 Как голосовать:",
            value="Нажмите 🅰️ или 🅱️ ниже!",
            inline=False
        )
        
        embed.set_footer(text="🤔 Сложный выбор, не правда ли?")
        
        await interaction.response.send_message(embed=embed)
        message = await interaction.original_response()
        
        await message.add_reaction("🅰️")
        await message.add_reaction("🅱️")
    
    @app_commands.command(name="weather_mood", description="🌤️ Настроение по погоде")
    @app_commands.describe(weather="Текущая погода")
    async def weather_mood(self, interaction: discord.Interaction, weather: str):
        """Предлагает настроение и активности в зависимости от погоды"""
        weather_moods = {
            "солнечно": {
                "mood": "☀️ Радостное и энергичное",
                "activities": ["Прогулка в парке", "Пикник на природе", "Фотосессия", "Спорт на улице"],
                "color": 0xFFD700,
                "advice": "Отличный день для активности на свежем воздухе!"
            },
            "дождь": {
                "mood": "🌧️ Уютное и спокойное",
                "activities": ["Чтение книги", "Просмотр фильма", "Чай с печеньем", "Творчество дома"],
                "color": 0x4682B4,
                "advice": "Прекрасное время для домашнего уюта и саморазвития."
            },
            "снег": {
                "mood": "❄️ Сказочное и мечтательное",
                "activities": ["Лепка снеговика", "Катание на санках", "Горячий шоколад", "Зимняя фотография"],
                "color": 0xF0F8FF,
                "advice": "Насладитесь зимней магией и теплом домашнего очага!"
            },
            "облачно": {
                "mood": "☁️ Задумчивое и творческое",
                "activities": ["Рисование", "Письмо", "Медитация", "Планирование будущего"],
                "color": 0x708090,
                "advice": "Идеальная погода для размышлений и творчества."
            },
            "ветрено": {
                "mood": "💨 Динамичное и свободное",
                "activities": ["Запуск воздушного змея", "Велосипедная прогулка", "Танцы", "Новые начинания"],
                "color": 0x87CEEB,
                "advice": "Позвольте ветру перемен унести старые заботы!"
            }
        }
        
        weather_lower = weather.lower()
        
        # Ищем подходящее настроение
        mood_data = None
        for key, data in weather_moods.items():
            if key in weather_lower:
                mood_data = data
                break
        
        if not mood_data:
            # Универсальное настроение
            mood_data = {
                "mood": "🌈 Адаптивное и позитивное",
                "activities": ["Что-то новое", "Общение с друзьями", "Изучение интересного", "Саморазвитие"],
                "color": Config.COLORS['info'],
                "advice": "Любая погода хороша, если у вас правильное настроение!"
            }
        
        embed = discord.Embed(
            title="🌤️ Настроение по погоде",
            description=f"**Погода:** {weather}",
            color=mood_data["color"]
        )
        
        embed.add_field(
            name="😊 Рекомендуемое настроение",
            value=mood_data["mood"],
            inline=False
        )
        
        activities_text = "\n".join([f"• {activity}" for activity in mood_data["activities"]])
        embed.add_field(
            name="🎯 Подходящие активности",
            value=activities_text,
            inline=False
        )
        
        embed.add_field(
            name="💡 Совет",
            value=mood_data["advice"],
            inline=False
        )
        
        embed.set_footer(text="🌈 Каждая погода имеет свою красоту!")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="tech_fact", description="💻 Технологический факт")
    async def tech_fact(self, interaction: discord.Interaction):
        """Отправляет интересный технологический факт"""
        tech_facts = [
            "Первый компьютерный вирус был создан в 1971 году и назывался 'Creeper'.",
            "Компания Google изначально называлась 'BackRub'.",
            "Первый смартфон был выпущен IBM в 1994 году и назывался Simon.",
            "Wi-Fi расшифровывается как 'Wireless Fidelity'.",
            "Более 90% валюты мира существует только в цифровом виде.",
            "Первая веб-камера была создана для наблюдения за кофеваркой в Кембридже.",
            "Email существует дольше, чем World Wide Web.",
            "Python назван в честь британского комедийного шоу 'Летающий цирк Монти Пайтона'.",
            "Слово 'robot' происходит от чешского слова 'robota', что означает 'принудительный труд'.",
            "В 1 ГБ данных содержится примерно 230,000 страниц обычного текста.",
            "Первый жесткий диск весил больше тонны и стоил $10,000 за каждый мегабайт.",
            "Bluetooth назван в честь датского короля Харальда Синезубого (Bluetooth).",
            "Первое доменное имя symbolics.com было зарегистрировано 15 марта 1985 года.",
            "Компьютерная мышь была изобретена в 1964 году Дугласом Энгельбартом.",
            "Первый баннерная реклама в интернете появилась в 1994 году и имела CTR 44%."
        ]
        
        fact = random.choice(tech_facts)
        
        embed = discord.Embed(
            title="💻 Технологический факт",
            description=fact,
            color=Config.COLORS['utility']
        )
        
        embed.add_field(
            name="🤓 Знали ли вы?",
            value="Технологии развиваются со скоростью света!",
            inline=False
        )
        
        embed.set_footer(text="💡 Знания делают нас сильнее!")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="random_fact", description="🎲 Случайный интересный факт")
    async def random_fact(self, interaction: discord.Interaction):
        """Отправляет случайный интересный факт"""
        random_facts = [
            "Осьминоги имеют три сердца и голубую кровь.",
            "Мед никогда не портится. Археологи находили горшки с медом возрастом 3000 лет.",
            "Банан - это ягода, а клубника - нет.",
            "Акулы существуют дольше, чем деревья.",
            "В космосе астронавты не могут плакать из-за отсутствия гравитации.",
            "Дельфины дают имена друг другу.",
            "Человеческий мозг на 75% состоит из воды.",
            "Отпечатки пальцев коал очень похожи на человеческие.",
            "Сердце кита размером с автомобиль Volkswagen Beetle.",
            "Антарктида - единственный континент без муравьев.",
            "Слоны - одни из немногих животных, которые узнают себя в зеркале.",
            "Горячая вода замерзает быстрее холодной (эффект Мпембы).",
            "У жирафов такой же размер языка, как и их высота - около 50 см.",
            "Морковь изначально была фиолетовой, а не оранжевой.",
            "Пингвины могут прыгать на высоту до 3 метров."
        ]
        
        fact = random.choice(random_facts)
        
        embed = discord.Embed(
            title="🎲 Случайный факт",
            description=fact,
            color=Config.COLORS['entertainment']
        )
        
        embed.add_field(
            name="🌟 Удивительно!",
            value="Мир полон невероятных фактов!",
            inline=False
        )
        
        embed.set_footer(text="🧠 Каждый день можно узнать что-то новое!")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="calculate", description="🧮 Математический калькулятор")
    @app_commands.describe(expression="Математическое выражение для вычисления")
    async def calculate(self, interaction: discord.Interaction, expression: str):
        """Вычисляет математическое выражение"""
        # Разрешенные символы для безопасности
        allowed_chars = "0123456789+-*/()., "
        
        # Проверяем безопасность выражения
        if not all(c in allowed_chars for c in expression):
            await interaction.response.send_message("❌ Можно использовать только числа и операции: +, -, *, /, ( )", ephemeral=True)
            return
        
        # Заменяем запятые на точки для десятичных дробей
        expression = expression.replace(",", ".")
        
        try:
            # Вычисляем выражение
            result = eval(expression)
            
            # Форматируем результат
            if isinstance(result, float):
                if result.is_integer():
                    result = int(result)
                else:
                    result = round(result, 10)  # Ограничиваем количество знаков после запятой
            
            embed = discord.Embed(
                title="🧮 Калькулятор",
                color=Config.COLORS['utility']
            )
            
            embed.add_field(
                name="📝 Выражение",
                value=f"`{expression}`",
                inline=False
            )
            
            embed.add_field(
                name="📊 Результат",
                value=f"**{result}**",
                inline=False
            )
            
            # Добавляем дополнительную информацию для некоторых результатов
            if isinstance(result, (int, float)):
                if result > 1000000:
                    embed.add_field(
                        name="🔢 В научной нотации",
                        value=f"{result:.2e}",
                        inline=True
                    )
                
                if isinstance(result, int) and result > 1:
                    # Проверяем, является ли число простым (для небольших чисел)
                    if result < 1000:
                        is_prime = result > 1 and all(result % i != 0 for i in range(2, int(result**0.5) + 1))
                        embed.add_field(
                            name="🔍 Особенность",
                            value="Простое число!" if is_prime else "Составное число",
                            inline=True
                        )
            
            embed.set_footer(text="🧮 Математика - королева наук!")
            
        except ZeroDivisionError:
            embed = discord.Embed(
                title="❌ Ошибка вычисления",
                description="Деление на ноль невозможно!",
                color=Config.COLORS['error']
            )
            
        except (ValueError, SyntaxError):
            embed = discord.Embed(
                title="❌ Ошибка вычисления",
                description="Некорректное математическое выражение!",
                color=Config.COLORS['error']
            )
            
        except Exception as e:
            embed = discord.Embed(
                title="❌ Ошибка вычисления",
                description="Произошла ошибка при вычислении.",
                color=Config.COLORS['error']
            )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="word_association", description="🔗 Ассоциации к слову")
    @app_commands.describe(word="Слово для поиска ассоциаций")
    async def word_association(self, interaction: discord.Interaction, word: str):
        """Генерирует ассоциации к заданному слову"""
        word_associations = {
            "солнце": ["тепло", "свет", "лето", "радость", "энергия", "витамин D"],
            "дождь": ["капли", "зонт", "лужи", "свежесть", "природа", "уют"],
            "музыка": ["мелодия", "ритм", "эмоции", "концерт", "наушники", "душа"],
            "книга": ["знания", "фантазия", "страницы", "автор", "библиотека", "мудрость"],
            "кофе": ["бодрость", "аромат", "утро", "кафе", "зерна", "тепло"],
            "море": ["волны", "соль", "отпуск", "корабль", "глубина", "бескрайность"],
            "дом": ["семья", "уют", "тепло", "крыша", "безопасность", "очаг"],
            "друг": ["доверие", "поддержка", "веселье", "понимание", "верность", "общение"],
            "любовь": ["сердце", "счастье", "забота", "романтика", "чувства", "гармония"],
            "мечта": ["цель", "будущее", "желание", "фантазия", "надежда", "стремление"]
        }
        
        word_lower = word.lower()
        
        # Ищем прямые ассоциации
        if word_lower in word_associations:
            associations = word_associations[word_lower]
        else:
            # Генерируем общие ассоциации
            general_associations = [
                "новое", "интересное", "важное", "красивое", "полезное", "особенное",
                "значимое", "ценное", "удивительное", "вдохновляющее", "творческое",
                "позитивное", "энергичное", "спокойное", "гармоничное", "магическое"
            ]
            associations = random.sample(general_associations, 6)
        
        embed = discord.Embed(
            title="🔗 Ассоциации к слову",
            description=f"**Слово:** {word.title()}",
            color=Config.COLORS['entertainment']
        )
        
        # Разделяем ассоциации на группы
        embed.add_field(
            name="💭 Первые ассоциации",
            value=" • ".join(associations[:3]),
            inline=False
        )
        
        embed.add_field(
            name="🌟 Дополнительные ассоциации",
            value=" • ".join(associations[3:6]),
            inline=False
        )
        
        # Добавляем случайную категорию
        categories = [
            "🎨 Творческая ассоциация",
            "💫 Эмоциональная связь", 
            "🌈 Позитивный аспект",
            "🔮 Глубокий смысл"
        ]
        
        category = random.choice(categories)
        deep_associations = [
            "символ надежды", "источник вдохновения", "путь к успеху",
            "ключ к пониманию", "мост между мирами", "отражение души",
            "энергия изменений", "основа гармонии", "искра творчества"
        ]
        
        embed.add_field(
            name=category,
            value=random.choice(deep_associations),
            inline=False
        )
        
        embed.set_footer(text="🧠 Ассоциации помогают нам лучше понимать мир!")
        
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(ExtendedCommands(bot))
