from state import *
from util import *
import import_dir
import phrases

import_dir.do('menu', globals())


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, phrases.start_message, reply_markup=menu_keyboard)


@bot.message_handler(commands=['help'])
def help(message):
    bot.send_message(message.chat.id, phrases.help_message, parse_mode="Markdown")


@bot.message_handler(regexp="^Меню$")
def return_to_menu(message):
    if check_state():
        bot.send_message(message.chat.id, "Для получения справки нажмите /help",
                         reply_markup=menu_keyboard)


@bot.message_handler(regexp="^(\/contacts)|(Контакты)$")
def contacts(message):
    if check_state():
        bot.send_message(message.chat.id, phrases.contacts,
                         reply_markup=menu_keyboard, parse_mode="Markdown")


if __name__ == "__main__":
    bot.polling(none_stop=True, timeout=5)
