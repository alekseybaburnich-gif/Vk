from vkbottle import Bot, Message
import random

TOKEN = "ТОКЕН_ВАШЕГО_СООБЩЕСТВА"

bot = Bot(token=TOKEN)

hug_phrases = [
    "🤗 {user} крепко обнял(а) {target}!",
    "❤️ {user} тепло обнял(а) {target}!",
    "😊 {user} заключил(а) {target} в объятия!"
]

hit_phrases = [
    "💥 {user} ударил(а) {target} подушкой!",
    "🥊 {user} слегка стукнул(а) {target}!",
    "⚡ {user} устроил(а) дружеский удар по {target}!"
]


@bot.on.message(text="/обнять <target>")
async def hug(message: Message, target: str):
    user = message.from_id
    phrase = random.choice(hug_phrases)

    await message.answer(
        phrase.format(
            user=f"[id{user}|Пользователь]",
            target=target
        )
    )


@bot.on.message(text="/ударить <target>")
async def hit(message: Message, target: str):
    user = message.from_id
    phrase = random.choice(hit_phrases)

    await message.answer(
        phrase.format(
            user=f"[id{user}|Пользователь]",
            target=target
        )
    )


bot.run_forever()
