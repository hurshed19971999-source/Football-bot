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

# === ФЛАСК ===
app = Flask(__name__)

@app.route('/')
def home():
    return "⚽ Футбольный бот работает 24/7 с веб-поиском!"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

# === БОТ ===
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# === КНОПКИ ===
def main_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    keyboard.add(
        KeyboardButton("⚽ Задать вопрос"),
        KeyboardButton("📸 Фото игроков"),
        KeyboardButton("🏆 Топ-лиги"),
        KeyboardButton("📰 Новости футбола"),
        KeyboardButton("ℹ️ Помощь")
    )
    return keyboard

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

# === ФОТО ИГРОКОВ ===
player_photos = {
    "messi": "https://cdn.pixabay.com/photo/2022/12/20/06/18/lionel-messi-7668029_640.jpg",
    "ronaldo": "https://cdn.pixabay.com/photo/2022/11/22/10/29/cristiano-ronaldo-7609522_640.jpg",
    "mbappe": "https://cdn.pixabay.com/photo/2022/12/06/18/55/kylian-mbappe-7640139_640.jpg",
    "haaland": "https://cdn.pixabay.com/photo/2023/02/20/20/53/erling-haaland-7804054_640.jpg",
    "neymar": "https://cdn.pixabay.com/photo/2018/06/27/09/37/neymar-3502004_640.jpg",
    "pedri": "https://cdn.pixabay.com/photo/2021/07/12/12/23/pedri-6460953_640.jpg"
}

player_captions = {
    "messi": "🐐 **Лионель Месси**\n\n✅ 8 Золотых мячей\n✅ Чемпион мира 2022",
    "ronaldo": "🐐 **Криштиану Роналду**\n\n✅ 5 Золотых мячей\n✅ 900+ голов",
    "mbappe": "⚡ **Килиан Мбаппе**\n\n✅ Чемпион мира 2018\n✅ Лучший бомбардир ЧМ-2022",
    "haaland": "💪 **Эрлинг Холланд**\n\n✅ Лучший бомбардир АПЛ 2023",
    "neymar": "✨ **Неймар**\n\n✅ Лучший бомбардир Бразилии",
    "pedri": "🎯 **Педри**\n\n✅ Лучший молодой игрок"
}

# === ТОП-ЛИГИ ===
leagues_info = {
    "apl": "🏴󠁧󠁢󠁥󠁮󠁧󠁿 **АПЛ**\n\n1. Манчестер Юнайтед - 20\n2. Ливерпуль - 19\n3. Арсенал - 13",
    "laliga": "🇪🇸 **Ла Лига**\n\n1. Реал Мадрид - 35\n2. Барселона - 27\n3. Атлетико - 11",
    "bundesliga": "🇩🇪 **Бундеслига**\n\n1. Бавария - 32\n2. Боруссия Д - 8",
    "seriea": "🇮🇹 **Серия А**\n\n1. Ювентус - 36\n2. Милан - 19\n3. Интер - 19"
}

# === ФУНКЦИЯ ЗАПРОСА К ИИ С ВЕБ-ПОИСКОМ ===
def ask_football_ai(question):
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://t.me/Bothurshed_bot",
                "X-Title": "Football Expert Bot"
            },
            data=json.dumps({
                "model": "openai/gpt-4.1-mini:online",
                "messages": [
                    {
                        "role": "system",
                        "content": "Ты эксперт по футболу. Сегодня апрель 2026 года. Отвечай кратко, по делу, на русском языке, добавляй эмодзи ⚽. Если спрашивают про актуальные события (результаты матчей, трансферы, турнирные таблицы), используй поиск в интернете, чтобы дать точный и свежий ответ."
                    },
                    {
                        "role": "user",
                        "content": question
                    }
                ],
                "max_tokens": 800,
                "temperature": 0.7,
                "plugins": [{"id": "web", "max_results": 3}]
            }),
            timeout=45
        )
        
        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"]
        else:
            error_msg = f"Ошибка API: {response.status_code}"
            try:
                error_detail = response.json()
                error_msg += f" - {error_detail.get('error', {}).get('message', '')}"
            except:
                pass
            return f"❌ {error_msg}"
            
    except requests.exceptions.Timeout:
        return "⏰ Таймаут. API не отвечает. Попробуй ещё раз."
    except Exception as e:
        return f"❌ Ошибка: {str(e)[:150]}"

# === КОМАНДА /start ===
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id, 
        "⚽ **Футбольный эксперт 24/7 с доступом в интернет!** ⚽\n\n"
        "Я знаю всё о футболе, включая **свежие новости 2026 года**!\n\n"
        "📰 Могу рассказать о последних матчах, трансферах и результатах.\n\n"
        "Используй кнопки ниже 👇",
        reply_markup=main_keyboard()
    )

# === ОБРАБОТКА КНОПОК МЕНЮ ===
@bot.message_handler(func=lambda message: message.text == "⚽ Задать вопрос")
def ask_question(message):
    bot.send_message(message.chat.id, "Задавай любой вопрос о футболе! Я найду актуальную информацию в интернете 👇")

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

@bot.message_handler(func=lambda message: message.text == "📰 Новости футбола")
def football_news(message):
    bot.send_chat_action(message.chat.id, 'typing')
    answer = ask_football_ai("Расскажи самые свежие новости футбола за последние дни. Какие громкие трансферы, результаты матчей, события?")
    bot.reply_to(message, answer)

@bot.message_handler(func=lambda message: message.text == "ℹ️ Помощь")
def help_command(message):
    bot.send_message(
        message.chat.id,
        "📖 **Помощь**\n\n"
        "⚽ **Задать вопрос** - любой вопрос о футболе (я ищу актуальную информацию в интернете)\n"
        "📸 **Фото игроков** - фото топ-игроков\n"
        "🏆 **Топ-лиги** - информация о чемпионатах\n"
        "📰 **Новости футбола** - свежие новости\n\n"
        "🌐 **Умею искать в интернете**: результаты матчей, трансферы, турнирные таблицы и любые актуальные события 2026 года!"
    )

# === ОБРАБОТКА ИНЛАЙН КНОПОК ===
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    try:
        if call.data in player_photos:
            bot.send_photo(
                call.message.chat.id,
                player_photos[call.data],
                caption=player_captions[call.data],
                parse_mode="Markdown"
            )
        elif call.data in leagues_info:
            bot.send_message(call.message.chat.id, leagues_info[call.data], parse_mode="Markdown")
        bot.answer_callback_query(call.id)
    except Exception as e:
        bot.send_message(call.message.chat.id, f"❌ Ошибка: {e}")
        bot.answer_callback_query(call.id)

# === ОБРАБОТКА ТЕКСТОВЫХ ВОПРОСОВ ===
@bot.message_handler(func=lambda message: True)
def handle_question(message):
    # Пропускаем команды и кнопки
    if message.text in ["⚽ Задать вопрос", "📸 Фото игроков", "🏆 Топ-лиги", "📰 Новости футбола", "ℹ️ Помощь"]:
        return
    
    bot.send_chat_action(message.chat.id, 'typing')
    answer = ask_football_ai(message.text)
    bot.reply_to(message, answer)

# === ЗАПУСК ===
if __name__ == "__main__":
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()
    sleep(2)
    print("🤖 Футбольный бот с веб-поиском запущен на Render.com 24/7!")
    bot.infinity_polling()