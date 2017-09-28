from telebot import types
import telebot
import conf
import MySQLdb
import logging


hide = types.ReplyKeyboardRemove()
return_button = types.KeyboardButton("Меню")
force_reply = types.ForceReply(selective=False)

menu_keyboard = types.ReplyKeyboardMarkup()
menu_keyboard.add(types.KeyboardButton("Фото"),
                  types.KeyboardButton("Советы"),
                  )
menu_keyboard.add(types.KeyboardButton("Вопрос"),
                  types.KeyboardButton("Статьи"),
                  types.KeyboardButton("Контакты")
                  )

logging.basicConfig(filename="telebot.log",
                    filemode='w',
                    level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')

logger = telebot.logger
telebot.logger.setLevel(logging.INFO)

bot = telebot.TeleBot(conf.TOKEN)

connection = MySQLdb.connect(conf.DB_HOST, conf.DB_USER, conf.DB_PASSWORD, conf.DB_NAME,
                             use_unicode=True, charset="utf8", autocommit=True)
cursor = connection.cursor()