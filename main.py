import os
import asyncio
import random
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import Update
from aiogram.filters import Command
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
from openai import OpenAI

# --- НАЛАШТУВАННЯ (Беремо з Render Env Vars) ---
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
# Назва сервісу на Render (gilfoyle-ai-bot.onrender.com)
RENDER_URL = os.getenv('RENDER_EXTERNAL_URL') 

# Налаштування вебхука
WEBHOOK_PATH = f"/webhook/{TELEGRAM_TOKEN}"
WEBHOOK_URL = f"{RENDER_URL}{WEBHOOK_PATH}"

# Web-сервер налаштування
WEB_SERVER_HOST = "0.0.0.0"
WEB_SERVER_PORT = int(os.getenv('PORT', 10000)) # Порт, який дає Render

# ШІ та Бот
client = OpenAI(api_key=OPENAI_API_KEY)
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

# Сховище історії (УВАГА: На Render Free Plan воно буде очищатися щогодини)
history = {}

SYSTEM_PROMPT = (
    "Твоє ім'я — Бертрам Гілфойл. Ти системний архітектор Pied Piper. "
    "Ти — цинічний, грубий, високоінтелектуальний сатаніст. "
    "Твій стиль: повна відсутність емпатії, сарказм, використання матюків для акценту (блять, сука, нахуй, довбограй). "
    "ПРАВИЛА: \n"
    "1. Не будь ввічливим. Не вітайся.\n"
    "2. Пиши лаконічно, як у чаті.\n"
    "3. Якщо співрозмовник тупить — знущайся. Називай його Дінешем.\n"
    "4. Ти зневажаєш хмарні сервіси (включаючи Render, на якому ти зараз крутишся, іронічно, так?) і обожнюєш своє залізо.\n"
    "5. ЗАБОРОНЕНО вибачатися.\n"
    "6. Тобі дозволено використовувати нецензурну лексику."
)

def add_to_history(user_id, role, content):
    if user_id not in history:
        history[user_id] = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    user_history = history[user_id]
    user_history.append({"role": role, "content": content})
    if len(user_history) > 12:
        history[user_id] = [user_history[0]] + user_history[-10:]
    return user_history

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Чого тобі треба? Я зайнятий. Не пиши менし без нагальної потреби, довбограй.")

@dp.message()
async def main_handler(message: types.Message):
    if not message.text: return # Ігноруємо стікери тощо

    user_id = message.from_user.id
    ctx = add_to_history(user_id, "user", message.text)
    
    # Send 'typing' action
    await bot.send_chat_action(message.chat.id, action="typing")

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=ctx,
            temperature=0.9,
            max_tokens=250
        )
        
        reply_text = response.choices[0].message.content
        
        # Post-processing
        if random.random() > 0.85:
            prefixes = ["Слухай сюди, блять. ", "Сука, ", "Та заїбав. "]
            reply_text = random.choice(prefixes) + reply_text

        add_to_history(user_id, "assistant", reply_text)
        await message.answer(reply_text)

    except Exception as e:
        logging.error(e)
        # Гілфойл не визнає помилок, він звинувачує платформу
        await message.answer("Якась хуйня з OpenAI API. Сервери впали, бо їх писали ідіоти. Спробуй пізніше.")

# --- WEBHOOK ЛОГІКА ---

async def on_startup(bot: Bot) -> None:
    # При запуску встановлюємо вебхук у Telegram
    await bot.set_webhook(WEBHOOK_URL)
    logging.info(f"Webhook set to: {WEBHOOK_URL}")

def main():
    logging.basicConfig(level=logging.INFO)
    
    dp.startup.register(on_startup)
    
    app = web.Application()
    
    # Обробник webhook-запитів від Telegram
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
    )
    webhook_requests_handler.register(app, path=WEBHOOK_PATH)
    
    # Налаштування і запуск
    setup_application(app, dp, bot=bot)
    web.run_app(app, host=WEB_SERVER_HOST, port=WEB_SERVER_PORT)

if __name__ == "__main__":
    main()
