import MySQLdb

import telebot
from telebot import types

import conf
import phrases

import logging
from random import shuffle


photo_search_categories = ["Экспозиция", "Объектив", "Жанр", "Камера", "Автор"]

hide = types.ReplyKeyboardRemove()
return_button = types.KeyboardButton("Меню")
force_reply = types.ForceReply(selective=False)

search_photo_keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=False)
buttons = [types.KeyboardButton(c) for c in photo_search_categories]
search_photo_keyboard.add(buttons[0], buttons[1], buttons[2])
search_photo_keyboard.add(buttons[3], buttons[4], return_button)

menu = types.ReplyKeyboardMarkup()
menu.add(types.KeyboardButton("Фото"),
         types.KeyboardButton("Советы"),
         )
menu.add(types.KeyboardButton("Вопрос"),
         types.KeyboardButton("Статьи"),
         types.KeyboardButton("Контакты")
         )

guides_search_type = types.ReplyKeyboardMarkup()
guides_search_type.add(types.KeyboardButton("Категории"),
                       types.KeyboardButton("Поиск"),
                       return_button)

logger = telebot.logger
telebot.logger.setLevel(logging.INFO)

bot = telebot.TeleBot(conf.TOKEN)
bot.remove_webhook()


def pairwise(iterable):
    a = iter(iterable)
    return zip(a, a)


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, phrases.start_message, reply_markup=menu)


@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id, phrases.help_message)


@bot.message_handler(regexp="Меню")
def return_to_menu(message):
    bot.send_message(message.chat.id, "Для получения справки нажмите /help",
                     reply_markup=menu)

############################################################################


@bot.message_handler(regexp="(\/question)|(Вопрос)")
def faq_search(message):
    keyboard = types.InlineKeyboardMarkup()
    url_button = types.InlineKeyboardButton(text="Перейти на сайт",
                                            url=conf.FAQ_SEARCH_LINK)
    keyboard.add(url_button)
    bot.send_message(message.chat.id,
                     "Попробуйте найти ответы с помощью функции поиска на нашем сайте"
                     " (поиск непосредственно в боте - в разработке)",
                     reply_markup=keyboard)

############################################################################


@bot.message_handler(regexp="(\/photo)|(Фото)")
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
    query = "select * from photos where {0} = \'{1}\'".format("exposure", message.text)
    cursor.execute(query)
    # logging.info(query)
    show_photos(message, list(cursor.fetchall()),
                "фотографий с заданной экспозицией не найдено")


def choose_lens(message):
    query = "select distinct(lens) from photos where lens LIKE '%NIKKOR {}mm%'".format(message.text)
    cursor.execute(query)
    # logging.info(query)

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
    query = "select * from photos where lens = \'{0}\'".format(call.data)
    cursor.execute(query)
    show_photos(call.message, list(cursor.fetchall()), "Что-то пошло не так...")


@bot.callback_query_handler(func=lambda call: call.data in photo_genres)
def search_by_genre(call):
    cursor.execute("select * from photos where {0} = \'{1}\'".format("genre", call.data))
    show_photos(call.message, list(cursor.fetchall()),
                "фотографий выбранного жанра не найдено")


@bot.callback_query_handler(func=lambda call: call.data in cameras)
def search_by_camera(call):
    query = "select * from photos where {0} = \'{1}\'".format("camera", call.data)
    cursor.execute(query)
    # logging.info(query)
    show_photos(call.message, list(cursor.fetchall()),
                "фотографий с заданной камерой не найдено")


@bot.callback_query_handler(func=lambda call: call.data in authors)
def search_by_author(call):
    query = "select * from photos where {0} LIKE \'%{1}%\'".format("author", call.data)
    cursor.execute(query)
    # logging.info(query)
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
        # TODO: кнопка/опция "показать еще"


def print_photo(message, row):
    link, exposure, lens, genre, aperture, camera, iso, focal_length, author = row
    bot.send_message(message.chat.id, "{0}\n{1}\n{2}\n{3}\n{4}\n{5}\n{6}\n{7}\n{8}"
                     .format(link, exposure, lens, genre, aperture, camera, iso,
                             focal_length, author),
                     reply_markup=search_photo_keyboard)

