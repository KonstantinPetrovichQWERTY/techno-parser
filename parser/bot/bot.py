import asyncio
import logging
from os import getenv
from datetime import datetime, timedelta

import requests
from parser.services.parser import start_parsing_process
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    filename="parser_logs.log",
    encoding='utf-8',
)

last_command_time = {}
COMMAND_COOLDOWN = 600

TOKEN = getenv('TELEGRAM_BOT_TOKEN')

dp = Dispatcher()


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    kb = [
        [KeyboardButton(text="/update"),
         KeyboardButton(text='/random_dog')],
    ]
    keyboard = ReplyKeyboardMarkup(keyboard=kb, 
                                   resize_keyboard=True, 
                                   input_field_placeholder='не пишите тут ничего')
    
    await message.answer(f'Привет, {message.from_user.full_name}!\nКоманда "/update" позволяет внепланово запустить парсер', reply_markup=keyboard)


@dp.message(Command('update'))
async def update_handler(message: Message) -> None:
    await message.reply('опять работать. \nух сейчас как разойдусь. подожди-ка пару минут')

    user_id = message.from_user.id
    current_time = datetime.now()

    if user_id in last_command_time:
        elapsed_time = (current_time - last_command_time[user_id]).total_seconds()
        if elapsed_time < COMMAND_COOLDOWN:
            remaining_time = COMMAND_COOLDOWN - elapsed_time
            await message.reply(f"А нееет. У меня перерыв на обед.\nПодожди {int(remaining_time // 60)} минут")
            return

    last_command_time[user_id] = current_time

    await message.reply(start_parsing_process())



@dp.message(Command('random_dog'))
async def random_dog_handler(message: Message) -> None:
    url = 'https://random.dog/woof.json'
    content = requests.get(url).json()
    picture_url = content['url']
    await message.answer_photo(photo=picture_url)


@dp.message()
async def echo_handler(message: Message) -> None:
    await message.reply("ну ёпрст!")


async def main() -> None:
    bot = Bot(token=TOKEN)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
