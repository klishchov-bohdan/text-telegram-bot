from filters import IsPrivate
from utils.misc import rate_limit
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from data import config
from loader import dp


@rate_limit(limit=3)
@dp.message_handler(IsPrivate(), CommandStart())
async def command_start(message: types.Message):
    await message.answer('hello')
