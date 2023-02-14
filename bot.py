import os

from enum import Enum

from pydantic import BaseModel
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import Bot, Dispatcher, executor, types
from decouple import config

from api_handler import search, get_magnet

storage = MemoryStorage()
bot = Bot(token=config('TOKEN'))
dp = Dispatcher(bot=bot, storage=storage)


class Form(StatesGroup):
    search = State()


class MessageModel(BaseModel):
    start: str
    search_button_template: str
    search: str
    results: str
    link: str


class Constants(Enum):
    absolute_path = os.path.dirname(__file__)
    MESSAGE_FILE = os.path.join(absolute_path, "templates/messages.json")
    torrentId = "torrentId"
    magnetLink = 'Magnet link'


MESSAGES = MessageModel.parse_file(Constants.MESSAGE_FILE.value)


def search_keyboard(search_results: list):
    """Creates inline keyboard with buttons for search results."""
    search_keyboard = InlineKeyboardMarkup(resize_keyboard=True)
    for line in search_results:
        button_text = MESSAGES.search_button_template.format(*line.values())
        callback_data = line.get(Constants.torrentId.value)
        line_button = InlineKeyboardButton(text=button_text,
                                           callback_data=callback_data)
        search_keyboard.add(line_button)
    return search_keyboard


def magnet_keyboard(magnetLink: str):
    """Creates inline button for the magnet link."""
    magnet_keyboard = InlineKeyboardMarkup(resize_keyboard=True)
    button_text = Constants.magnetLink.value
    magnet_button = InlineKeyboardButton(text=button_text, url=magnetLink)
    magnet_keyboard.add(magnet_button)
    return magnet_keyboard


def main_keyboard():
    """Creates main menu buttons."""
    search_button = KeyboardButton('Search')
    mainmenu = ReplyKeyboardMarkup(resize_keyboard=True).add(search_button)
    return mainmenu


@dp.message_handler(state=None, commands=['start'])
async def start_handler(message: types.Message):
    """Handles the /start command. Welcomes the user and generates main menu
    keyboard."""
    await bot.send_message(message.from_user.id, MESSAGES.start.format(
        message.from_user.first_name), reply_markup=main_keyboard(),
                           parse_mode='MarkdownV2')


@dp.callback_query_handler(lambda callback_query: True)
async def process_callback_button(callback_query: types.CallbackQuery):
    """Catches the torrendId from the callback query and generates inline
    button with magnet link."""
    torrentId = callback_query.data
    magnetLink = get_magnet(torrentId)
    await bot.send_message(callback_query.from_user.id, MESSAGES.link,
                           reply_markup=magnet_keyboard(magnetLink),
                           parse_mode="MarkdownV2")


@dp.message_handler(state=None, text="Search")
async def search_handler(message: types.Message):
    """Handles the Search button in main menu. Starts searching proccess and
    creates the State for the bot."""
    await bot.send_message(message.from_user.id,
                           MESSAGES.search, parse_mode="MarkdownV2")
    await Form.search.set()


@dp.message_handler(state=Form.search)
async def results_handler(message: types.Message, state: FSMContext):
    """Finishes the Search state for the bot and sends results as inline
    buttons."""
    search_query = message.text
    search_results = search(search_query)
    await bot.send_message(message.from_user.id, MESSAGES.results,
                           reply_markup=search_keyboard(search_results),
                           parse_mode="MarkdownV2")
    await state.finish()


if __name__ == "__main__":
    executor.start_polling(dp)
