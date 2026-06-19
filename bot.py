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

cur.execute("""
CREATE TABLE IF NOT EXISTS items(
id INTEGER PRIMARY KEY AUTOINCREMENT,
user_id INTEGER,
item TEXT
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

@dp.message(Command("дуэль"))
async def duel(message: types.Message):

    args = message.text.split()

    if len(args) < 2:
        await message.answer(
            "⚔️ Напиши: /дуэль @user"
        )
        return

    win = random.choice([True, False])

    if win:
        add_money(message.from_user, 50)
        add_xp(message.from_user, 30)

        await message.answer(
            f"⚔️ {message.from_user.first_name} победил!\n"
            "💰 +50 монет\n"
            "⭐ +30 опыта"
        )

    else:
        add_money(message.from_user, -20)

        await message.answer(
            f"💀 {message.from_user.first_name} проиграл\n"
            "💰 -20 монет"
        )



@dp.message(Command("магазин"))
async def shop(message: types.Message):

    await message.answer(
        "🏪 Магазин:\n\n"
        "🐉 Дракон — 500 монет\n"
        "⚔️ Меч — 150 монет\n"
        "🍀 Талисман — 200 монет\n\n"
        "Покупка:\n"
        "/купить меч"
    )



@dp.message(Command("купить"))
async def buy(message: types.Message):

    args = message.text.split()

    if len(args)<2:
        await message.answer(
            "Что купить?"
        )
        return

    item=args[1]

    prices={
        "дракон":500,
        "меч":150,
        "талисман":200
    }

    if item not in prices:
        await message.answer(
            "Такого предмета нет"
        )
        return


    coins,_=user_data(message.from_user)

    if coins < prices[item]:
        await message.answer(
            "💸 Не хватает монет"
        )
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
async def inventory(message:types.Message):

    cur.execute(
        "SELECT item FROM items WHERE user_id=?",
        (message.from_user.id,)
    )

    items=cur.fetchall()


    if not items:
        await message.answer(
            "🎒 Инвентарь пуст"
        )
        return


    text="🎒 Твои вещи:\n"

    for i in items:
        text += f"• {i[0]}\n"


    await message.answer(text)

@dp.message(Command("help"))
async def help_cmd(message: types.Message):

    await message.answer(
        "📋 Команды бота:\n\n"
        "🤗 Общение:\n"
        "/обнять @user\n"
        "/поцеловать @user\n"
        "/погладить @user\n"
        "/дать_пять @user\n\n"
        "🎲 Развлечения:\n"
        "/кубик\n"
        "/монетка\n"
        "/шанс\n"
        "/шутка\n"
        "/факт\n"
        "/совет\n\n"
        "💰 Профиль:\n"
        "/профиль\n"
        "/баланс\n"
        "/работать\n"
        "/топ"
    )



@dp.message(Command("шутка"))
async def joke(message: types.Message):

    jokes = [
        "Почему программист пошёл в магазин? Потому что закончились баги 😄",
        "Компьютер не спит — он просто переходит в режим ожидания 😴",
        "Мой код работает. Не спрашивайте почему 😂"
    ]

    await message.answer(
        random.choice(jokes)
    )



@dp.message(Command("факт"))
async def fact(message: types.Message):

    facts = [
        "🐙 У осьминога три сердца.",
        "🦈 Акулы старше деревьев.",
        "🌎 Земля вращается быстрее, чем кажется."
    ]

    await message.answer(
        random.choice(facts)
    )



@dp.message(Command("совет"))
async def advice(message: types.Message):

    tips = [
        "💡 Не откладывай маленькие дела.",
        "💡 Учись чему-то понемногу каждый день.",
        "💡 Иногда лучший план — начать."
    ]

    await message.answer(
        random.choice(tips)
    )



@dp.message(Command("настроение"))
async def mood(message: types.Message):

    moods = [
        "😎 Отличное!",
        "😴 Сонное",
        "🔥 Боевой режим",
        "😂 Весёлое"
    ]

    await message.answer(
        random.choice(moods)
    )



@dp.message()
async def auto_reply(message: types.Message):

    text = message.text.lower()

    if "привет" in text:
        await message.answer(
            "👋 Привет!"
        )

    elif "как дела" in text:
        await message.answer(
            "🤖 Работаю, всё отлично!"
        )

    elif "спасибо" in text:
        await message.answer(
            "😊 Всегда пожалуйста"
        )


    db.commit()



@dp.message()
async def message_counter(message: types.Message):

    if message.from_user:
        add_message(message.from_user)



@dp.message(Command("стата"))
async def stats(message: types.Message):

    cur.execute(
        "SELECT messages FROM stats WHERE user_id=?",
        (message.from_user.id,)
    )

    data=cur.fetchone()

    count=data[0] if data else 0

    await message.answer(
        f"📊 Твоя статистика:\n"
        f"💬 Сообщений: {count}"
    )



# ===== НОВЫЕ РЕАКЦИИ =====


@dp.message(Command("пожалеть"))
async def pity(message: types.Message):

    args=message.text.split()

    if len(args)<2:
        await message.answer(
            "Кого пожалеть?"
        )
        return

    await message.answer(
        f"🥺 {message.from_user.first_name} пожалел(а) {args[1]}"
    )



@dp.message(Command("пожатьруку"))
async def hand(message: types.Message):

    args=message.text.split()

    if len(args)<2:
        return

    await message.answer(
        f"🤝 {message.from_user.first_name} пожал руку {args[1]}"
    )



@dp.message(Command("ржать"))
async def laugh(message: types.Message):

    args=message.text.split()

    if len(args)<2:
        return

    await message.answer(
        f"😂 {message.from_user.first_name} смеётся вместе с {args[1]}"
    )



@dp.message(Command("обидеться"))
async def angry(message: types.Message):

    await message.answer(
        "😤 Я обиделся... но ненадолго"
    )

if __name__=="__main__":
    asyncio.run(main())

# ===== СТАТИСТИКА =====

cur.execute("""
CREATE TABLE IF NOT EXISTS stats(
user_id INTEGER PRIMARY KEY,
messages INTEGER DEFAULT 0
)
""")

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

    db.commit()



@dp.message(Command("стата"))
async def stats(message: types.Message):

    cur.execute(
        "SELECT messages FROM stats WHERE user_id=?",
        (message.from_user.id,)
    )

    data = cur.fetchone()

    count = data[0] if data else 0

    await message.answer(
        f"📊 Твоя статистика:\n💬 Сообщений: {count}"
    )



@dp.message(Command("пожалеть"))
async def pity(message: types.Message):

    args = message.text.split()

    if len(args) < 2:
        await message.answer("Кого пожалеть?")
        return

    await message.answer(
        f"🥺 {message.from_user.first_name} пожалел(а) {args[1]}"
    )



@dp.message(Command("пожатьруку"))
async def hand(message: types.Message):

    args = message.text.split()

    if len(args) < 2:
        await message.answer("Кого?")
        return

    await message.answer(
        f"🤝 {message.from_user.first_name} пожал руку {args[1]}"
    )



@dp.message(Command("ржать"))
async def laugh(message: types.Message):

    args = message.text.split()

    if len(args) < 2:
        await message.answer("Кого?")
        return

    await message.answer(
        f"😂 {message.from_user.first_name} смеётся вместе с {args[1]}"
    )



@dp.message(Command("обидеться"))
async def angry(message: types.Message):

    await message.answer(
        "😤 Я обиделся... но уже нормально"
    )



# АВТООТВЕТЫ ДОЛЖНЫ БЫТЬ САМЫМИ ПОСЛЕДНИМИ

@dp.message()
async def auto_reply(message: types.Message):

    if message.from_user:
        add_message(message.from_user)

    if not message.text:
        return

    text = message.text.lower()

    if "привет" in text:
        await message.answer("👋 Привет!")

    elif "как дела" in text:
        await message.answer("🤖 Работаю, всё отлично!")

    elif "спасибо" in text:
        await message.answer("😊 Всегда пожалуйста")


if __name__=="__main__":
    asyncio.run(main())