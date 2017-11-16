from menu.articles import update_articles_categories
from menu.guides import update_guides_categories
from menu.photo import update_photo_categories
from state import *
from util import *
import import_dir
import phrases
import time

import_dir.do('menu', globals())


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, phrases.start_message, reply_markup=menu_keyboard)


@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id, phrases.help_message, parse_mode="Markdown")


@bot.message_handler(regexp="^Меню$")
def return_to_menu(message):
    if check_state(message.chat.id):
        bot.send_message(message.chat.id, "Для получения справки нажмите /help",
                         reply_markup=menu_keyboard)


@bot.message_handler(regexp="^(\/contacts)|(Контакты)$")
def contacts(message):
    if check_state(message.chat.id):
        bot.send_message(message.chat.id, phrases.contacts,
                         reply_markup=menu_keyboard, parse_mode="Markdown")


def update_categories():
    update_articles_categories()
    update_guides_categories()
    update_photo_categories()


if __name__ == "__main__":
    while True:
        logger.info('update category lists')
        update_categories()
        try:
            bot.polling(none_stop=True, timeout=5)
        # ConnectionError and ReadTimeout because of possible timeout of the requests library
        # TypeError for moviepy errors
        # maybe there are others, therefore Exception
        except Exception as e:
            logger.error(e)
            time.sleep(15)

