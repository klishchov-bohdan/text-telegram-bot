from aiogram import types

from filters import IsPrivate
from loader import dp


@dp.message_handler()
async def command_not_exists(message: types.Message):
    await message.answer(f'Command {message.text} is not exists')


@dp.message_handler(IsPrivate(), state='*', content_types=types.ContentType.ANY)
async def invalid_message(message: types.Message):
    await message.delete()
