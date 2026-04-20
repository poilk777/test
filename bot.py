import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import os

# Токен бота (замените на свой)
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Обработчик команды /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Привет! Я бот, отвечающий 'hello world' на любые сообщения!")

# Общий обработчик для всех текстовых сообщений
@dp.message(lambda message: True)
async def echo_hello_world(message: types.Message):
    await message.answer("hello world")

# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот остановлен")
