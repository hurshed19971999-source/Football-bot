import os
import asyncio
import logging
from starlette.applications import Starlette
from starlette.responses import Response, PlainTextResponse
from starlette.requests import Request
from starlette.routing import Route
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

# --- Настройки ---
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
OPENROUTER_KEY = os.environ.get("OPENROUTER_API_KEY")
# Render сам подставит этот URL
RENDER_EXTERNAL_URL = os.environ.get("RENDER_EXTERNAL_URL")
PORT = int(os.getenv("PORT", 8000))

logging.basicConfig(level=logging.INFO)

# --- Функция запроса к ИИ (оставляем как есть) ---
def ask_football_ai(question):
    import requests, json
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {OPENROUTER_KEY}", "Content-Type": "application/json"},
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

# --- Обработчики команд бота ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⚽ Футбольный эксперт теперь на сервере 24/7! Задавай любой вопрос!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return
    answer = ask_football_ai(update.message.text)
    await update.message.reply_text(answer)

# --- Главная функция, которая запускает веб-сервер и регистрирует вебхук ---
async def main():
    # Создаем приложение бота (без запуска polling)
    application = Application.builder().token(TELEGRAM_TOKEN).updater(None).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Регистрируем вебхук
    webhook_url = f"{RENDER_EXTERNAL_URL}/webhook"
    await application.bot.set_webhook(url=webhook_url)
    logging.info(f"Webhook set to {webhook_url}")

    # Создаем Starlette приложение для обработки входящих запросов от Telegram
    async def telegram_webhook(request: Request) -> Response:
        # Получаем обновление от Telegram и кладем в очередь бота
        data = await request.json()
        update = Update.de_json(data, application.bot)
        await application.process_update(update)
        return Response()

    async def health_check(request: Request) -> PlainTextResponse:
        return PlainTextResponse("OK")

    starlette_app = Starlette(routes=[
        Route("/webhook", telegram_webhook, methods=["POST"]),
        Route("/health", health_check, methods=["GET"]),
    ])

    # Запускаем веб-сервер
    import uvicorn
    config = uvicorn.Config(starlette_app, host="0.0.0.0", port=PORT, log_level="info")
    server = uvicorn.Server(config)
    logging.info("Starting web server...")
    await server.serve()

if __name__ == "__main__":
    asyncio.run(main())