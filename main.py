# main.py
import asyncio
from aiogram import Bot, Dispatcher
from config import API_TOKEN
from db import create_table
from functions import setup_handlers

# Создаем объект бота и диспетчер
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Запуск бота
async def main():
    await create_table()  # Создание таблиц базы данных
    setup_handlers(dp)  # Настройка хэндлеров
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
