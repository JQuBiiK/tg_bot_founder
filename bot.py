import asyncio
import logging
import aiosqlite
import json
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

# Включаем логирование
logging.basicConfig(level=logging.INFO)

# Замените "YOUR_BOT_TOKEN" на токен, который вы получили от BotFather
API_TOKEN = '7929694971:AAFJkUfbBrQ0gbvVKhSYlb6Ew2Amwz1Uqdo'

# Загружаем вопросы из JSON-файла
with open('questions.json', 'r', encoding='utf-8') as file:
    quiz_data = json.load(file)

# Объект бота
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Функция для создания таблицы, если она еще не существует
async def create_table():
    async with aiosqlite.connect('quiz_bot.db') as db:
        await db.execute('''CREATE TABLE IF NOT EXISTS quiz_state (
                                user_id INTEGER PRIMARY KEY,
                                question_index INTEGER,
                                correct_answers INTEGER
                            )''')
        await db.execute('''CREATE TABLE IF NOT EXISTS user_answers (
                                user_id INTEGER,
                                question_index INTEGER,
                                user_answer TEXT,
                                correct_answer TEXT,
                                is_correct INTEGER
                            )''')
        await db.commit()

# Хэндлер на команду /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Привет! Я бот для проведения квиза по Python. Введите /quiz, чтобы начать.")

# Хэндлер на команду /quiz
@dp.message(Command("quiz"))
async def cmd_quiz(message: types.Message):
    user_id = message.from_user.id
    async with aiosqlite.connect('quiz_bot.db') as db:
        # Удаляем старые записи для нового квиза
        await db.execute('DELETE FROM quiz_state WHERE user_id = ?', (user_id,))
        await db.execute('DELETE FROM user_answers WHERE user_id = ?', (user_id,))
        # Создаем новую запись для квиза
        await db.execute('INSERT INTO quiz_state (user_id, question_index, correct_answers) VALUES (?, ?, ?)', (user_id, 0, 0))
        await db.commit()
    await start_quiz(user_id, message)

# Функция для начала или продолжения квиза
async def start_quiz(user_id, message):
    async with aiosqlite.connect('quiz_bot.db') as db:
        async with db.execute('SELECT question_index, correct_answers FROM quiz_state WHERE user_id = ?', (user_id,)) as cursor:
            row = await cursor.fetchone()
            question_index, correct_answers = row

        if question_index >= len(quiz_data):
            await send_final_results(user_id, message)
            return

        question_data = quiz_data[question_index]
        question_text = question_data['question']
        options = question_data['options']

        keyboard = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text=option)] for option in options],
            resize_keyboard=True
        )

        await message.answer(question_text, reply_markup=keyboard)

# Функция для обработки ответов пользователя
@dp.message()
async def handle_answer(message: types.Message):
    user_id = message.from_user.id
    user_answer = message.text

    async with aiosqlite.connect('quiz_bot.db') as db:
        async with db.execute('SELECT question_index, correct_answers FROM quiz_state WHERE user_id = ?', (user_id,)) as cursor:
            row = await cursor.fetchone()
            if row is None:
                await message.answer("Введите /quiz, чтобы начать квиз.")
                return
            question_index, correct_answers = row

        question_data = quiz_data[question_index]
        correct_option = question_data['correct_option']
        options = question_data['options']
        correct_answer = options[correct_option]

        # Проверяем, правильный ли ответ
        is_correct = int(user_answer == correct_answer)
        if is_correct:
            correct_answers += 1

        # Сохраняем ответ пользователя
        await db.execute('INSERT INTO user_answers (user_id, question_index, user_answer, correct_answer, is_correct) VALUES (?, ?, ?, ?, ?)',
                         (user_id, question_index, user_answer, correct_answer, is_correct))
        await db.execute('UPDATE quiz_state SET question_index = ?, correct_answers = ? WHERE user_id = ?', 
                         (question_index + 1, correct_answers, user_id))
        await db.commit()

        # Проверяем, есть ли еще вопросы
        if question_index + 1 >= len(quiz_data):
            await send_final_results(user_id, message)
        else:
            await start_quiz(user_id, message)

# Функция для отправки итоговых результатов
async def send_final_results(user_id, message):
    async with aiosqlite.connect('quiz_bot.db') as db:
        async with db.execute('SELECT question_index, user_answer, correct_answer, is_correct FROM user_answers WHERE user_id = ?', (user_id,)) as cursor:
            rows = await cursor.fetchall()

        results_text = "Результаты квиза:\n\n"
        for row in rows:
            question_index, user_answer, correct_answer, is_correct = row
            question_text = quiz_data[question_index]['question']
            correctness = "✅" if is_correct else "❌"
            results_text += f"{question_text}\nВаш ответ: {user_answer} {correctness}\nПравильный ответ: {correct_answer}\n\n"

        await message.answer(results_text, reply_markup=ReplyKeyboardRemove())

# Запуск бота
async def main():
    await create_table()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
