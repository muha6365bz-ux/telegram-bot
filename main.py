import asyncio
import random
import time

from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

from answers import answers
from questions import questions

API_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"   # аз BotFather мегирӣ
WEBHOOK_URL = "YOUR_RENDER_WEBHOOK_URL" # Render → https://.../webhook

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

user_state = {}  # барои ҳар user → саволҳои боқӣ ва таймер


def get_keyboard():
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="A", callback_data="A")],
        [InlineKeyboardButton(text="B", callback_data="B")],
        [InlineKeyboardButton(text="C", callback_data="C")],
        [InlineKeyboardButton(text="D", callback_data="D")]
    ])
    return kb


async def send_question(user_id):
    st = user_state[user_id]
    if not st["left"]:
        return await bot.send_message(user_id, "Саволҳо тамом шуданд! /reset барои аз нав")

    q_id = random.choice(st["left"])
    st["left"].remove(q_id)
    st["current"] = q_id
    st["time"] = time.time()

    q = questions[q_id]

    if q.get("text"):
        await bot.send_message(user_id, f"{q_id}) {q['text']}")

    if q.get("img"):
        await bot.send_photo(user_id, photo=open(f"imgs/{q_id}.png", "rb"))

    await bot.send_message(user_id, "Ваш ответ:", reply_markup=get_keyboard())


@dp.message(Command("start"))
async def cmd_start(msg: types.Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Бо вақт (180с)", callback_data="mode_time")],
        [InlineKeyboardButton(text="Бе вақт", callback_data="mode_no")]
    ])
    await msg.answer("Режимро интихоб кунед:", reply_markup=kb)


@dp.message(Command("reset"))
async def cmd_reset(msg: types.Message):
    user_state[msg.from_user.id] = {
        "mode": None,
        "left": list(range(1, 625)),
        "current": None,
        "time": None
    }
    await msg.answer("Аз нав. /start")


@dp.callback_query(F.data.in_({"mode_time", "mode_no"}))
async def select_mode(cb: types.CallbackQuery):
    mode = cb.data
    user_state[cb.from_user.id] = {
        "mode": "time" if mode == "mode_time" else "no",
        "left": list(range(1, 625)),
        "current": None,
        "time": None
    }
    await cb.message.answer("Оғоз мешавад...")
    await send_question(cb.from_user.id)


@dp.callback_query(F.data.in_({"A", "B", "C", "D"}))
async def check_answer(cb: types.CallbackQuery):
    user = cb.from_user.id
    st = user_state.get(user)
    if not st:
        return await cb.message.answer("Бо /start сар кунед")

    qid = st["current"]
    correct = answers[qid]
    chosen = cb.data

    if chosen == correct:
        await cb.message.answer("Дуруст")
    else:
        q = questions[qid]
        await cb.message.answer(f"Нодуруст. Дуруст: {correct} = {q[correct]}")

    await send_question(user)


async def webhook():
    await bot.set_webhook(WEBHOOK_URL)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(webhook())
