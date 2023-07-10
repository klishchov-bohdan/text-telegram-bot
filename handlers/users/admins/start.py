from filters import IsPrivate, IsAdmin
from utils.misc import rate_limit
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from data import config
from loader import dp, bot


@rate_limit(limit=3)
@dp.message_handler(IsPrivate(), IsAdmin(), CommandStart())
async def command_start_admin(message: types.Message):
    await message.answer('hello, admin')
