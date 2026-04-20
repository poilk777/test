import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardMarkup, ReplyKeyboardButton

# Загрузка переменных окружения
load_dotenv()

# Инициализация бота
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Хранилище пользователей (в реальном проекте используйте базу данных)
users_db = {}

# Состояния FSM (Finite State Machine)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, default_state

class UserStates(default_state):
    waiting_name = State()
    waiting_email = State()
    waiting_password = State()


# Главная кнопка меню
def get_main_keyboard():
    markup = ReplyKeyboardMarkup(keyboard=[
        [ReplyKeyboardButton(text="📝 Регистрация"), ReplyKeyboardButton(text="🔐 Вход")],
        [ReplyKeyboardButton(text="❓ Помощь")]
    ], resize_keyboard=True)
    return markup


# Клавиатура после успешного действия
def get_success_keyboard():
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Вернуться в меню", callback_data="back_to_menu")]
    ])
    return markup


# Обработка команды /start
@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "👋 Привет! Я ваш помощник по аккаунтам.\n\n"
        "Выберите действие:",
        reply_markup=get_main_keyboard()
    )


# Обработка нажатия на кнопку "Регистрация"
@dp.message(F.text == "📝 Регистрация")
async def register_start(message: Message, state: FSMContext):
    # Очищаем предыдущие данные если есть
    await state.clear()
    
    user = users_db.get(str(message.from_user.id))
    if user and user.get('registered'):
        await message.answer(
            "✅ Вы уже зарегистрированы!\n"
            "Для входа используйте команду /login или кнопку 🔐",
            reply_markup=get_main_keyboard()
        )
    else:
        await message.answer(
            "📝 Регистрация\n\n"
            "Это безопасно! Просто заполните форму:\n\n"
            "Шаг 1/3 — Как вас зовут?",
            reply_markup=types.ReplyKeyboardRemove()
        )
        await state.update_data(current_step='name')
        await state.set_state(UserStates.waiting_name)


# Обработка ввода имени при регистрации
@dp.message(UserStates.waiting_name)
async def process_name(message: Message, state: FSMContext):
    try:
        # Сохраняем имя пользователя
        name = message.text.strip()
        
        # Проверяем длину имени
        if len(name) < 2:
            await message.answer(
                "⚠️ Имя должно быть не короче 2 символов.\n"
                "Введите ваше имя ещё раз:",
                reply_markup=types.ReplyKeyboardRemove()
            )
            return
        
        # Переходим к следующему шагу
        await state.update_data({'name': name})
        await message.answer(
            "Отлично! Теперь укажите ваш Email:\n"
            "(формат: example@email.com)",
            reply_markup=types.ReplyKeyboardRemove()
        )
        
        await state.update_data(current_step='email')
        await state.set_state(UserStates.waiting_email)
        
    except Exception as e:
        await message.answer("⚠️ Произошла ошибка. Попробуйте начать заново.")
        await state.clear()


# Обработка ввода email при регистрации
@dp.message(UserStates.waiting_email)
async def process_email(message: Message, state: FSMContext):
    import re
    try:
        email = message.text.strip().lower()
        
        # Простая проверка формата email
        email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if not re.match(email_regex, email):
            await message.answer(
                "⚠️ Неверный формат Email.\n"
                "Попробуйте снова (например: test@example.com):\n",
                reply_markup=types.ReplyKeyboardRemove()
            )
            return
        
        # Сохраняем email
        await state.update_data({'email': email})
        
        # Переходим к шагу пароля
        await message.answer(
            "Теперь выберите пароль:\n"
            "(минимум 6 символов)",
            reply_markup=types.ReplyKeyboardRemove()
        )
        
        await state.update_data(current_step='password')
        await state.set_state(UserStates.waiting_password)
        
    except Exception as e:
        await message.answer("⚠️ Произошла ошибка. Попробуйте начать заново.")
        await state.clear()


# Обработка ввода пароля при регистрации
@dp.message(UserStates.waiting_password)
async def process_password(message: Message, state: FSMContext):
    try:
        password = message.text.strip()
        
        # Проверка сложности пароля
        if len(password) < 6:
            await message.answer(
                "⚠️ Пароль слишком короткий (минимум 6 символов).\n"
                "Попробуйте снова:",
                reply_markup=types.ReplyKeyboardRemove()
            )
            return
        
        # Сохраняем пользователя
        user_data = await state.get_data()
        
        users_db[str(message.from_user.id)] = {
            'name': user_data['name'],
            'email': user_data['email'],
            'password': password,
            'registered': True,
            'logged_in': False
        }
        
        # Отправляем информацию о пользователе
        await message.answer(
            f"🎉 Поздравляем с регистрацией!\n\n"
            f"💡 Ваши данные сохранены:\n"
            f"👤 Имя: {user_data['name']}\n"
            f"📧 Email: {user_data['email']}\n\n"
            f"Используйте кнопку 🔐 Для входа в систему!",
            reply_markup=get_success_keyboard()
        )
        
        await state.clear()
        
    except Exception as e:
        await message.answer(f"⚠️ Произошла ошибка при регистрации: {e}")
        await state.clear()


