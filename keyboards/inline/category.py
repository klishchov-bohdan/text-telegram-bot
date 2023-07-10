from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

cancel_add_category = InlineKeyboardMarkup(row_width=2,
                                           resize_keyboard=True,
                                           one_time_keyboard=True,
                                           inline_keyboard=[
                                               [
                                                   InlineKeyboardButton(text='Отменить',
                                                                        callback_data='cancel_add_category'),
                                               ]
                                           ])

admin_categories_menu = InlineKeyboardMarkup(row_width=2,
                                             resize_keyboard=True,
                                             one_time_keyboard=True,
                                             inline_keyboard=[
                                                 [
                                                     InlineKeyboardButton(text='Добавить категорию',
                                                                          callback_data='add_category'),
                                                 ],
                                                 [
                                                     InlineKeyboardButton(text='Изменить категорию',
                                                                          callback_data='update_category'),
                                                 ],
                                                 [
                                                     InlineKeyboardButton(text='Удалить категорию',
                                                                          callback_data='delete_category'),
                                                 ],
                                                 [
                                                     InlineKeyboardButton(text='Все категории',
                                                                          callback_data='all_categories'),
                                                 ],
                                                 [
                                                     InlineKeyboardButton(text='Отменить',
                                                                          callback_data='cancel_categories_menu'),
                                                 ]
                                             ])

categories_menu = InlineKeyboardMarkup(row_width=2,
                                       resize_keyboard=True,
                                       one_time_keyboard=True,
                                       inline_keyboard=[
                                           [
                                               InlineKeyboardButton(text='Все категории',
                                                                    callback_data='all_categories'),
                                           ],
                                           [
                                               InlineKeyboardButton(text='Отменить',
                                                                    callback_data='cancel_categories_menu'),
                                           ]
                                       ])
