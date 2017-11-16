from util import *
import state
import conf

guides_search_type = types.ReplyKeyboardMarkup()
guides_search_type.add(types.KeyboardButton("Категории"),
                       types.KeyboardButton("Поиск"),
                       return_button)
guides_categories = []


def update_guides_categories():
    global guides_categories
    cursor.execute('select distinct(category) from infographics')
    guides_categories = [c[0] for c in list(cursor.fetchall())]


@bot.message_handler(regexp="^(\/guides)|(Советы)$")
def guides_search(message):
    if state.check_state(message.chat.id):
        bot.send_message(message.chat.id, "Как будем искать?", reply_markup=guides_search_type)


@bot.message_handler(regexp="^Категории$")
def guides_cat_search(message):
    if state.check_state(message.chat.id):
        categories = types.InlineKeyboardMarkup()
        for g in guides_categories:
            categories.add(types.InlineKeyboardButton(text=g, callback_data=g))

        bot.send_message(message.chat.id, "Выберите категорию", reply_markup=categories)


@bot.callback_query_handler(func=lambda call: call.data in guides_categories)
def show_category_guides(call):
    cursor.execute("select url, `name` from infographics where category = '{0}'"
                   .format(call.data))
    for row in list(cursor.fetchall()):
        bot.send_message(call.message.chat.id, "{0}\n{1}".format(row[1], row[0]))


@bot.message_handler(regexp="^Поиск$")
def guides_keyword_search(message):
    state.start_enter_text(message.chat.id)

    msg = bot.send_message(message.chat.id,
                           "Введите ключевое слово:",
                           reply_markup=force_reply)
    bot.register_next_step_handler(msg, search_guides_by_keywords)


def search_guides_by_keywords(message):
    state.finish_enter_text(message.chat.id)

    cursor.execute("select url, `name` from infographics where `name` LIKE \'%{0}%\'"
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

