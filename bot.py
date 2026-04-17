import telebot
import requests
import json
import os

TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
OPENROUTER_KEY = os.environ.get("OPENROUTER_API_KEY")

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
    bot.send_message(message.chat.id, "⚽ Футбольный эксперт теперь на сервере 24/7! Задавай любой вопрос!")

@bot.message_handler(func=lambda message: True)
def handle(message):
    bot.send_chat_action(message.chat.id, 'typing')
    answer = ask_football_ai(message.text)
    bot.reply_to(message, answer)

print("🤖 Бот запущен на Render.com 24/7!")
bot.infinity_polling()