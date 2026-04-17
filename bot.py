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
        KeyboardButton("🏆 Топ-лиги"),
        KeyboardButton("📰 Новости футбола"),
        KeyboardButton("📊 Турнирные таблицы"),
        KeyboardButton("ℹ️ Помощь")
    )
    return keyboard

# === ИНФО О ЛИГАХ ===
leagues_info = {
    "apl": "🏴󠁧󠁢󠁥󠁮󠁧󠁿 **АПЛ (Английская Премьер-лига)**\n\nЧемпионы по сезонам:\n• 2023/24 - Манчестер Сити\n• 2022/23 - Манчестер Сити\n• 2021/22 - Манчестер Сити\n• 2020/21 - Манчестер Сити\n\n🏆 Всего титулов:\n1. Манчестер Юнайтед - 20\n2. Ливерпуль - 19\n3. Арсенал - 13\n4. Манчестер Сити - 8",
    "laliga": "🇪🇸 **Ла Лига (Испания)**\n\nЧемпионы по сезонам:\n• 2023/24 - Реал Мадрид\n• 2022/23 - Барселона\n• 2021/22 - Реал Мадрид\n\n🏆 Всего титулов:\n1. Реал Мадрид - 35\n2. Барселона - 27\n3. Атлетико Мадрид - 11",
    "bundesliga": "🇩🇪 **Бундеслига (Германия)**\n\nЧемпионы по сезонам:\n• 2023/24 - Байер 04\n• 2022/23 - Бавария\n• 2021/22 - Бавария\n\n🏆 Всего титулов:\n1. Бавария - 32\n2. Боруссия Дортмунд - 8\n3. Вердер - 4",
    "seriea": "🇮🇹 **Серия А (Италия)**\n\nЧемпионы по сезонам:\n• 2023/24 - Интер\n• 2022/23 - Наполи\n• 2021/22 - Милан\n\n🏆 Всего титулов:\n1. Ювентус - 36\n2. Милан - 19\n3. Интер - 19",
    "ligue1": "🇫🇷 **Лига 1 (Франция)**\n\nЧемпионы по сезонам:\n• 2023/24 - ПСЖ\n• 2022/23 - ПСЖ\n• 2021/22 - ПСЖ\n\n🏆 Всего титулов:\n1. ПСЖ - 12\n2. Сент-Этьен - 10\n3. Марсель - 9",
    "rfpl": "🇷🇺 **РПЛ (Россия)**\n\nЧемпионы по сезонам:\n• 2023/24 - Зенит\n• 2022/23 - Зенит\n• 2021/22 - Зенит\n\n🏆 Всего титулов:\n1. Зенит - 10\n2. Спартак - 10\n3. ЦСКА - 6"
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
        "🔍 **Что я умею:**\n"
        "• Отвечать на любые вопросы о футболе\n"
        "• Искать актуальные новости в интернете\n"
        "• Рассказывать о турнирных таблицах\n"
        "• Обсуждать игроков, команды, тактику\n\n"
        "Используй кнопки ниже 👇",
        reply_markup=main_keyboard()
    )

# === ОБРАБОТКА КНОПОК МЕНЮ ===
@bot.message_handler(func=lambda message: message.text == "⚽ Задать вопрос")
def ask_question(message):
    bot.send_message(message.chat.id, "Задавай любой вопрос о футболе! Я найду актуальную информацию в интернете 👇")

@bot.message_handler(func=lambda message: message.text == "🏆 Топ-лиги")
def show_leagues(message):
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("🏴󠁧󠁢󠁥󠁮󠁧󠁿 АПЛ", callback_data="apl"),
        InlineKeyboardButton("🇪🇸 Ла Лига", callback_data="laliga"),
        InlineKeyboardButton("🇩🇪 Бундеслига", callback_data="bundesliga"),
        InlineKeyboardButton("🇮🇹 Серия А", callback_data="seriea"),
        InlineKeyboardButton("🇫🇷 Лига 1", callback_data="ligue1"),
        InlineKeyboardButton("🇷🇺 РПЛ", callback_data="rfpl")
    )
    bot.send_message(message.chat.id, "📊 Выбери лигу, чтобы узнать о чемпионах:", reply_markup=keyboard)

@bot.message_handler(func=lambda message: message.text == "📰 Новости футбола")
def football_news(message):
    bot.send_chat_action(message.chat.id, 'typing')
    answer = ask_football_ai("Расскажи самые свежие новости футбола за последние дни. Какие громкие трансферы, результаты матчей, события? Используй поиск в интернете.")
    bot.reply_to(message, answer)

@bot.message_handler(func=lambda message: message.text == "📊 Турнирные таблицы")
def standings(message):
    bot.send_chat_action(message.chat.id, 'typing')
    answer = ask_football_ai("Покажи текущие турнирные таблицы топ-5 лиг (АПЛ, Ла Лига, Бундеслига, Серия А, Лига 1). Кто лидирует? Используй поиск в интернете для актуальных данных.")
    bot.reply_to(message, answer)

@bot.message_handler(func=lambda message: message.text == "ℹ️ Помощь")
def help_command(message):
    bot.send_message(
        message.chat.id,
        "📖 **Помощь**\n\n"
        "⚽ **Задать вопрос** - любой вопрос о футболе (я ищу актуальную информацию в интернете)\n"
        "🏆 **Топ-лиги** - информация о чемпионатах и их победителях\n"
        "📰 **Новости футбола** - свежие новости из мира футбола\n"
        "📊 **Турнирные таблицы** - текущие таблицы топ-лиг\n\n"
        "🌐 **Умею искать в интернете**: результаты матчей, трансферы, турнирные таблицы и любые актуальные события 2026 года!\n\n"
        "💡 **Примеры вопросов:**\n"
        "• Кто выиграет Лигу Чемпионов?\n"
        "• Какие трансферы прошлым летом?\n"
        "• Кто лучший бомбардир в истории?\n"
        "• Сравни Месси и Роналду"
    )

# === ОБРАБОТКА ИНЛАЙН КНОПОК ===
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if call.data in leagues_info:
        bot.send_message(call.message.chat.id, leagues_info[call.data], parse_mode="Markdown")
        bot.answer_callback_query(call.id)

# === ОБРАБОТКА ТЕКСТОВЫХ ВОПРОСОВ ===
@bot.message_handler(func=lambda message: True)
def handle_question(message):
    # Пропускаем команды и кнопки
    if message.text in ["⚽ Задать вопрос", "🏆 Топ-лиги", "📰 Новости футбола", "📊 Турнирные таблицы", "ℹ️ Помощь"]:
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