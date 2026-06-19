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
xp INTEGER DEFAULT 0,
last_work INTEGER DEFAULT 0
)
""")

db.commit()


def user_add(user):
    cur.execute(
        "INSERT OR IGNORE INTO users(id,name) VALUES(?,?)",
        (user.id,user.first_name)
    )
    db.commit()


def user_data(user):
    user_add(user)

    cur.execute(
        "SELECT coins,xp FROM users WHERE id=?",
        (user.id,)
    )

    return cur.fetchone()


def add_money(user,amount):
    user_add(user)

    cur.execute(
        "UPDATE users SET coins=coins+? WHERE id=?",
        (amount,user.id)
    )

    db.commit()


def add_xp(user,amount):
    user_add(user)

    cur.execute(
        "UPDATE users SET xp=xp+? WHERE id=?",
        (amount,user.id)
    )

    db.commit()



@dp.message(Command("start"))
async def start(message:types.Message):

    user_add(message.from_user)

    await message.answer(
        "🔥 Бот запущен!\n\n"
        "Команды:\n"
        "/профиль\n"
        "/работать\n"
        "/топ\n"
        "/кубик\n"
        "/монетка"
    )



@dp.message(Command("профиль"))
async def profile(message:types.Message):

    coins,xp=user_data(message.from_user)

    lvl=xp//100+1

    await message.answer(
        f"👤 {message.from_user.first_name}\n"
        f"💰 Монеты: {coins}\n"
        f"⭐ Опыт: {xp}\n"
        f"🏆 Уровень: {lvl}"
    )



@dp.message(Command("работать"))
async def work(message:types.Message):

    user_add(message.from_user)

    cur.execute(
        "SELECT last_work FROM users WHERE id=?",
        (message.from_user.id,)
    )

    last=cur.fetchone()[0]

    now=int(time.time())

    if now-last < 60:
        await message.answer(
            "⏳ Подожди минуту"
        )
        return


    reward=random.randint(20,100)

    add_money(
        message.from_user,
        reward
    )

    add_xp(
        message.from_user,
        20
    )

    cur.execute(
        "UPDATE users SET last_work=? WHERE id=?",
        (now,message.from_user.id)
    )

    db.commit()


    await message.answer(
        f"🛠 Работа выполнена!\n"
        f"💰 +{reward}"
    )



@dp.message(Command("баланс"))
async def balance(message:types.Message):

    coins,xp=user_data(message.from_user)

    await message.answer(
        f"💰 Баланс: {coins}"
    )



async def main():

    await dp.start_polling(bot)


if __name__=="__main__":
    asyncio.run(main())