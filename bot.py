import os

from enum import Enum

from pydantic import BaseModel
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import Bot, Dispatcher, executor, types
from decouple import config

from api_handler import search, get_magnet

storage = MemoryStorage()
bot = Bot(token=config("TOKEN"))
dp = Dispatcher(bot=bot, storage=storage)


class MessageModel(BaseModel):
    start: str
    search_button_template: str
    search: str
    results: str
    no_results: str
    link: str


class Constants(Enum):
    absolute_path = os.path.dirname(__file__)
    MESSAGE_FILE = os.path.join(absolute_path, "templates/messages.json")
    torrentId = "torrentId"
    magnetLink = "Magnet link"


MESSAGES = MessageModel.parse_file(Constants.MESSAGE_FILE.value)


def search_keyboard(search_results: list):
    """Creates inline keyboard with buttons for search results."""
    search_keyboard = InlineKeyboardMarkup(resize_keyboard=True)
    for line in search_results:
        button_text = MESSAGES.search_button_template.format(*line.values())
        callback_data = line.get(Constants.torrentId.value)
        line_button = InlineKeyboardButton(
            text=button_text, callback_data=callback_data
        )
        search_keyboard.add(line_button)
    return search_keyboard


def magnet_keyboard(magnetLink: str):
    """Creates inline button for the magnet link."""
    magnet_keyboard = InlineKeyboardMarkup(resize_keyboard=True)
    button_text = Constants.magnetLink.value
    magnet_button = InlineKeyboardButton(text=button_text, url=magnetLink)
    magnet_keyboard.add(magnet_button)
    return magnet_keyboard


@dp.message_handler(commands=["start"])
async def start_handler(message: types.Message):
    """Handles the /start command. Welcomes the user and generates main menu
    keyboard."""
    await bot.send_message(
        message.from_user.id,
        MESSAGES.start.format(message.from_user.first_name),
        parse_mode="MarkdownV2",
    )


@dp.callback_query_handler(lambda callback_query: True)
async def process_callback_button(callback_query: types.CallbackQuery):
    """Catches the torrendId from the callback query and generates inline
    button with magnet link."""
    torrentId = callback_query.data
    magnetLink = get_magnet(torrentId)
    await bot.send_message(
        callback_query.from_user.id,
        MESSAGES.link,
        reply_markup=magnet_keyboard(magnetLink),
        parse_mode="MarkdownV2",
    )


@dp.message_handler()
async def results_handler(message: types.Message):
    """Finishes the Search state for the bot and sends results as inline
    buttons."""
    search_query = message.text
    search_results = search(search_query)

    if not search_results:
        await bot.send_message(
            message.from_user.id,
            MESSAGES.no_results,
            parse_mode="MarkdownV2",
        )
    else:
        await bot.send_message(
            message.from_user.id,
            MESSAGES.results,
            reply_markup=search_keyboard(search_results),
            parse_mode="MarkdownV2",
        )


if __name__ == "__main__":
    executor.start_polling(dp)
