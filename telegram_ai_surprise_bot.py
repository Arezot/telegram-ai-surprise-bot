### telegram_ai_surprise_bot/bot.py

### telegram_ai_surprise_bot/bot.py

from dotenv import load_dotenv
load_dotenv(dotenv_path="apikeys.env")
from telegram import Update, LabeledPrice
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from openai import OpenAI  # Импортируем новый клиент OpenAI
import random
import os

# Загрузка переменных окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)  # Создаем клиент OpenAI

# Список случайных призов
PRIZES = ["Кружка", "Футболка", "Наклейка", "Ничего 😅", "Премиум-доступ", "Секретный приз"]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я ИИ-бот. Напиши мне что-нибудь или введи /buy, чтобы купить сюрприз-бокс.")

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text

    # Используем новый синтаксис OpenAI API
    response = client.chat.completions.create(
        model="openchat/openchat-3.5-1210",
        messages=[{"role": "user", "content": user_message}]
    )

    reply = response.choices[0].message.content  # Новый способ доступа к данным
    await update.message.reply_text(reply)

async def buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prices = [LabeledPrice("Сюрприз бокс", 10000)]  # 100 рублей (в копейках)
    await context.bot.send_invoice(
        chat_id=update.message.chat_id,
        title="Сюрприз бокс",
        description="Оплати и получи случайный приз!",
        payload="surprise-box",
        provider_token=os.getenv("PAYMENT_PROVIDER_TOKEN"),  # Опечатка исправлена
        currency="RUB",
        prices=prices,
        start_parameter="buy-surprise"
    )

async def successful_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prize = random.choice(PRIZES)
    await update.message.reply_text(f"Поздравляем! Вам выпало: {prize}")

if __name__ == "__main__":
    print(f"BOT_TOKEN: {BOT_TOKEN}")
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("buy", buy))
    app.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

    app.run_polling()