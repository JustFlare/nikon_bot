from util import *
from random import shuffle

import phrases
import conf

photo_select_query = "select url, exposure, lens, genre, aperture, camera," \
                     " ISO, focal_length, author from photos where "


photo_search_categories = ["Экспозиция", "Объектив", "Жанр", "Камера", "Автор"]
search_photo_keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=False)
buttons = [types.KeyboardButton(c) for c in photo_search_categories]
search_photo_keyboard.add(buttons[0], buttons[1], buttons[2])
search_photo_keyboard.add(buttons[3], buttons[4], return_button)

cursor.execute('select distinct(genre) from photos')
photo_genres = [g[0] for g in list(cursor.fetchall())]
cursor.execute('select distinct(author) from photos')
authors = [a[0] for a in list(cursor.fetchall())]
cursor.execute('select distinct(camera) from photos order by SUBSTRING(camera, 7)')
cameras = [c[0] for c in list(cursor.fetchall())]
cursor.execute('select distinct(lens) from photos')
all_lens = [l[0] for l in list(cursor.fetchall())]


def pairwise(iterable):
    a = iter(iterable)
    return zip(a, a)


@bot.message_handler(regexp="^(\/photo)|(Фото)$")
def photo_search(message):
    bot.send_message(message.chat.id, "Выберите категорию поиска:",
                     reply_markup=search_photo_keyboard)


@bot.message_handler(func=lambda message: message.text in photo_search_categories)
def choose_search_category(message):
    keyboard = types.InlineKeyboardMarkup()
    if message.text == 'Экспозиция':
        msg = bot.send_message(message.chat.id,
                               "Введите значение экспозиции (например, 1/125 или 1/2500)",
                               reply_markup=force_reply)
        bot.register_next_step_handler(msg, search_by_exposure)

    elif message.text == 'Объектив':
        msg = bot.send_message(message.chat.id,
                               "Введите фокусное расстояние объектива",
                               reply_markup=force_reply)
        bot.register_next_step_handler(msg, choose_lens)

    elif message.text == 'Жанр':
        for g in photo_genres:
            keyboard.add(types.InlineKeyboardButton(text=g, callback_data=g))
        bot.send_message(message.chat.id, "Выберите жанр:", reply_markup=keyboard)

    elif message.text == 'Камера':
        for c1, c2 in pairwise(cameras):
            keyboard.add(types.InlineKeyboardButton(text=c1, callback_data=c1),
                         types.InlineKeyboardButton(text=c2, callback_data=c2))
        bot.send_message(message.chat.id, "Выберите камеру:", reply_markup=keyboard)

    elif message.text == 'Автор':
        for a in authors:
            keyboard.add(types.InlineKeyboardButton(text=a, callback_data=a))
        bot.send_message(message.chat.id, "Выберите автора", reply_markup=keyboard)

    else:
        bot.send_message(message.chat.id, "Неверное название категории. "
                                          "Выберите одну из предложенных на клавиатуре.")


def search_by_exposure(message):
    query = photo_select_query + " {0} = \'{1}\'".format("exposure", message.text)
    cursor.execute(query)
    show_photos(message, list(cursor.fetchall()),
                "фотографий с заданной экспозицией не найдено")


def choose_lens(message):
    query = "select distinct(lens) from photos where lens LIKE '%NIKKOR %{}%mm%'".format(
        message.text)
    cursor.execute(query)

    res = list(cursor.fetchall())
    if res:
        kb = types.InlineKeyboardMarkup()
        found_lens = [l[0] for l in res]
        for l in found_lens:
            kb.add(types.InlineKeyboardButton(text=l, callback_data=l))

        bot.send_message(message.chat.id, "Выберите модель объектива:",
                         reply_markup=kb)
    else:
        bot.send_message(message.chat.id, "Объектива с таким фокусным расстоянием не найдено",
                         reply_markup=search_photo_keyboard)


@bot.callback_query_handler(func=lambda call: call.data in all_lens)
def search_by_lens(call):
    query = photo_select_query + "lens = \'{0}\'".format(call.data)
    cursor.execute(query)
    show_photos(call.message, list(cursor.fetchall()), "Что-то пошло не так...")


@bot.callback_query_handler(func=lambda call: call.data in photo_genres)
def search_by_genre(call):
    cursor.execute(photo_select_query + "{0} = \'{1}\'".format("genre", call.data))
    show_photos(call.message, list(cursor.fetchall()),
                "фотографий выбранного жанра не найдено")


@bot.callback_query_handler(func=lambda call: call.data in cameras)
def search_by_camera(call):
    query = photo_select_query + "{0} = \'{1}\'".format("camera", call.data)
    cursor.execute(query)
    show_photos(call.message, list(cursor.fetchall()),
                "фотографий с заданной камерой не найдено")


@bot.callback_query_handler(func=lambda call: call.data in authors)
def search_by_author(call):
    query = photo_select_query + " {0} LIKE \'%{1}%\'".format("author", call.data)
    cursor.execute(query)
    show_photos(call.message, list(cursor.fetchall()), "такого автора нет в нашей базе данных")


def show_photos(message, data, not_found_text):
    if len(data) == 0:
        bot.send_message(message.chat.id, not_found_text, reply_markup=search_photo_keyboard)
    elif len(data) < conf.MAX_PHOTOS_TO_SHOW:
        for row in data:
            print_photo(message, row)
    else:
        shuffle(data)
        for row in data[:conf.MAX_PHOTOS_TO_SHOW]:
            print_photo(message, row)


def print_photo(message, row):
    url, exposure, lens, genre, aperture, camera, iso, focal_length, author = row
    bot.send_message(message.chat.id,
                     phrases.PHOTO_PRINT_PATTERN.format(camera, lens, aperture, exposure, iso,
                                                        focal_length, author, url),
                     reply_markup=search_photo_keyboard)
