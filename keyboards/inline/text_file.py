from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

cancel_add_file = InlineKeyboardMarkup(row_width=2,
                                       resize_keyboard=True,
                                       one_time_keyboard=True,
                                       inline_keyboard=[
                                           [
                                               InlineKeyboardButton(text='Отменить',
                                                                    callback_data='cancel_add_file'),
                                           ]
                                       ])

admin_files_menu = InlineKeyboardMarkup(row_width=2,
                                        resize_keyboard=True,
                                        one_time_keyboard=True,
                                        inline_keyboard=[
                                            [
                                                InlineKeyboardButton(text='Добавить файл',
                                                                     callback_data='add_file'),
                                            ],
                                            [
                                                InlineKeyboardButton(text='Изменить/удалить файлы',
                                                                     callback_data='edit_files'),
                                            ],
                                            [
                                                InlineKeyboardButton(text='Все файлы',
                                                                     callback_data='all_files'),
                                            ],
                                            [
                                                InlineKeyboardButton(text='Файлы по категориям',
                                                                     callback_data='files_by_category'),
                                            ],
                                            [
                                                InlineKeyboardButton(text='Отменить',
                                                                     callback_data='cancel_files_menu'),
                                            ]
                                        ])

files_menu = InlineKeyboardMarkup(row_width=2,
                                  resize_keyboard=True,
                                  one_time_keyboard=True,
                                  inline_keyboard=[
                                      [
                                          InlineKeyboardButton(text='Все файлы',
                                                               callback_data='all_files'),
                                      ],
                                      [
                                          InlineKeyboardButton(text='Файлы по категориям',
                                                               callback_data='files_by_category'),
                                      ],
                                  ])

file_send_menu = InlineKeyboardMarkup(row_width=2,
                                      resize_keyboard=True,
                                      one_time_keyboard=True,
                                      inline_keyboard=[
                                          [
                                              InlineKeyboardButton(text='Предыдущий',
                                                                   callback_data='send_prev_file'),
                                              InlineKeyboardButton(text='Следующий',
                                                                   callback_data='send_next_file'),
                                          ],
                                          [
                                              InlineKeyboardButton(text='Сортировка',
                                                                   callback_data='send_sorted_documents'),
                                          ],
                                          [
                                              InlineKeyboardButton(text='Отмена',
                                                                   callback_data='cancel_send_files'),
                                          ],
                                      ])

admin_files_edit_menu = InlineKeyboardMarkup(row_width=2,
                                             resize_keyboard=True,
                                             one_time_keyboard=True,
                                             inline_keyboard=[
                                                 [
                                                     InlineKeyboardButton(text='Предыдущий',
                                                                          callback_data='admin_send_prev_file'),
                                                     InlineKeyboardButton(text='Следующий',
                                                                          callback_data='admin_send_next_file'),
                                                 ],
                                                 [
                                                     InlineKeyboardButton(text='Сортировка',
                                                                          callback_data='send_sorted_documents_edit'),
                                                 ],
                                                 [
                                                     InlineKeyboardButton(text='Редактировать',
                                                                          callback_data='admin_edit_selected_file'),
                                                 ],
                                                 [
                                                     InlineKeyboardButton(text='Удалить',
                                                                          callback_data='admin_delete_selected_file'),
                                                 ],
                                                 [
                                                     InlineKeyboardButton(text='Отмена',
                                                                          callback_data='admin_cancel_edit_files_menu'),
                                                 ],
                                             ])

file_edit_menu = InlineKeyboardMarkup(row_width=2,
                                      resize_keyboard=True,
                                      one_time_keyboard=True,
                                      inline_keyboard=[
                                          [
                                              InlineKeyboardButton(text='Название',
                                                                   callback_data='admin_edit_file_name'),
                                          ],
                                          [
                                              InlineKeyboardButton(text='Описание',
                                                                   callback_data='admin_edit_file_description'),
                                          ],
                                          [
                                              InlineKeyboardButton(text='Категория',
                                                                   callback_data='admin_edit_file_category'),
                                          ],
                                          [
                                              InlineKeyboardButton(text='Заменить файл',
                                                                   callback_data='admin_edit_file_document'),
                                          ],
                                          [
                                              InlineKeyboardButton(text='Отмена',
                                                                   callback_data='admin_cancel_edit_file'),
                                          ],
                                      ])

file_edit_delete_cancel = InlineKeyboardMarkup(row_width=2,
                                               resize_keyboard=True,
                                               one_time_keyboard=True,
                                               inline_keyboard=[
                                                   [
                                                       InlineKeyboardButton(text='Отменить',
                                                                            callback_data='admin_edit_delete_file_cancel'),
                                                   ],
                                               ])

sorting_files_menu = InlineKeyboardMarkup(row_width=2,
                                          resize_keyboard=True,
                                          one_time_keyboard=True,
                                          inline_keyboard=[
                                              [
                                                  InlineKeyboardButton(text='Сортировка от А до Я',
                                                                       callback_data='alphabetically_sorting'),
                                              ],
                                              [
                                                  InlineKeyboardButton(text='Сортировка от Я до А',
                                                                       callback_data='alphabetically_sorting_reverse'),
                                              ],
                                          ])

sorting_edit_files_menu = InlineKeyboardMarkup(row_width=2,
                                               resize_keyboard=True,
                                               one_time_keyboard=True,
                                               inline_keyboard=[
                                                   [
                                                       InlineKeyboardButton(text='Сортировка от А до Я',
                                                                            callback_data='alphabetically_sorting_edit'),
                                                   ],
                                                   [
                                                       InlineKeyboardButton(text='Сортировка от Я до А',
                                                                            callback_data='alphabetically_sorting_reverse_edit'),
                                                   ],
                                               ])

# cancel_searching_text = InlineKeyboardMarkup(row_width=2,
#                                              resize_keyboard=True,
#                                              one_time_keyboard=True,
#                                              inline_keyboard=[
#                                                  [
#                                                      InlineKeyboardButton(text='Отменить поиск',
#                                                                           callback_data='cancel_searching'),
#                                                  ],
#                                              ])
