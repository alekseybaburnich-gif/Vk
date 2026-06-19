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

@dp.message(Command("кубик"))
async def dice(message: types.Message):
    num = random.randint(1,6)

    await message.answer(
        f"🎲 Выпало: {num}"
    )


@dp.message(Command("монетка"))
async def coin(message: types.Message):

    await message.answer(
        random.choice([
            "🪙 Орёл!",
            "🪙 Решка!"
        ])
    )


@dp.message(Command("шанс"))
async def chance(message: types.Message):

    await message.answer(
        f"🎯 Шанс: {random.randint(0,100)}%"
    )



actions = {
    "обнять":"🤗 обнял(а)",
    "поцеловать":"😘 поцеловал(а)",
    "погладить":"😊 погладил(а)",
    "дать_пять":"🙌 дал(а) пять",
    "ударить":"👊 ударил(а)"
}


async def do_action(message, act):

    args = message.text.split()

    if len(args) < 2:
        await message.answer(
            "Укажи пользователя"
        )
        return

    await message.answer(
        f"{message.from_user.first_name} "
        f"{act} {args[1]}"
    )



@dp.message(Command("обнять"))
async def hug(message):
    await do_action(message,"🤗 обнял(а)")


@dp.message(Command("поцеловать"))
async def kiss(message):
    await do_action(message,"😘 поцеловал(а)")


@dp.message(Command("погладить"))
async def pat(message):
    await do_action(message,"😊 погладил(а)")


@dp.message(Command("дать_пять"))
async def highfive(message):
    await do_action(message,"🙌 дал(а) пять")


@dp.message(Command("ударить"))
async def hit(message):
    await do_action(message,"👊 ударил(а)")



@dp.message(Command("топ"))
async def top(message: types.Message):

    cur.execute(
        "SELECT name,coins FROM users ORDER BY coins DESC LIMIT 10"
    )

    users = cur.fetchall()

    text="🏆 ТОП игроков:\n\n"

    for i,u in enumerate(users,1):
        text += f"{i}. {u[0]} — 💰 {u[1]}\n"

    await message.answer(text)



@dp.message(Command("дать"))
async def give(message:types.Message):

    args = message.text.split()

    if len(args)<3:
        await message.answer(
            "Пример: /дать @user 50"
        )
        return

    amount=int(args[2])

    coins,_ = user_data(message.from_user)

    if coins < amount:
        await message.answer(
            "Недостаточно монет"
        )
        return

    add_money(
        message.from_user,
        -amount
    )

    await message.answer(
        f"💸 Передано {amount} монет {args[1]}"
    )

if __name__=="__main__":
    asyncio.run(main())