import discord
from discord.ext import commands
from discord import app_commands
import random
import asyncio
from config import Config

# Словарь для хранения активных игр
active_games = {}

class Games(commands.Cog):
    """Игровые команды бота"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @app_commands.command(name="guess_number", description="🎯 Угадай загаданное число")
    @app_commands.describe(maximum="Максимальное число для угадывания (по умолчанию 100)")
    async def guess_number(self, interaction: discord.Interaction, maximum: int = 100):
        """Игра в угадывание числа"""
        if maximum < 2 or maximum > 10000:
            await interaction.response.send_message("❌ Максимальное число должно быть от 2 до 10,000!", ephemeral=True)
            return
        
        channel_id = interaction.channel.id
        if channel_id in active_games:
            await interaction.response.send_message("❌ В этом канале уже идёт игра! Используйте `/stop_game` чтобы остановить.", ephemeral=True)
            return
        
        secret_number = random.randint(1, maximum)
        attempts = 0
        max_attempts = min(10, max(3, maximum // 10))
        
        active_games[channel_id] = {
            'type': 'guess_number',
            'secret': secret_number,
            'attempts': attempts,
            'max_attempts': max_attempts,
            'player': interaction.user.id
        }
        
        embed = discord.Embed(
            title="🎯 Угадай число!",
            description=f"Я загадал число от **1** до **{maximum}**!\n"
                       f"У вас есть **{max_attempts}** попыток.\n\n"
                       f"Просто напишите число в чат!",
            color=Config.COLORS['entertainment']
        )
        embed.set_footer(text=f"Игрок: {interaction.user.display_name}")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="rps", description="✂️ Камень, ножницы, бумага")
    @app_commands.describe(choice="Ваш выбор: камень, ножницы или бумага")
    async def rock_paper_scissors(self, interaction: discord.Interaction, choice: str):
        """Игра в камень, ножницы, бумага"""
        choices = {
            'камень': '🗿',
            'ножницы': '✂️', 
            'бумага': '📄',
            'rock': '🗿',
            'scissors': '✂️',
            'paper': '📄'
        }
        
        user_choice = choice.lower()
        if user_choice not in choices:
            await interaction.response.send_message("❌ Выберите: камень, ножницы или бумага!", ephemeral=True)
            return
        
        bot_choice = random.choice(['камень', 'ножницы', 'бумага'])
        
        # Определяем победителя
        win_conditions = {
            'камень': 'ножницы',
            'ножницы': 'бумага', 
            'бумага': 'камень'
        }
        
        # Конвертируем английские варианты
        if user_choice in ['rock', 'scissors', 'paper']:
            translate = {'rock': 'камень', 'scissors': 'ножницы', 'paper': 'бумага'}
            user_choice = translate[user_choice]
        
        if user_choice == bot_choice:
            result = "Ничья!"
            color = Config.COLORS['warning']
        elif win_conditions[user_choice] == bot_choice:
            result = "Вы выиграли! 🎉"
            color = Config.COLORS['success']
        else:
            result = "Вы проиграли! 😢"
            color = Config.COLORS['error']
        
        embed = discord.Embed(
            title="✂️ Камень, ножницы, бумага",
            description=f"**Ваш выбор:** {choices[user_choice]} {user_choice.title()}\n"
                       f"**Мой выбор:** {choices[bot_choice]} {bot_choice.title()}\n\n"
                       f"**Результат:** {result}",
            color=color
        )
        embed.set_footer(text="Хотите сыграть ещё? 🎮")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="trivia", description="🧠 Викторина")
    async def trivia(self, interaction: discord.Interaction):
        """Викторина с вопросами"""
        questions = [
            {
                "question": "Какой язык программирования создал Гвидо ван Россум?",
                "options": ["Java", "Python", "C++", "JavaScript"],
                "correct": 1
            },
            {
                "question": "Что означает HTTP?",
                "options": ["HyperText Transfer Protocol", "High Tech Transfer Protocol", "Home Tool Transfer Protocol", "HyperText Transport Protocol"],
                "correct": 0
            },
            {
                "question": "В каком году был создан Discord?",
                "options": ["2013", "2015", "2017", "2019"],
                "correct": 1
            },
            {
                "question": "Сколько байт в одном килобайте?",
                "options": ["1000", "1024", "512", "2048"],
                "correct": 1
            },
            {
                "question": "Кто основал Microsoft?",
                "options": ["Стив Джобс", "Марк Цукерберг", "Билл Гейтс", "Ларри Пейдж"],
                "correct": 2
            }
        ]
        
        question_data = random.choice(questions)
        
        embed = discord.Embed(
            title="🧠 Вопрос викторины",
            description=question_data["question"],
            color=Config.COLORS['info']
        )
        
        for i, option in enumerate(question_data["options"]):
            embed.add_field(
                name=f"{i+1}️⃣ Вариант {i+1}",
                value=option,
                inline=False
            )
        
        embed.set_footer(text="Ответ появится через 15 секунд! ⏰")
        
        await interaction.response.send_message(embed=embed)
        
        await asyncio.sleep(15)
        
        correct_answer = question_data["options"][question_data["correct"]]
        
        answer_embed = discord.Embed(
            title="✅ Правильный ответ",
            description=f"**{correct_answer}**",
            color=Config.COLORS['success']
        )
        answer_embed.set_footer(text="Знали ответ? 🤓")
        
        await interaction.followup.send(embed=answer_embed)
    
    @app_commands.command(name="word_chain", description="🔗 Игра в цепочку слов")
    async def word_chain(self, interaction: discord.Interaction):
        """Запускает игру в цепочку слов"""
        channel_id = interaction.channel.id
        if channel_id in active_games:
            await interaction.response.send_message("❌ В этом канале уже идёт игра! Используйте `/stop_game` чтобы остановить.", ephemeral=True)
            return
        
        starting_words = ["программа", "компьютер", "дискорд", "бот", "игра", "сервер", "канал", "пользователь", "пизда"]
        start_word = random.choice(starting_words)
        
        active_games[channel_id] = {
            'type': 'word_chain',
            'last_word': start_word,
            'used_words': {start_word},
            'current_player': None,
            'words_count': 1
        }
        
        embed = discord.Embed(
            title="🔗 Игра в цепочку слов",
            description=f"**Правила:**\n"
                       f"• Следующее слово должно начинаться на последнюю букву предыдущего\n"
                       f"• Нельзя повторять уже использованные слова\n"
                       f"• Только существительные в именительном падеже\n\n"
                       f"**Первое слово:** `{start_word}`\n"
                       f"**Следующее слово должно начинаться на букву:** `{start_word[-1].upper()}`",
            color=Config.COLORS['entertainment']
        )
        embed.set_footer(text="Напишите слово в чат! 💬")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="memory_game", description="🧩 Тренировка памяти")
    async def memory_game(self, interaction: discord.Interaction):
        """Игра на тренировку памяти"""
        channel_id = interaction.channel.id
        if channel_id in active_games:
            await interaction.response.send_message("❌ В этом канале уже идёт игра! Используйте `/stop_game` чтобы остановить.", ephemeral=True)
            return
        
        # Генерируем последовательность
        sequence = [random.randint(1, 9) for _ in range(5)]
        
        active_games[channel_id] = {
            'type': 'memory_game',
            'sequence': sequence,
            'current_position': 0,
            'player': interaction.user.id
        }
        
        sequence_str = " ".join(map(str, sequence))
        
        embed = discord.Embed(
            title="🧩 Тренировка памяти",
            description=f"**Запомните эту последовательность:**\n\n"
                       f"# {sequence_str}\n\n"
                       f"Последовательность исчезнет через 10 секунд!\n"
                       f"Затем вводите числа по одному в чат.",
            color=Config.COLORS['info']
        )
        embed.set_footer(text=f"Игрок: {interaction.user.display_name}")
        
        message = await interaction.response.send_message(embed=embed)
        
        await asyncio.sleep(10)
        
        hidden_embed = discord.Embed(
            title="🧩 Тренировка памяти",
            description="**Теперь введите числа по порядку!**\n\n"
                       f"Введите **число №1** из запомненной последовательности:",
            color=Config.COLORS['warning']
        )
        hidden_embed.set_footer(text=f"Игрок: {interaction.user.display_name}")
        
        await interaction.edit_original_response(embed=hidden_embed)
    
    @app_commands.command(name="coin_battle", description="💰 Битва монеток")
    @app_commands.describe(opponent="Противник для битвы монеток")
    async def coin_battle(self, interaction: discord.Interaction, opponent: discord.Member):
        """Битва монеток между двумя игроками"""
        if opponent.bot:
            await interaction.response.send_message("❌ Нельзя играть против ботов!", ephemeral=True)
            return
        
        if opponent.id == interaction.user.id:
            await interaction.response.send_message("❌ Нельзя играть против самого себя!", ephemeral=True)
            return
        
        user1_flip = random.choice(['Орёл', 'Решка'])
        user2_flip = random.choice(['Орёл', 'Решка'])
        
        if user1_flip == user2_flip:
            result = "Ничья! Обе монетки показали одинаковый результат!"
            color = Config.COLORS['warning']
        else:
            winner = interaction.user if user1_flip == 'Орёл' else opponent
            result = f"Победитель: {winner.mention}!"
            color = Config.COLORS['success']
        
        embed = discord.Embed(
            title="💰 Битва монеток",
            description=f"**{interaction.user.display_name}:** 🪙 {user1_flip}\n"
                       f"**{opponent.display_name}:** 🪙 {user2_flip}\n\n"
                       f"**{result}**",
            color=color
        )
        embed.set_footer(text="Удача решает всё! 🍀")
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="stop_game", description="⏹️ Остановить активную игру")
    async def stop_game(self, interaction: discord.Interaction):
        """Остановить активную игру в канале"""
        channel_id = interaction.channel.id
        if channel_id not in active_games:
            await interaction.response.send_message("❌ В этом канале нет активных игр!", ephemeral=True)
            return
        
        game_type = active_games[channel_id]['type']
        del active_games[channel_id]
        
        embed = discord.Embed(
            title="⏹️ Игра остановлена",
            description=f"Игра **{game_type}** была остановлена.",
            color=Config.COLORS['info']
        )
        
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="games_help", description="❓ Помощь по игровым командам")
    async def games_help(self, interaction: discord.Interaction):
        """Показывает помощь по игровым командам"""
        embed = discord.Embed(
            title="🎯 Игровые команды",
            description="Все доступные игры и развлечения!",
            color=Config.COLORS['entertainment']
        )
        
        games_list = [
            "`/guess_number [макс]` - Угадай загаданное число",
            "`/rps [выбор]` - Камень, ножницы, бумага",
            "`/trivia` - Викторина с вопросами",
            "`/word_chain` - Игра в цепочку слов",
            "`/memory_game` - Тренировка памяти", 
            "`/coin_battle [@противник]` - Битва монеток",
            "`/stop_game` - Остановить активную игру"
        ]
        
        embed.add_field(
            name="🎮 Доступные игры:",
            value="\n".join(games_list),
            inline=False
        )
        
        embed.add_field(
            name="📋 Правила:",
            value="• В каждом канале может быть только одна активная игра\n"
                  "• Некоторые игры требуют взаимодействия в чате\n"
                  "• Используйте `/stop_game` для остановки игры",
            inline=False
        )
        
        embed.set_footer(text="Играйте и веселитесь! 🎉")
        
        await interaction.response.send_message(embed=embed)
    
    @commands.Cog.listener()
    async def on_message(self, message):
        """Обработка сообщений для активных игр"""
        if message.author.bot:
            return
        
        channel_id = message.channel.id
        if channel_id not in active_games:
            return
        
        game = active_games[channel_id]
        
        if game['type'] == 'guess_number':
            await self.handle_guess_number(message, game)
        elif game['type'] == 'word_chain':
            await self.handle_word_chain(message, game)
        elif game['type'] == 'memory_game':
            await self.handle_memory_game(message, game)
    
    async def handle_guess_number(self, message, game):
        """Обработка игры угадывания числа"""
        if message.author.id != game['player']:
            return
        
        try:
            guess = int(message.content)
        except ValueError:
            return
        
        game['attempts'] += 1
        secret = game['secret']
        
        if guess == secret:
            embed = discord.Embed(
                title="🎉 Поздравляю!",
                description=f"Вы угадали число **{secret}** за **{game['attempts']}** попыток!",
                color=Config.COLORS['success']
            )
            del active_games[message.channel.id]
        elif game['attempts'] >= game['max_attempts']:
            embed = discord.Embed(
                title="😞 Попытки закончились",
                description=f"Загаданное число было: **{secret}**\nПопробуйте ещё раз!",
                color=Config.COLORS['error']
            )
            del active_games[message.channel.id]
        else:
            remaining = game['max_attempts'] - game['attempts']
            hint = "больше" if guess < secret else "меньше"
            
            embed = discord.Embed(
                title="🎯 Попробуйте ещё раз",
                description=f"Загаданное число **{hint}** чем **{guess}**\n"
                           f"Осталось попыток: **{remaining}**",
                color=Config.COLORS['warning']
            )
        
        await message.channel.send(embed=embed)
    
    async def handle_word_chain(self, message, game):
        """Обработка игры в цепочку слов"""
        word = message.content.lower().strip()
        
        if len(word.split()) != 1:
            return
        
        last_word = game['last_word']
        
        # Проверяем правильность слова
        if word[0] != last_word[-1]:
            embed = discord.Embed(
                title="❌ Неверно!",
                description=f"Слово должно начинаться на букву **{last_word[-1].upper()}**",
                color=Config.COLORS['error']
            )
            await message.channel.send(embed=embed)
            return
        
        if word in game['used_words']:
            embed = discord.Embed(
                title="❌ Слово уже использовалось!",
                description="Придумайте другое слово.",
                color=Config.COLORS['error']
            )
            await message.channel.send(embed=embed)
            return
        
        # Добавляем слово
        game['last_word'] = word
        game['used_words'].add(word)
        game['words_count'] += 1
        
        embed = discord.Embed(
            title="✅ Отлично!",
            description=f"**Слов в цепочке:** {game['words_count']}\n"
                       f"**Последнее слово:** `{word}`\n"
                       f"**Следующее слово на:** `{word[-1].upper()}`",
            color=Config.COLORS['success']
        )
        
        await message.channel.send(embed=embed)
    
    async def handle_memory_game(self, message, game):
        """Обработка игры на память"""
        if message.author.id != game['player']:
            return
        
        try:
            number = int(message.content)
        except ValueError:
            return
        
        expected = game['sequence'][game['current_position']]
        
        if number == expected:
            game['current_position'] += 1
            
            if game['current_position'] >= len(game['sequence']):
                embed = discord.Embed(
                    title="🎉 Отличная память!",
                    description="Вы правильно воспроизвели всю последовательность!",
                    color=Config.COLORS['success']
                )
                del active_games[message.channel.id]
            else:
                embed = discord.Embed(
                    title="✅ Правильно!",
                    description=f"Теперь введите **число №{game['current_position'] + 1}**:",
                    color=Config.COLORS['success']
                )
        else:
            sequence_str = " ".join(map(str, game['sequence']))
            embed = discord.Embed(
                title="❌ Неправильно!",
                description=f"Правильная последовательность была:\n**{sequence_str}**",
                color=Config.COLORS['error']
            )
            del active_games[message.channel.id]
        
        await message.channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Games(bot))
