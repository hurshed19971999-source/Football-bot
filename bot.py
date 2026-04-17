import telebot
import requests
import json
import os
import threading
from flask import Flask
from time import sleep

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

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "⚽ **Футбольный эксперт теперь на сервере 24/7!** ⚽\n\n"
        "Задавай любой вопрос о футболе. Я всегда онлайн! 🚀"
    )

@bot.message_handler(func=lambda message: True)
def handle(message):
    bot.send_chat_action(message.chat.id, 'typing')
    answer = ask_football_ai(message.text)
    bot.reply_to(message, answer)

# === ЗАПУСК ВСЕГО СРАЗУ ===
if __name__ == "__main__":
    # Запускаем Flask в отдельном потоке (для Render)
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()
    
    # Небольшая задержка для гарантии
    sleep(2)
    
    print("🤖 Бот запущен на Render.com 24/7!")
    bot.infinity_polling()