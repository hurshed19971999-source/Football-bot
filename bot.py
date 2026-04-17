import telebot
import requests
import json
import os
import threading
from flask import Flask
from time import sleep
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# === ТОКЕНЫ ===
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
OPENROUTER_KEY = os.environ.get("OPENROUTER_API_KEY")

# === ФЛАСК (веб-сервер для Render) ===
app = Flask(__name__)

@app.route('/')
def home():
    return "⚽ Футбольный бот работает 24/7!"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

# === ТЕЛЕГРАМ БОТ ===
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# === КНОПКИ ГЛАВНОГО МЕНЮ ===
def main_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    keyboard.add(
        KeyboardButton("⚽ Задать вопрос"),
        KeyboardButton("📸 Фото игроков"),
        KeyboardButton("🏆 Топ-лиги"),
        KeyboardButton("ℹ️ Помощь")
    )
    return keyboard

# === ИНЛАЙН КНОПКИ ДЛЯ ФОТО ===
def players_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("🐐 Месси", callback_data="messi"),
        InlineKeyboardButton("🐐 Роналду", callback_data="ronaldo"),
        InlineKeyboardButton("🇫🇷 Мбаппе", callback_data="mbappe"),
        InlineKeyboardButton("🇳🇴 Холланд", callback_data="haaland"),
        InlineKeyboardButton("🇧🇷 Неймар", callback_data="neymar"),
        InlineKeyboardButton("🇪🇸 Педри", callback_data="pedri")
    )
    return keyboard

# === ФУНКЦИЯ ЗАПРОСА К ИИ ===
def ask_football_ai(question):
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_KEY}",
                "Content-Type": "application/json",
            },
            data=json.dumps({
                "model": "openrouter/free",
                "messages": [{"role": "user", "content": f"Ты эксперт по футболу. Отвечай кратко на русском. Вопрос: {question}"}],
                "max_tokens": 500
            }),
            timeout=30
        )
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        return f"❌ Ошибка API: {response.status_code}"
    except Exception as e:
        return f"❌ Ошибка: {e}"

# === ФОТО ИГРОКОВ ===
player_photos = {
    "messi": "https://img.uefa.com/imgml/TP/players/1/2025/324x324/190038.jpg",
    "ronaldo": "https://img.uefa.com/imgml/TP/players/1/2025/324x324/63706.jpg",
    "mbappe": "https://img.uefa.com/imgml/TP/players/1/2025/324x324/250108855.jpg",
    "haaland": "https://img.uefa.com/imgml/TP/players/1/2025/324x324/250130613.jpg",
    "neymar": "https://img.uefa.com/imgml/TP/players/1/2025/324x324/250042244.jpg",
    "pedri": "https://img.uefa.com/imgml/TP/players/1/2025/324x324/250134011.jpg"
}

player_captions = {
    "messi": "🐐 **Лионель Месси**\n\n✅ 8 Золотых мячей\n✅ Чемпион мира 2022\n✅ 45 титулов",
    "ronaldo": "🐐 **Криштиану Роналду**\n\n✅ 5 Золотых мячей\n✅ 5 Лиг Чемпионов\n✅ 900+ голов",
    "mbappe": "⚡ **Килиан Мбаппе**\n\n✅ Чемпион мира 2018\n✅ Лучший бомбардир ЧМ-2022\n✅ Скорость 💨",
    "haaland": "💪 **Эрлинг Холланд**\n\n✅ Лучший бомбардир АПЛ 2023\n✅ 50+ голов за сезон\n✅ Физическая мощь",
    "neymar": "✨ **Неймар**\n\n✅ Финты и дриблинг\n✅ Лучший бомбардир Бразилии\n✅ Серебряный олимпийский",
    "pedri": "🎯 **Педри**\n\n✅ Лучший молодой игрок\n✅ Ла Масия\n✅ Гений передачи"
}

