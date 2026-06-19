from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import asyncio
import random
import sqlite3
import os
import time

TOKEN = os.getenv("TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()

db = sqlite3.connect("users.db")
cur = db.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY,
    name TEXT,
    coins INTEGER DEFAULT 100,
    xp INTEGER DEFAULT 0
)
""")

db.commit()


def add_user(user):
    cur.execute(
        "INSERT OR IGNORE INTO users(id,name) VALUES(?,?)",
        (user.id, user.first_name)
    )
    db.commit()


def get_user(user):
    add_user(user)
    cur.execute(
        "SELECT coins,xp FROM users WHERE id=?",
        (user.id,)
    )
    return cur.fetchone()


def change_coins(user, amount):
    add_user(user)
    cur.execute(
        "UPDATE users SET coins=coins+? WHERE id=?",
        (amount,user.id)
    )
    db.commit()


def change_xp(user, amount):
    add_user(user)
    cur.execute(
        "UPDATE users SET xp=xp+? WHERE id=?",
        (amount,user.id)
    )
    db.commit()



@dp.message(Command("start"))
async def start(message: types.Message):
    add_user(message.from_user)
    await message.answer(
        "🔥 Бот запущен!\n"
        "Команды:\n"
        "/профиль\n"
        "/баланс\n"
        "/работать\n"
        "/топ\n"
        "/обнять @user\n"
        "/кубик"
    )



@dp.message(Command("профиль"))
async def profile(message: types.Message):
    coins,xp = get_user(message.from_user)

    await message.answer(
        f"👤 {message.from_user.first_name}\n"
        f"💰 Монеты: {coins}\n"
        f"⭐ Опыт: {xp}"
    )



@dp.message(Command("баланс"))
async def balance(message: types.Message):
    coins,xp = get_user(message.from_user)

    await message.answer(
        f"💰 Твой баланс: {coins}"
    )



@dp.message(Command("работать"))
async def work(message: types.Message):

    reward = random.randint(10,50)

    change_coins(message.from_user,reward)
    change_xp(message.from_user,10)

    await message.answer(
        f"🛠 Ты поработал!\n"
        f"Получено: +{reward} монет"
    )



@dp.message(Command("кубик"))
async def dice(message: types.Message):

    num=random.randint(1,6)

    await message.answer(
        f"🎲 Выпало число: {num}"
    )



@dp.message(Command("монетка"))
async def coin(message: types.Message):

    await message.answer(
        random.choice(
            ["🪙 Орёл","🪙 Решка"]
        )
    )



actions={
"обнять":"🤗 обнял(а)",
"поцеловать":"😘 поцеловал(а)",
"погладить":"😊 погладил(а)",
"ударить":"👊 ударил(а)"
}



async def action(message,cmd):

    args=message.text.split()

    if len(args)<2:
        await message.answer(
            "Нужно указать пользователя"
        )
        return

    await message.answer(
        f"{message.from_user.first_name} "
        f"{actions[cmd]} {args[1]}"
    )



@dp.message(Command("обнять"))
async def hug(message):
    await action(message,"обнять")


@dp.message(Command("поцеловать"))
async def kiss(message):
    await action(message,"поцеловать")


@dp.message(Command("погладить"))
async def pat(message):
    await action(message,"погладить")


@dp.message(Command("ударить"))
async def hit(message):
    await action(message,"ударить")



@dp.message(Command("шанс"))
async def chance(message):

    await message.answer(
        f"🎯 Шанс: {random.randint(0,100)}%"
    )



async def main():
    await dp.start_polling(bot)


if __name__=="__main__":
    asyncio.run(main())