# Обработка нажатия на кнопку "Вход"
@dp.message(F.text == "🔐 Вход")
async def login_start(message: Message, state: FSMContext):
    # Получаем пользователя из базы
    user_id = str(message.from_user.id)
    user = users_db.get(user_id)
    
    if not user or not user.get('registered'):
        await message.answer(
            "⚠️ У вас нет аккаунта.\n"
            "Сначала выполните регистрацию кнопкой 📝",
            reply_markup=get_main_keyboard()
        )
        return
    
    await state.update_data(current_step='login_login', user_id=user_id)
    await message.answer(
        "🔐 Вход в систему\n\n"
        "Шаг 1/2 — Введите ваш Email:",
        reply_markup=types.ReplyKeyboardRemove()
    )
    await state.set_state(UserStates.waiting_email)


# Обработка ввода Email при входе
@dp.message(UserStates.waiting_email)
async def process_login_email(message: Message, state: FSMContext):
    try:
        login = message.text.strip().lower()
        
        # Проверяем формат email
        import re
        email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if not re.match(email_regex, login):
            await message.answer(
                "⚠️ Неверный формат Email.\n"
                "Попробуйте снова:\n",
                reply_markup=types.ReplyKeyboardRemove()
            )
            return
        
        # Сохраняем логин во временные данные
        await state.update_data({'login': login})
        
        # Переходим к шапу паролю
        await message.answer(
            "Шаг 2/2 — Введите ваш пароль:",
            reply_markup=types.ReplyKeyboardRemove()
        )
        
        await state.update_data(current_step='login_password')
        await state.set_state(UserStates.waiting_password)
        
    except Exception as e:
        await message.answer("⚠️ Произошла ошибка. Попробуйте снова.")
        await state.clear()


# Обработка ввода пароля при входе
@dp.message(UserStates.waiting_password)
async def process_login_password(message: Message, state: FSMContext):
    try:
        password = message.text.strip()
        user_data = await state.get_data()
        
        # Проверяем учётные данные
        user = users_db.get(user_data['user_id'])
        
        if user['email'] != user_data['login']:
            await message.answer(
                "⚠️ Неверный Email.\n"
                "Попробуйте войти заново.",
                reply_markup=get_main_keyboard()
            )
            await state.clear()
            return
        
        if user['password'] != password:
            await message.answer(
                "⚠️ Неверный пароль.\n"
                "Попробуйте войти заново.",
                reply_markup=get_main_keyboard()
            )
            await state.clear()
            return
        
        # Успешный вход
        user['logged_in'] = True
        user['last_login'] = "Сейчас"
        
        await message.answer(
            f"✅ Добро пожаловать, {user['name']}!\n\n"
            f"Вы успешно вошли в систему.\n"
            f"📊 Ваш статус: активен\n\n"
            f"Добро пожаловать обратно!",
            reply_markup=get_success_keyboard()
        )
        
        await state.clear()
        
    except Exception as e:
        await message.answer(f"⚠️ Произошла ошибка при входе: {e}")
        await state.clear()


# Обработка callback-запроса (кнопки)
@dp.callback_query(F.data == "back_to_menu")
async def back_to_menu_callback(query: CallbackQuery):
    await query.message.edit_text(
        "👋 Вернитесь в главное меню.\n\n"
        "Что бы вы хотели сделать?",
        reply_markup=get_main_keyboard()
    )
    await query.answer()


# Команда /help
@dp.message(Command("help"))
async def cmd_help(message: Message):
    help_text = """
❓ *Помощь*

📌 Доступные команды:
• /start - запустить бота
• /help - показать эту подсказку

📝 Регистрация:
Нажмите кнопку 📝 Registration и следуйте инструкциям

🔐 Вход:
Нажмите кнопку 🔐 Login для входа в систему

💡 Советы:
• Всегда сохраняйте свои учётные данные в безопасности
• Используйте сложные пароли
• Не передавайте свой пароль третьим лицам
"""
    await message.answer(help_text, parse_mode="Markdown")


# Обработчик ошибок
@dp.message()
async def default_handler(message: Message):
    # Если пользователь пытается ответить на сообщение бота
    text = message.text.lower() if message.text else ""
    
    keyboard = get_main_keyboard()
    
    # Проверка текстовых команд
    if text == "/start":
        await cmd_start(message)
        return
    elif text == "/help":
        await cmd_help(message)
        return
    elif text in ["📝 регистрация", "📝 registration"]:
        await register_start(message, None)  # state будет обработано автоматически
        return
    elif text in ["🔐 вход", "🔐 login"]:
        await login_start(message, None)
        return
    elif text in ["❓ помощь", "❓ help"]:
        await cmd_help(message)
        return
    
    await message.answer(
        "❌ Неизвестная команда.\n"
        "Используйте /help для получения помощи или воспользуйтесь кнопками в меню.",
        reply_markup=keyboard
    )


# Запуск бота
if __name__ == "__main__":
    print("🚀 Запускаю Telegram-бота...")
    print("⚙️ Бот готов к работе!")
    dp.run_polling(bot)
