import MySQLdb
import telebot
from telebot import types
from conf import *
import logging

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
photo_search_query = 'select * from photos where {0} == {1}'

logger = telebot.logger
telebot.logger.setLevel(logging.INFO)


bot = telebot.TeleBot(TOKEN)
bot.remove_webhook()


@bot.message_handler(commands=['start', 'help'])
def start(message):
    bot.send_message(message.chat.id, START_MESSAGE)


# TODO: # make it reacts to /question command - search nikon website with a given question
@bot.message_handler(commands=['question'])
def search_faq(message):
    keyboard = types.InlineKeyboardMarkup()
    url_button = types.InlineKeyboardButton(text="Перейти на сайт",
                                            url=FAQ_SEARCH_LINK)
    keyboard.add(url_button)
    bot.send_message(message.chat.id, "Попробуйте найти ответы с помощью функции поиска на нашем сайте",
                     reply_markup=keyboard)

############################################################################


@bot.message_handler(commands=['photo'])
def search_photo(message):
    # markup = types.ReplyKeyboardMarkup(row_width=2)

    keyboard = types.InlineKeyboardMarkup()
    for k, v in photo_search_categories.items():
        keyboard.add(types.InlineKeyboardButton(text=v, callback_data=k))

    bot.send_message(message.chat.id, "Выберите категорию поиска:", reply_markup=keyboard)


@bot.message_handler(func=lambda message: message.text in photo_search_categories)
def send_welcome(message):
    if message.text == 'Экспозиция':
        pass
        #cursor.execute(photo_search_query.format('exposure'))

############################################################################


@bot.message_handler(commands=['buy'])
def buy(message):
    keyboard = types.InlineKeyboardMarkup()
    url_button = types.InlineKeyboardButton(text="Перейти в магазин",
                                            url=STORE_LINK)
    keyboard.add(url_button)
    bot.send_message(message.chat.id, "Где купить", reply_markup=keyboard)


@bot.message_handler(func=lambda m: True)  # этот обработчик реагирует все прочие сообщения
def answer_unhandled_command(message):
    bot.send_message(message.chat.id, 'Для просмотра списка доступных команд введите /help')


if __name__ == "__main__":
    print('start bot')
    #connection = MySQLdb.connect(DB_HOST, DB_USER, DB_PASSWORD, DB_NAME)
    #cursor = connection.cursor()
    bot.polling(none_stop=True)
    #cursor.close()
    #connection.close()