# === ТОП-ЛИГИ ===
leagues_info = {
    "apl": "🏴󠁧󠁢󠁥󠁮󠁧󠁿 **АПЛ** (Английская Премьер-лига)\n\nСамые титулованные:\n1. Манчестер Юнайтед - 20 титулов\n2. Ливерпуль - 19\n3. Арсенал - 13\n4. Манчестер Сити - 8",
    "laliga": "🇪🇸 **Ла Лига** (Испания)\n\nСамые титулованные:\n1. Реал Мадрид - 35 титулов\n2. Барселона - 27\n3. Атлетико Мадрид - 11",
    "bundesliga": "🇩🇪 **Бундеслига** (Германия)\n\nСамые титулованные:\n1. Бавария - 32 титула\n2. Боруссия Дортмунд - 8\n3. Вердер - 4",
    "seriea": "🇮🇹 **Серия А** (Италия)\n\nСамые титулованные:\n1. Ювентус - 36 титулов\n2. Милан - 19\n3. Интер - 19"
}

# === КОМАНДА /start ===
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "⚽ **Футбольный эксперт 24/7!** ⚽\n\n"
        "Я знаю всё о футболе. Используй кнопки ниже:",
        reply_markup=main_keyboard()
    )

# === ОБРАБОТКА КНОПОК МЕНЮ ===
@bot.message_handler(func=lambda message: message.text == "⚽ Задать вопрос")
def ask_question(message):
    bot.send_message(message.chat.id, "Задавай любой вопрос о футболе! 👇")

@bot.message_handler(func=lambda message: message.text == "📸 Фото игроков")
def show_players(message):
    bot.send_message(message.chat.id, "Выбери игрока:", reply_markup=players_keyboard())

@bot.message_handler(func=lambda message: message.text == "🏆 Топ-лиги")
def show_leagues(message):
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("🏴󠁧󠁢󠁥󠁮󠁧󠁿 АПЛ", callback_data="apl"),
        InlineKeyboardButton("🇪🇸 Ла Лига", callback_data="laliga"),
        InlineKeyboardButton("🇩🇪 Бундеслига", callback_data="bundesliga"),
        InlineKeyboardButton("🇮🇹 Серия А", callback_data="seriea")
    )
    bot.send_message(message.chat.id, "Выбери лигу:", reply_markup=keyboard)

@bot.message_handler(func=lambda message: message.text == "ℹ️ Помощь")
def help_command(message):
    bot.send_message(
        message.chat.id,
        "📖 **Помощь**\n\n"
        "⚽ Задать вопрос - любой вопрос о футболе\n"
        "📸 Фото игроков - фото топ-игроков\n"
        "🏆 Топ-лиги - информация о чемпионатах\n\n"
        "Бот работает 24/7 на сервере!"
    )

# === ОБРАБОТКА НАЖАТИЙ НА ИНЛАЙН КНОПКИ ===
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if call.data in player_photos:
        bot.send_photo(
            call.message.chat.id,
            player_photos[call.data],
            caption=player_captions[call.data],
            parse_mode="Markdown"
        )
        bot.answer_callback_query(call.id)
    
    elif call.data in leagues_info:
        bot.send_message(call.message.chat.id, leagues_info[call.data], parse_mode="Markdown")
        bot.answer_callback_query(call.id)

# === ОБРАБОТКА ТЕКСТОВЫХ ВОПРОСОВ ===
@bot.message_handler(func=lambda message: True)
def handle_question(message):
    # Пропускаем команды и кнопки
    if message.text in ["⚽ Задать вопрос", "📸 Фото игроков", "🏆 Топ-лиги", "ℹ️ Помощь"]:
        return
    
    bot.send_chat_action(message.chat.id, 'typing')
    answer = ask_football_ai(message.text)
    bot.reply_to(message, answer)

# === ЗАПУСК ===
if __name__ == "__main__":
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()
    sleep(2)
    print("🤖 Футбольный бот с меню запущен на Render.com 24/7!")
    bot.infinity_polling()