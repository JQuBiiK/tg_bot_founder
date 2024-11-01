import aiosqlite  # Подключаем aiosqlite для работы с базой данных
from aiogram import types
from aiogram.filters.command import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from db import update_quiz_index, get_quiz_index, save_user_answer, update_user_statistics, get_top_users, reset_user_progress
from config import logging
import json

# Загружаем вопросы из JSON-файла
with open('questions.json', 'r', encoding='utf-8') as file:
    quiz_data = json.load(file)

def setup_handlers(dp):
    dp.message(Command("start"))(cmd_start)
    dp.message(Command("quiz"))(cmd_quiz)
    dp.message(Command("stats"))(cmd_stats)
    dp.message()(handle_answer)

# Хэндлер на команду /start
async def cmd_start(message: types.Message):
    await message.answer("Привет! Я бот для проведения квиза по Python. Введите /quiz, чтобы начать.")

# Хэндлер на команду /quiz
async def cmd_quiz(message: types.Message):
    user_id = message.from_user.id
    await reset_user_progress(user_id)  # Сбрасываем прогресс пользователя перед началом нового квиза
    await update_quiz_index(user_id, 0)  # Устанавливаем индекс вопроса на 0
    await start_quiz(user_id, message)

# Хэндлер на команду /stats
async def cmd_stats(message: types.Message):
    top_users = await get_top_users()
    if not top_users:
        await message.answer("Пока нет данных о статистике. Пройдите квиз, чтобы попасть в рейтинг.")
        return

    stats_text = "🏆 Топ-10 участников квиза:\n\n"
    for i, (user_id, best_score, attempts) in enumerate(top_users, start=1):
        stats_text += f"{i}. Участник {user_id}: лучший результат {best_score}, количество попыток {attempts} 🧠\n"
    
    await message.answer(stats_text)

# Функция для начала или продолжения квиза
async def start_quiz(user_id, message):
    question_index = await get_quiz_index(user_id)

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
async def handle_answer(message: types.Message):
    user_id = message.from_user.id
    user_answer = message.text
    question_index = await get_quiz_index(user_id)
    
    if question_index >= len(quiz_data):
        await message.answer("Квиз уже завершен. Введите /quiz, чтобы начать заново.")
        return

    question_data = quiz_data[question_index]
    correct_option = question_data['correct_option']
    correct_answer = question_data['options'][correct_option]
    is_correct = int(user_answer == correct_answer)
    
    # Сохраняем ответ пользователя в базе данных
    await save_user_answer(user_id, question_index, user_answer, correct_answer, is_correct)

    # Формируем ответ в зависимости от правильности
    if is_correct:
        feedback = f"Ваш ответ: {user_answer} ✅"
    else:
        feedback = f"Ваш ответ: {user_answer} ❌\nПравильный ответ: {correct_answer}"

    # Отправляем ответ без клавиатуры
    await message.answer(feedback, reply_markup=ReplyKeyboardRemove())
    
    # Обновляем индекс вопроса
    await update_quiz_index(user_id, question_index + 1)
    
    # Переходим к следующему вопросу или завершаем квиз
    await start_quiz(user_id, message)

# Функция для отправки итоговых результатов
async def send_final_results(user_id, message):
    async with aiosqlite.connect('quiz_bot.db') as db:
        async with db.execute('SELECT COUNT(*) FROM user_answers WHERE user_id = ? AND is_correct = 1', (user_id,)) as cursor:
            correct_answers = (await cursor.fetchone())[0]
    
    # Обновляем статистику пользователя и проверяем, является ли это новый рекорд
    is_new_record, best_score = await update_user_statistics(user_id, correct_answers)
    
    if is_new_record:
        result_message = f"Квиз завершен! Ваш результат: {correct_answers} правильных ответов. 🎉 Новый рекорд!\nДля просмотра результат введите /stats"
    else:
        result_message = f"Квиз завершен! Ваш результат: {correct_answers} правильных ответов.\nВаш лучший результат: {best_score}.\nДля просмотра результат введите /stats"

    await message.answer(result_message)
