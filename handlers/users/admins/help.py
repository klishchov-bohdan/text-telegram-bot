from filters import IsPrivate, IsAdmin
from utils.misc import rate_limit
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import CommandHelp
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from data import config
from loader import dp


@rate_limit(limit=3)
@dp.message_handler(IsPrivate(), IsAdmin(), CommandHelp())
async def command_help_admin(message: types.Message):
    await message.answer('help admin')
