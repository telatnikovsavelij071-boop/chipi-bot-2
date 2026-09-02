import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart
import google.generativeai as genai

# Включаем логирование ошибок в консоль
logging.basicConfig(level=logging.INFO)

# Получаем секретные ключи из настроек Render
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Авторизация в Google Gemini API
genai.configure(api_key=GEMINI_API_KEY)

# Подключаем рабочую модель
model = genai.GenerativeModel("gemini-1.5-flash")

# Создаем экземпляры бота и диспетчера
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

# Обработчик команды /start
@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer("Привет! Я готов к работе. Напиши мне любой вопрос!")

# Обработчик всех текстовых сообщений
@dp.message()
async def handle_message(message: types.Message):
    try:
        # Запрос к нейросети
        response = model.generate_content(message.text)
        # Отправка ответа пользователю
        await message.reply(response.text)
    except Exception as e:
        logging.error(f"Ошибка при ответе: {e}")
        await message.reply("Произошла ошибка при обращении к нейросети. Попробуй позже.")

# Главная функция запуска
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
