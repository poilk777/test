import telebot
from telebot import types

# Создаем бота
BOT_TOKEN = 'YOUR_BOT_TOKEN_HERE'  # Вставьте токен от @BotFather
bot = telebot.TeleBot(BOT_TOKEN)


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    """Приветствие при команде /start"""
    welcome_message = """👋 Привет! Я бот, который отвечает 'hello world' на ваши сообщения!

Попробуйте написать мне что-нибудь, и я отвечу!"""
    bot.reply_to(message, welcome_message)


@bot.message_handler(content_types=['text'])
def handle_text(message):
    """Обработка текстовых сообщений"""
    bot.reply_to(message, "hello world")


print("Бот запущен...")
bot.infinity_polling()
