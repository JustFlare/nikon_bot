import telebot
from conf import *
import flask
import logging

logger = telebot.logger
telebot.logger.setLevel(logging.INFO)

WEBHOOK_URL_BASE = "https://{}:{}".format(WEBHOOK_HOST, WEBHOOK_PORT)
WEBHOOK_URL_PATH = "/{}/".format(TOKEN)

START_MESSAGE = '''Здравствуйте! 
Этот бот умеет делать чудесные вещи, например подсчитывать число символов в вашем сообщении'''


bot = telebot.TeleBot(TOKEN)
bot.remove_webhook()  # удаляем предыдущие вебхуки, если они были
bot.set_webhook(url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH)  # добавляем новый вебхук

app = flask.Flask(__name__)


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.send_message(message.chat.id, START_MESSAGE)


@bot.message_handler(func=lambda m: True)  # этот обработчик реагирует все прочие сообщения
def send_len(message):
    bot.send_message(message.chat.id,
                     'В вашем сообщении {} символов.'.format(len(message.text)))


@app.route('/', methods=['GET', 'HEAD'])
def index():
    return 'it works!'


# обрабатываем вызовы вебхука
@app.route(WEBHOOK_URL_PATH, methods=['POST'])
def webhook():
    if flask.request.headers.get('content-type') == 'application/json':
        json_string = flask.request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return ''
    else:
        flask.abort(403)


# TODO: посмотреть доки к этому методу и в проде сделать как там пишут
# Start flask server
app.run(host=WEBHOOK_LISTEN,
        port=WEBHOOK_PORT,
        ssl_context=(WEBHOOK_SSL_CERT, WEBHOOK_SSL_PRIV),
        debug=True)
