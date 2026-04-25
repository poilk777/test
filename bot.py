#!/usr/bin/env python3
"""
Telegram Bot - простой бот с командами и меню
"""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes
)

# Токен бота (замените на свой)
BOT_TOKEN = "ВАШ_ТОКЕН_ЗДЕСЬ"

# Хранилище данных пользователей
users_data = {}

# Команды бота
COMMANDS = {
    "/start": "Привет! Я ваш помощник.",
    "/help": "Доступные команды: /start, /help, /info, /menu",
    "/info": "Информация о боте: версия 1.0, создан для помощи.",
    "/menu": "Показать главное меню."
}


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка команды /start"""
    user = update.effective_user
    username = user.username or user.first_name
    
    welcome_text = (
        f"Привет, {username}! 👋\n\n"
        f"Я помогу вам справиться с задачами.\n\n"
        f"Нажмите кнопку ниже, чтобы увидеть меню:"
    )
    
    keyboard = [
        [InlineKeyboardButton("📚 Мои задачи", callback_data="tasks")],
        [InlineKeyboardButton("ℹ️ Информация", callback_data="info")],
        [InlineKeyboardButton("👤 Профиль", callback_data="profile")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)
    
    # Сохраняем пользователя в данные
    users_data[user.id] = {"username": username, "count": 0}


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка команды /help"""
    help_text = (
        "<b>Доступные команды:</b>\n\n"
        "• <code>/start</code> - Начать работу с ботом\n"
        "• <code>/help</code> - Показать эту справку\n"
        "• <code>/info</code> - Информация о боте\n"
        "• <code>/menu</code> - Главное меню\n"
        "• <code>/settings</code> - Настройки"
    )
    await update.message.reply_text(help_text, parse_mode="HTML")


async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка команды /info"""
    info_text = (
        "<b>🤖 Мой помощник v1.0</b>\n\n"
        "Я создан, чтобы упростить вашу жизнь!\n\n"
        "<b>Возможности:</b>\n"
        "• Отвечаю на вопросы\n"
        "• Управляю задачами\n"
        "• Предоставляю информацию\n\n"
        "<i>Используйте /menu для доступа ко всем функциям</i>"
    )
    await update.message.reply_text(info_text, parse_mode="HTML")


async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка команды /menu"""
    menu_text = "🎯 <b>Главное меню</b>"
    
    keyboard = [
        [InlineKeyboardButton("✅ Завершить задачу", callback_data="complete_task")],
        [InlineKeyboardButton("➕ Добавить задачу", callback_data="add_task")],
        [InlineKeyboardButton("📋 Список задач", callback_data="list_tasks")],
        [InlineKeyboardButton("⚙️ Настройки", callback_data="settings")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(menu_text, reply_markup=reply_markup, parse_mode="HTML")


async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка команды /settings"""
    settings_text = (
        "<b>⚙️ Настройки</b>\n\n"
        "Выберите опцию настройки:"
    )
    
    keyboard = [
        [InlineKeyboardButton("🔔 Уведомления", callback_data="notifications")],
        [InlineKeyboardButton("🌐 Язык", callback_data="language")],
        [InlineKeyboardButton("❌ Выйти", callback_data="exit")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(settings_text, reply_markup=reply_markup, parse_mode="HTML")


async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка нажатий кнопок в меню"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    responses = {
        "tasks": "📚 <b>Мои задачи</b>\n\nУ вас пока нет активных задач.",
        "info": "ℹ️ <b>Информация</b>\n\nБот работает 24/7 и готов помочь!",
        "profile": "👤 <b>Профиль</b>\n\nВы используете бота уже несколько раз!",
        "complete_task": "✅ <b>Завершить задачу</b>\n\nВведите ID задачи для завершения:",
        "add_task": "➕ <b>Добавить задачу</b>\n\nВведите название новой задачи:",
        "list_tasks": "📋 <b>Список задач</b>\n\nНет задач в списке.",
        "settings": "⚙️ <b>Настройки</b>\n\nВыберите что изменить:",
        "notifications": "🔔 <b>Уведомления</b>\n\nУведомления включены ✓",
        "language": "🌐 <b>Язык</b>\n\nТекущий язык: Русский",
        "exit": "❌ <b>Выход</b>\n\nДо свидания!"
    }
    
    response = responses.get(data, "Неизвестная команда.")
    
    if data in ["notifications", "language"]:
        keyboard = [[InlineKeyboardButton("↩️ Назад", callback_data="back")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
    else:
        keyboard = [
            [InlineKeyboardButton("↩️ Назад", callback_data="menu")],
            [InlineKeyboardButton("🏠 Главная", callback_data="home")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(response, parse_mode="HTML", reply_markup=reply_markup)


async def echo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка обычных сообщений"""
    message = update.message.text
    
    # Простейшая реакция на слова
    if "привет" in message.lower():
        response = "Привет! Чем могу помочь?"
    elif "как дела" in message.lower():
        response = "Отлично, спасибо! А у вас как?"
    elif "пока" in message.lower():
        response = "До свидания! Возвращайтесь ещё!"
    elif "?" in message:
        response = "Хороший вопрос! Попробуйте использовать /help для списка команд."
    else:
        response = "Я пока не знаю, как ответить на это. Используйте /help для команд."
    
    await update.message.reply_text(response)


def main():
    """Основная функция запуска бота"""
    print("🤖 Запуск Telegram бота...")
    
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Добавляем handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("info", info_command))
    application.add_handler(CommandHandler("menu", menu_command))
    application.add_handler(CommandHandler("settings", settings_command))
    
    # Callback query handlers
    application.add_handler(CallbackQueryHandler(handle_callback_query))
    
    # Echo handler для обычных сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo_handler))
    
    # Запуск бота
    print("✅ Бот запущен! Нажмите Start в Telegram для начала работы.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
