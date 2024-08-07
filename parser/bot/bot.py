import asyncio
import logging
from os import getenv

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

TOKEN = getenv('TELEGRAM_BOT_TOKEN')

dp = Dispatcher()


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    kb = [
        [KeyboardButton(text="/update")],
    ]
    keyboard = ReplyKeyboardMarkup(keyboard=kb)
    await message.answer(f'Привет, {message.from_user.full_name}!\nКоманда "/update" позволяет внепланово запустить парсер', reply_markup=keyboard)


@dp.message(Command('update'))
async def run_parsing(message: Message) -> None:
    await message.reply('опять работать')
    await message.reply(start_parsing_process())


@dp.message()
async def echo_handler(message: Message) -> None:
    await message.reply("ну ёпрст!")


async def main() -> None:
    bot = Bot(token=TOKEN)

    await dp.start_polling(bot, skip_updates=True)


if __name__ == "__main__":
    asyncio.run(main())
