import MySQLdb
import telebot
from telebot import types
from conf import *
import logging
from random import shuffle

START_MESSAGE = '''Здравствуйте! 
Этот бот призван помочь начинающим фотографам и облегчить взаимодействие с фотоаппаратами nikon
Содержание:
/question - ответы на вопрос
/photo - поиск фотографий по различным категориям
/articles - статьи 
/guides - обучающие материалы
/buy - где купить
'''

photo_search_categories = {"exposure": "Экспозиция", "lens": "Объектив",
                           "genre": "Жанр", "camera": "Камера", "author": "Автор"}

logger = telebot.logger
telebot.logger.setLevel(logging.INFO)


bot = telebot.TeleBot(TOKEN)
bot.remove_webhook()


@bot.message_handler(commands=['start', 'help'])
def start(message):
    bot.send_message(message.chat.id, START_MESSAGE)


@bot.message_handler(commands=['question'])
def search_faq(message):
    keyboard = types.InlineKeyboardMarkup()
    url_button = types.InlineKeyboardButton(text="Перейти на сайт",
                                            url=FAQ_SEARCH_LINK)
    keyboard.add(url_button)
    bot.send_message(message.chat.id,
                     "Попробуйте найти ответы с помощью функции поиска на нашем сайте",
                     reply_markup=keyboard)

############################################################################


@bot.message_handler(commands=['photo'])
def search_photo(message):
    keyboard = types.InlineKeyboardMarkup()
    for k, v in photo_search_categories.items():
        keyboard.add(types.InlineKeyboardButton(text=v, callback_data=k))

    bot.send_message(message.chat.id, "Выберите категорию поиска:", reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data in photo_search_categories)
def search_category_choice(call):
    markup = types.ForceReply(selective=False)
    if call.data == 'exposure':
        msg = bot.send_message(call.message.chat.id,
                               "Введите значение экспозиции (например, 1/125 или 1/2500)",
                               reply_markup=markup)
        bot.register_next_step_handler(msg, search_by_exposure)
    elif call.data == 'lens':
        msg = bot.send_message(call.message.chat.id,
                               "Введите название (можно частичное) объектива",
                               reply_markup=markup)
        bot.register_next_step_handler(msg, search_by_lens)
    elif call.data == 'genre':
        keyboard = types.InlineKeyboardMarkup()
        for g in photo_genres:
            keyboard.add(types.InlineKeyboardButton(text=g, callback_data=g))

        bot.send_message(call.message.chat.id, "Выберите жанр:", reply_markup=keyboard)
    elif call.data == 'camera':
        msg = bot.send_message(call.message.chat.id,
                               "Введите название камеры (например Nikon D4)",
                               reply_markup=markup)
        bot.register_next_step_handler(msg, search_by_camera)
    elif call.data == 'author':
        msg = bot.send_message(call.message.chat.id,
                               "Введите имя и/или фамилию автора",
                               reply_markup=markup)
        bot.register_next_step_handler(msg, search_by_author)


@bot.callback_query_handler(func=lambda call: call.data in photo_genres)
def search_category_choice(call):
    cursor.execute("select * from photos where {0} = \'{1}\'".format("genre", call.data))
    show_photos(call.message, list(cursor.fetchall()),
                "фотографий выбранного жанра не найдено")


def search_by_exposure(message):
    cursor.execute("select * from photos where {0} = \'{1}\'".format("exposure", message.text))
    show_photos(message, list(cursor.fetchall()),
                "фотографий с заданной экспозицией не найдено")


def search_by_lens(message):
    cursor.execute(
        "select * from photos where {0} LIKE \'%{1}%\'".format("lens", message.text))
    show_photos(message, list(cursor.fetchall()), "фотографий с таким объективом не найдено")


def search_by_camera(message):
    cursor.execute(
        "select * from photos where {0} = \'{1}\'".format("camera", message.text))
    show_photos(message, list(cursor.fetchall()), "фотографий с заданной камерой не найдено")


def search_by_author(message):
    cursor.execute(
        "select * from photos where {0} LIKE \'%{1}%\'".format("author", message.text))
    show_photos(message, list(cursor.fetchall()), "такого автора пока нет в нашей базе данных")


def show_photos(message, data, not_found_text):
    if len(data) == 0:
        bot.send_message(message.chat.id, not_found_text)
        # TODO: предложить пользователю попробовать еще раз
    elif len(data) < MAX_PHOTOS_TO_SHOW:
        for row in data:
            print_photo(message, row)
    else:
        shuffle(data)
        for row in data[:MAX_PHOTOS_TO_SHOW]:
            print_photo(message, row)
        # TODO: кнопка/опция "показать еще"


def print_photo(message, row):
    link, exposure, lens, genre, aperture, camera, iso, focal_length, author = row
    bot.send_message(message.chat.id, "{0}\n{1}\n{2}\n{3}\n{4}\n{5}\n{6}\n{7}\n{8}"
                     .format(link, exposure, lens, genre, aperture, camera, iso,
                             focal_length, author))

############################################################################


@bot.message_handler(commands=['guides', 'articles'])
def buy(message):
    bot.send_message(message.chat.id, "Эта функция пока не реализована")


@bot.message_handler(commands=['buy'])
def buy(message):
    keyboard = types.InlineKeyboardMarkup()
    url_button = types.InlineKeyboardButton(text="Перейти в магазин",
                                            url=STORE_LINK)
    keyboard.add(url_button)
    bot.send_message(message.chat.id, "Где купить", reply_markup=keyboard)


if __name__ == "__main__":
    print('start bot')
    connection = MySQLdb.connect(DB_HOST, DB_USER, DB_PASSWORD, DB_NAME,
                                 use_unicode=True, charset="utf8")
    cursor = connection.cursor()

    cursor.execute('select distinct(genre) from photos')
    photo_genres = [g[0] for g in list(cursor.fetchall())]

    bot.polling(none_stop=True)
    cursor.close()
    connection.close()
