import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from google import genai

# Конфигурация бота и Gemini API
BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

MODELS = [
    {"name": "gemini-2.5-flash", "label": "2.5 Flash"},
    {"name": "gemini-3.5-flash-lite", "label": "3.5 Flash-Lite"},
    {"name": "gemini-2.0-flash", "label": "2.0 Flash"},
    {"name": "gemini-2.0-flash-lite", "label": "2.0 Flash-Lite"},
    {"name": "gemini-3.1-flash-lite", "label": "3.1 Flash-Lite"}
]

user_models = {}

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
ai_client = genai.Client(api_key=GEMINI_KEY)

def get_main_keyboard():
    builder = InlineKeyboardBuilder()
    for m in MODELS:
        builder.button(text=m["label"], callback_data=f"set_model:{m['name']}")
    builder.button(text="⭐ Купить Stars / Поддержать", callback_data="buy_stars")
    builder.button(text="🎁 Получить подарок от бота", callback_data="get_gift")
    builder.adjust(2, 2, 1)
    return builder.as_markup()

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    user_id = message.from_user.id
    if user_id not in user_models:
        user_models[user_id] = MODELS[0]["name"]
    
    current_label = next(m["label"] for m in MODELS if m["name"] == user_models[user_id])
    await message.answer(
        f"Привет! Я готов к работе.\nТекущая модель: **{current_label}**\n\n"
        "Выберите действие или отправьте текстовый вопрос:",
        reply_markup=get_main_keyboard(),
        parse_mode="Markdown"
    )

@dp.callback_query(F.data == "buy_stars")
async def send_invoice_handler(callback: types.CallbackQuery):
    prices = [types.LabeledPrice(label="Поддержка бота", amount=10)]
    
    await bot.send_invoice(
        chat_id=callback.message.chat.id,
        title="Оплата Telegram Stars",
        description="Пополнение баланса или поддержка работы ИИ-бота",
        payload="stars_payment_payload",
        currency="XTR",
        prices=prices
    )
    await callback.answer()

@dp.pre_checkout_query()
async def pre_checkout_handler(pre_checkout_query: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@dp.message(F.successful_payment)
async def successful_payment_handler(message: types.Message):
    payment_info = message.successful_payment
    await message.answer(
        f"Спасибо за оплату! Получено {payment_info.total_amount} Stars ⭐."
    )

@dp.callback_query(F.data == "get_gift")
async def send_gift_handler(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    
    try:
        await bot.send_gift(
            user_id=user_id,
            gift_id="5102392472004201011"
        )
        await callback.message.answer("🎁 Подарок успешно отправлен вам в профиль!")
    except Exception as e:
        await callback.message.answer(
            f"Не удалось отправить подарок. Возможно, на балансе бота недостаточно Stars.\nОшибка: {e}"
        )
    await callback.answer()

@dp.callback_query(F.data.startswith("set_model:"))
async def set_model_handler(callback: types.CallbackQuery):
    selected_model = callback.data.split(":")[1]
    user_models[callback.from_user.id] = selected_model
    label = next(m["label"] for m in MODELS if m["name"] == selected_model)
    
    await callback.message.edit_text(
        f"Модель изменена на **{label}**.",
        reply_markup=get_main_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()

# Обработчик текстовых сообщений
@dp.message(F.text)
async def ai_response_handler(message: types.Message):
    user_id = message.from_user.id
    selected_model = user_models.get(user_id, MODELS[0]["name"])
    
    await bot.send_chat_action(chat_id=message.chat.id, action="typing")
    
    try:
        response = ai_client.models.generate_content(
            model=selected_model,
            contents=message.text
        )
        await message.answer(response.text)
    except Exception as e:
        await message.answer(f"Ошибка при обращении к ИИ: {e}")

# Обработчик стикеров (чтобы бот не вылетал)
@dp.message(F.sticker)
async def sticker_handler(message: types.Message):
    if message.sticker.emoji:
        prompt = f"Пользователь прислал стикер с эмодзи {message.sticker.emoji}. Ответь коротко и мило на этот эмодзи."
        try:
            user_id = message.from_user.id
            selected_model = user_models.get(user_id, MODELS[0]["name"])
            response = ai_client.models.generate_content(
                model=selected_model,
                contents=prompt
            )
            await message.answer(response.text)
            return
        except Exception:
            pass
    
    await message.answer("Классный стикер! 😊 Задайте мне текстовый вопрос.")

async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
