from vkbottle import Bot, Message
import random
import os

TOKEN = os.getenv("TOKEN")

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
phrase = random.choice(hug_phrases)

await message.answer(
    phrase.format(
        user=f"[id{message.from_id}|Пользователь]",
        target=target
    )
)

@bot.on.message(text="/ударить <target>")
async def hit(message: Message, target: str):
phrase = random.choice(hit_phrases)

await message.answer(
    phrase.format(
        user=f"[id{message.from_id}|Пользователь]",
        target=target
    )
)

bot.run_forever()
