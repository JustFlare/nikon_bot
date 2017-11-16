from state import *
from util import *

article_genres = []


def update_articles_categories():
    global article_genres
    cursor.execute('select distinct(genre) from articles')
    article_genres = [g[0] for g in list(cursor.fetchall())]


@bot.message_handler(regexp="^(\/articles)|(Статьи)$")
def articles_search(message):
    if check_state():
        keyboard = types.InlineKeyboardMarkup()
        for g in article_genres:
            keyboard.add(types.InlineKeyboardButton(text=g, callback_data=g))
        bot.send_message(message.chat.id, "Выберите жанр:", reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data in article_genres)
def get_articles(call):
    cursor.execute("select url, `name`, author from articles where {0} = \'{1}\'".format("genre", call.data))
    res = list(cursor.fetchall())
    if res:
        for row in res:
            bot.send_message(call.message.chat.id,
                             "{0}\n{1}\n{2}".format(row[1], row[2], row[0]))
    else:
        bot.send_message(call.message.chat.id, "Статей выбранного жанра не найдено")

