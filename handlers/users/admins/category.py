from filters import IsPrivate, IsAdmin
from states.category import AddCategory, UpdateCategory, DeleteCategory
from utils.db_api import category_commands, file_commands
from utils.misc import rate_limit
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import CommandStart, Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from keyboards.inline import cancel_add_category as cac_kb
from keyboards.inline import admin_categories_menu as acm_kb

from data import config
from loader import dp


@rate_limit(limit=3)
@dp.message_handler(IsPrivate(), IsAdmin(), Command('categories'))
async def command_categories(message: types.Message):
    await message.answer('Выберите действие с категориями: ', reply_markup=acm_kb)


@rate_limit(limit=3)
@dp.callback_query_handler(IsAdmin(), text='add_category')
async def new_category(call: types.CallbackQuery):
    await call.message.delete()
    await call.message.answer('Введите название категории: ', reply_markup=cac_kb)
    await AddCategory.name.set()


@rate_limit(limit=3)
@dp.callback_query_handler(IsAdmin(), text='cancel_add_category', state=AddCategory.states)
async def cancel_add(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete()
    await state.finish()
    await call.message.answer('Отменено')


@rate_limit(limit=3)
@dp.message_handler(IsPrivate(), IsAdmin(), state=AddCategory.name)
async def new_category_name(message: types.Message, state: FSMContext):
    answer = message.text
    await state.update_data(name=answer)
    try:
        categories = await category_commands.get_all_categories()
        if answer in [category.category_name for category in categories]:
            await message.answer('Такая категория уже существует. Пожалуйста, введите другое название: ')
        else:
            await category_commands.add_category(answer)
            await message.answer('Категория успешно добавлена')
            await state.finish()
    except Exception as ex:
        print(ex)
        await message.answer('Что-то пошло не так при добавлении категории')
        await state.finish()


@rate_limit(limit=3)
@dp.callback_query_handler(IsAdmin(), text='update_category')
async def update_category(call: types.CallbackQuery):
    await call.message.delete()
    try:
        categories = await category_commands.get_all_categories()
        if len(categories) > 0:
            inline_category_kb = InlineKeyboardMarkup(row_width=2, resize_keyboard=True,
                                                      one_time_keyboard=True, inline_keyboard=[])
            for category in categories:
                inline_category_kb.inline_keyboard.append([InlineKeyboardButton(text=f'{category.category_name}',
                                                                                callback_data=f'{category.category_name}')])
            inline_category_kb.inline_keyboard.append([InlineKeyboardButton(text='Отменить',
                                                                            callback_data='cancel_update_category')])
            await call.message.answer('Выберите одну из категорий для изменения названия',
                                      reply_markup=inline_category_kb)
            await UpdateCategory.name.set()
        else:
            await call.message.answer('Нет категорий для изменения')
    except Exception as ex:
        await call.message.answer('Что-то пошло не так')
        print(ex)


@rate_limit(limit=3)
@dp.callback_query_handler(IsAdmin(), text='cancel_update_category', state=UpdateCategory.name)
async def cancel_update(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete()
    await state.finish()
    await call.message.answer('Отменено')


@rate_limit(limit=3)
@dp.callback_query_handler(state=UpdateCategory.name)
async def get_update_category(call: CallbackQuery, state: FSMContext):
    await call.message.delete()
    try:
        categories = await category_commands.get_all_categories()
        if call.data in [category.category_name for category in categories]:
            await state.update_data(name=call.data)
            await call.message.answer('Введите новое название категории:')
            await UpdateCategory.new_name.set()
        else:
            await call.message.answer('Такой категории не сещуствует')
    except Exception as ex:
        print(ex)
        await call.message.answer('Что-то пошло не так при изменении категории')
        await state.finish()


@rate_limit(limit=3)
@dp.message_handler(IsPrivate(), IsAdmin(), state=UpdateCategory.new_name)
async def update_category_name(message: types.Message, state: FSMContext):
    answer = message.text
    await state.update_data(new_name=answer)
    try:
        data = await state.get_data()
        name = data.get('name')
        new_name = data.get('new_name')
        await category_commands.update_category_name(name, new_name)
        await file_commands.update_files_category(name, new_name)
        await message.answer('Категория успешно изменена')
        await state.finish()
    except Exception as ex:
        print(ex)
        await message.answer('Что-то пошло не так при добавлении категории')
        await state.finish()


@rate_limit(limit=3)
@dp.callback_query_handler(IsAdmin(), text='delete_category')
async def delete_category(call: types.CallbackQuery):
    await call.message.delete()
    try:
        categories = await category_commands.get_all_categories()
        if len(categories) > 0:
            inline_category_kb = InlineKeyboardMarkup(row_width=2, resize_keyboard=True,
                                                      one_time_keyboard=True, inline_keyboard=[])
            for category in categories:
                inline_category_kb.inline_keyboard.append([InlineKeyboardButton(text=f'{category.category_name}',
                                                                                callback_data=f'{category.category_name}')])
            inline_category_kb.inline_keyboard.append([InlineKeyboardButton(text='Отменить',
                                                                            callback_data='cancel_delete_category')])
            await call.message.answer('Выберите одну из категорий для удаления',
                                      reply_markup=inline_category_kb)
            await DeleteCategory.name.set()
        else:
            await call.message.answer('Нет категорий для удаления')
    except Exception as ex:
        await call.message.answer('Что-то пошло не так')
        print(ex)


@rate_limit(limit=3)
@dp.callback_query_handler(IsAdmin(), text='cancel_delete_category', state=DeleteCategory.name)
async def cancel_delete(call: types.CallbackQuery, state: FSMContext):
    await call.message.delete()
    await state.finish()
    await call.message.answer('Отменено')


@rate_limit(limit=3)
@dp.callback_query_handler(state=DeleteCategory.name)
async def delete_category_name(call: CallbackQuery, state: FSMContext):
    await call.message.delete()
    try:
        if call.data == 'Неопределено':
            raise ValueError(f'Категория {call.data} не может быть удалена')
        categories = await category_commands.get_all_categories()
        if call.data in [category.category_name for category in categories]:
            await state.update_data(name=call.data)
            await category_commands.delete_category(call.data)
            if 'Неопределено' not in [category.category_name for category in categories]:
                await category_commands.add_category('Неопределено')
            await file_commands.update_files_category(call.data, 'Неопределено')
            await call.message.answer('Категория успешно удалена')
        else:
            await call.message.answer('Такой категории не сещуствует')
    except ValueError as ex:
        print(ex)
        await call.message.answer('Данная категория не может быть удалена')
    except Exception as ex:
        print(ex)
        await call.message.answer('Что-то пошло не так при удалении категории')
    finally:
        await state.finish()
