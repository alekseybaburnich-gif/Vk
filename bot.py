from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import asyncio
import random
import os

TOKEN = os.getenv("TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()

hugs = [
    "🤗 {user} обнял(а) {target}!",
    "❤️ {user} крепко обнял(а) {target}!",
    "😊 {user} тепло обнял(а) {target}!"
]

@dp.message(Command("обнять"))
async def hug(message: types.Message):
    args = message.text.split()

    if len(args) < 2:
        await message.answer("Укажи кого обнять 😊")
        return

    target = args[1]

    await message.answer(
        random.choice(hugs).format(
            user=message.from_user.first_name,
            target=target
        )
    )

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