############################################################################


@bot.message_handler(regexp="(\/articles)|(Статьи)")
def articles_search(message):
    keyboard = types.InlineKeyboardMarkup()
    for g in article_genres:
        keyboard.add(types.InlineKeyboardButton(text=g, callback_data=g))
    bot.send_message(message.chat.id, "Выберите жанр:", reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data in article_genres)
def get_articles(call):
    cursor.execute("select * from articles where {0} = \'{1}\'".format("genre", call.data))
    res = list(cursor.fetchall())
    if res:
        for row in res:
            bot.send_message(call.message.chat.id,
                             "{0}\n{1}\n{2}".format(row[1], row[2], row[0]))
    else:
        bot.send_message(call.message.chat.id, "Статей выбранного жанра не найдено")

############################################################################


@bot.message_handler(regexp="(\/guides)|(Советы)")
def guides_search(message):
    bot.send_message(message.chat.id, "Как будем искать?", reply_markup=guides_search_type)


@bot.message_handler(regexp="Категории")
def guides_cat_search(message):
    categories = types.InlineKeyboardMarkup()
    for g in guides_categories:
        categories.add(types.InlineKeyboardButton(text=g, callback_data=g))

    bot.send_message(message.chat.id, "Выберите категорию", reply_markup=categories)


@bot.callback_query_handler(func=lambda call: call.data in guides_categories)
def show_category_guides(call):
    cursor.execute("select filename, `name` from infographics where category = '{0}'"
                   .format(call.data))
    for row in list(cursor.fetchall()):
        bot.send_message(call.message.chat.id, "{0}\n{1}".format(row[1], row[0]))


@bot.message_handler(regexp="Поиск")
def guides_keyword_search(message):
    msg = bot.send_message(message.chat.id,
                           "Введите ключевое слово:",
                           reply_markup=force_reply)
    bot.register_next_step_handler(msg, search_guides_by_keywords)


def search_guides_by_keywords(message):
    cursor.execute("select filename, `name` from infographics where `name` LIKE \'%{0}%\'"
                   .format(message.text))
    data = list(cursor.fetchall())

    if len(data) > 0:
        data = data[:conf.MAX_KEYWORD_SEARCH] if len(data) > conf.MAX_KEYWORD_SEARCH else data
        for row in data:
            bot.send_message(message.chat.id, "{0}\n{1}".format(row[1], row[0]),
                             reply_markup=guides_search_type)
    else:
        bot.send_message(message.chat.id, "По этому слову ничего не найдено.",
                         reply_markup=guides_search_type)

############################################################################


@bot.message_handler(regexp="(\/contacts)|(Контакты)")
def buy(message):
    bot.send_message(message.chat.id, phrases.contacts, reply_markup=menu)


if __name__ == "__main__":
    print('start bot')
    connection = MySQLdb.connect(conf.DB_HOST, conf.DB_USER, conf.DB_PASSWORD, conf.DB_NAME,
                                 use_unicode=True, charset="utf8", autocommit=True)
    cursor = connection.cursor()

    # create category lists for searching
    """cursor.execute("UPDATE photos set camera = TRIM(camera), author = TRIM(author),"
                   " genre = TRIM(genre);")"""

    cursor.execute('select distinct(genre) from photos')
    photo_genres = [g[0] for g in list(cursor.fetchall())]
    cursor.execute('select distinct(author) from photos')
    authors = [a[0] for a in list(cursor.fetchall())]
    cursor.execute('select distinct(camera) from photos order by SUBSTRING(camera, 7)')
    cameras = [c[0] for c in list(cursor.fetchall())]
    cursor.execute('select distinct(lens) from photos')
    all_lens = [l[0] for l in list(cursor.fetchall())]

    cursor.execute('select distinct(category) from infographics')
    guides_categories = [c[0] for c in list(cursor.fetchall())]

    cursor.execute('select distinct(genre) from articles')
    article_genres = [g[0] for g in list(cursor.fetchall())]

    bot.polling(none_stop=True)
    cursor.close()
    connection.close()
