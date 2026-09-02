import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
import google.generativeai as genai

# Включаем логирование
logging.basicConfig(level=logging.INFO)

# Получаем ключи из Render
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Настраиваем доступ к API Google
genai.configure(api_key=GEMINI_API_KEY)

# =======================================================
# ВЫБОР МОДЕЛИ
# Оставьте раскомментированной (без #) только одну строку
# =======================================================
# model_name = "gemini-1.5-flash"      # Базовая и быстрая
# model_name = "gemini-1.5-pro"        # Умная, для сложных рассуждений
# model_name = "gemini-2.0-flash-exp"  # Экспериментальная
model_name = "gemini-3.6-flash"        # Новейшая (из вашей ошибки 404)

model = genai.GenerativeModel(model_name)

# Инициализируем бота
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer("Привет! Я Чипи-бот. Моя нейросеть обновлена, жду твоих вопросов!")

@dp.message()
async def handle_message(message: types.Message):
    try:
        # Отправляем текст в Gemini
        response = model.generate_content(message.text)
        # Возвращаем ответ пользователю
        await message.reply(response.text)
    except Exception as e:
        logging.error(f"Ошибка ИИ: {e}")
        await message.reply(f"Ошибка при обращении к ИИ: {e}")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    
