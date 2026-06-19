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


cur.execute("""
CREATE TABLE IF NOT EXISTS items(
id INTEGER PRIMARY KEY AUTOINCREMENT,
user_id INTEGER,
item TEXT
)
""")


cur.execute("""
CREATE TABLE IF NOT EXISTS stats(
user_id INTEGER PRIMARY KEY,
messages INTEGER DEFAULT 0
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




def add_message(user):

    cur.execute(
        "INSERT OR IGNORE INTO stats(user_id) VALUES(?)",
        (user.id,)
    )

    cur.execute(
        "UPDATE stats SET messages=messages+1 WHERE user_id=?",
        (user.id,)
    )

    add_xp(
        user,
        random.randint(1,5)
    )

    db.commit()



@dp.message(Command("start"))
async def start(message:types.Message):

    user_add(message.from_user)

    await message.answer(
        "🔥 Бот запущен!\n\n"
        "/профиль\n"
        "/работать\n"
        "/кубик\n"
        "/магазин\n"
        "/help"
    )



@dp.message(Command("профиль"))
async def profile(message):

    coins,xp=user_data(message.from_user)

    await message.answer(
        f"👤 {message.from_user.first_name}\n"
        f"💰 {coins}\n"
        f"⭐ {xp}\n"
        f"🏆 Уровень {xp//100+1}"
    )



@dp.message(Command("баланс"))
async def balance(message):

    coins,_=user_data(message.from_user)

    await message.answer(
        f"💰 Баланс: {coins}"
    )



@dp.message(Command("работать"))
async def work(message):

    cur.execute(
        "SELECT last_work FROM users WHERE id=?",
        (message.from_user.id,)
    )

    last=cur.fetchone()[0]

    now=int(time.time())

    if now-last < 60:
        await message.answer("⏳ Подожди минуту")
        return


    reward=random.randint(20,100)

    add_money(message.from_user,reward)
    add_xp(message.from_user,20)


    cur.execute(
        "UPDATE users SET last_work=? WHERE id=?",
        (now,message.from_user.id)
    )

    db.commit()


    await message.answer(
        f"🛠 Работа\n💰 +{reward}"
    )



@dp.message(Command("кубик"))
async def dice(message):

    await message.answer(
        f"🎲 {random.randint(1,6)}"
    )


@dp.message(Command("монетка"))
async def coin(message):

    await message.answer(
        random.choice(["🪙 Орёл","🪙 Решка"])
    )
@dp.message(Command("шанс"))
async def chance(message):

    await message.answer(
        f"🎯 Шанс: {random.randint(0,100)}%"
    )



@dp.message(Command("топ"))
async def top(message):

    cur.execute(
        "SELECT name,coins FROM users ORDER BY coins DESC LIMIT 10"
    )

    users=cur.fetchall()

    text="🏆 ТОП:\n\n"

    for i,u in enumerate(users,1):
        text+=f"{i}. {u[0]} — {u[1]}💰\n"

    await message.answer(text)



@dp.message(Command("магазин"))
async def shop(message):

    await message.answer(
        "🏪 Магазин:\n"
        "⚔️ меч — 150\n"
        "🐉 дракон — 500\n"
        "🍀 талисман — 200\n\n"
        "/купить меч"
    )



@dp.message(Command("купить"))
async def buy(message):

    args=message.text.split()

    if len(args)<2:
        return

    prices={
        "меч":150,
        "дракон":500,
        "талисман":200
    }

    item=args[1]

    if item not in prices:
        await message.answer("Нет такого")
        return


    coins,_=user_data(message.from_user)

    if coins < prices[item]:
        await message.answer("💸 Не хватает")
        return


    add_money(
        message.from_user,
        -prices[item]
    )


    cur.execute(
        "INSERT INTO items(user_id,item) VALUES(?,?)",
        (message.from_user.id,item)
    )

    db.commit()


    await message.answer(
        f"🎁 Куплено: {item}"
    )



@dp.message(Command("инвентарь"))
async def inv(message):

    cur.execute(
        "SELECT item FROM items WHERE user_id=?",
        (message.from_user.id,)
    )

    items=cur.fetchall()

    if not items:
        await message.answer("🎒 Пусто")
        return


    text="🎒 Вещи:\n"

    for i in items:
        text+=f"• {i[0]}\n"

    await message.answer(text)



async def action(message,word):

    args=message.text.split()

    if len(args)<2:
        await message.answer("Кого?")
        return

    await message.answer(
        f"{message.from_user.first_name} {word} {args[1]}"
    )



@dp.message(Command("обнять"))
async def hug(message):
    await action(message,"🤗 обнял(а)")



@dp.message(Command("пожалеть"))
async def pity(message):
    await action(message,"🥺 пожалел(а)")



@dp.message(Command("ржать"))
async def laugh(message):
    await action(message,"😂 смеётся с")



@dp.message(Command("стата"))
async def stats(message):

    cur.execute(
        "SELECT messages FROM stats WHERE user_id=?",
        (message.from_user.id,)
    )

    data=cur.fetchone()

    await message.answer(
        f"📊 Сообщений: {data[0] if data else 0}"
    )



@dp.message(Command("help"))
async def help_cmd(message):

    await message.answer(
        "📋 Команды:\n\n"
        "/профиль\n"
        "/работать\n"
        "/магазин\n"
        "/купить\n"
        "/инвентарь\n"
        "/кубик\n"
        "/обнять\n"
        "/стата"
    )

@dp.message(Command("уровень"))
async def level(message: types.Message):

    coins,xp = user_data(message.from_user)

    lvl = xp // 100 + 1

    await message.answer(
        f"⭐ {message.from_user.first_name}\n"
        f"Опыт: {xp}\n"
        f"Уровень: {lvl}"
    )

@dp.message()
async def all_messages(message):

    if message.from_user:
        add_message(message.from_user)

    if not message.text:
        return

    text = message.text.lower()

    if "привет" in text:
        await message.answer("👋 Привет!")

    elif "как дела" in text:
        await message.answer("🤖 Работаю 😎")

    elif "спасибо" in text:
        await message.answer("😊 Пожалуйста")

    elif "жиза" in text:
        await message.answer("😎 Жиза")

    elif "имба" in text:
        await message.answer("🔥 Имба!")

    elif "лол" in text:
        await message.answer("😂😂")

    elif "кек" in text:
        await message.answer("🤣")


async def main():
    await dp.start_polling(bot)


if __name__=="__main__":
    asyncio.run(main())