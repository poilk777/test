import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
import os

# Токен бота (вставьте ваш токен от @BotFather или используйте переменную окружения)
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


@dp.message(CommandStart())
async def send_welcome(message: types.Message):
    await message.answer("Привет! Я эхо-бот. Напишите мне что-нибудь, и я отправлю вам это же сообщение обратно! 😊")


@dp.message()
async def echo_handler(message: types.Message):
    # Отправляем то же сообщение обратно
    await message.answer(message.text or str(message))


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nБот выключен!")
