from filters import IsPrivate, IsAdmin
from states.category import Category
from utils.misc import rate_limit
from aiogram import types
from utils.db_api import category_commands, file_commands
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import CommandStart, Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from keyboards.inline import categories_menu as cm_kb

from data import config
from loader import dp


@rate_limit(limit=3)
@dp.message_handler(IsPrivate(), Command('categories'))
async def command_categories(message: types.Message):
    await message.answer('Выберите действие с категориями: ', reply_markup=cm_kb)


@dp.callback_query_handler(text='cancel_categories_menu')
async def cancel_categories_menu(call: CallbackQuery):
    await call.message.delete()
    await call.message.answer('Отменено')


@dp.callback_query_handler(text='all_categories')
async def all_categories(call: CallbackQuery):
    await call.message.delete()
    try:
        categories = await category_commands.get_all_categories()
        inline_category_kb = InlineKeyboardMarkup(row_width=2, resize_keyboard=True,
                                                  one_time_keyboard=True, inline_keyboard=[])
        for category in categories:
            inline_category_kb.inline_keyboard.append([InlineKeyboardButton(text=f'{category.category_name}',
                                                                            callback_data=f'{category.category_name}')])
        inline_category_kb.inline_keyboard.append([InlineKeyboardButton(text='Отменить',
                                                                        callback_data='cancel_get_category')])
        await call.message.answer('Выберите одну из категорий для получения списка имеющихся текстов',
                                  reply_markup=inline_category_kb)
        await Category.name.set()
    except Exception as ex:
        await call.message.answer('Что-то пошло не так')
        print(ex)


@dp.callback_query_handler(text='cancel_get_category', state=Category.name)
async def cancel(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete()
    await state.finish()
    await call.message.answer('Отменено')


@dp.callback_query_handler(state=Category.name)
async def get_category(call: CallbackQuery, state: FSMContext):
    await call.message.delete()
    try:
        categories = await category_commands.get_all_categories()
        if call.data in [category.category_name for category in categories]:
            answer = call.data
            files = await file_commands.get_files_by_category(answer)
            if len(files) > 0:
                msg = ''
                for file in files:
                    msg = msg + f'Название файла: {file.file_name}\n' \
                                f'Описание: {file.file_description}\n\n'
                await call.message.answer(msg)
            else:
                await call.message.answer('Файлов в данной категории пока не существует')
            await state.finish()
        else:
            await call.message.answer('Вы должны выбрать категорию')
    except Exception as ex:
        await call.message.answer('Что-то пошло не так')
        print(ex)
        await state.finish()

