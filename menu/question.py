import state
from util import *
import conf


@bot.message_handler(regexp="^(\/question)|(Вопрос)$")
def faq_keyword_search(message):
    if state.check_state(message.chat.id):
        state.start_enter_text(message.chat.id)
        msg = bot.send_message(message.chat.id,
                               "Введите запрос (например: KeyMission, SnapBridge, матрица):",
                               reply_markup=force_reply)
        bot.register_next_step_handler(msg, search_faq_by_keywords)


def search_faq_by_keywords(message):
    state.finish_enter_text(message.chat.id)
    words = message.text.split()

    if len(words) == 1:
        cursor.execute("SELECT url, title FROM `faq` Where locate('{0}', title) > 0"
                       .format(message.text[:-2]))
        data = list(cursor.fetchall())
    else:
        query = "SELECT url, title FROM `faq` Where "
        add_q = "locate('{0}', title) > 0 and "

        # TODO: сделать запрос который бы сортировал выдачу по числу вхождений
        for w in words:
            query += add_q.format(w[:-2])
        query = query[:-5]  # remove last " and "

        cursor.execute(query)
        data = list(cursor.fetchall())

        # if we can't find with "and" condition try to make search weaker - with "or"
        if len(data) == 0:
            query = query.replace("and", "or")
            cursor.execute(query)
            data = list(cursor.fetchall())

    if len(data) > 0:
        data = data[:conf.MAX_KEYWORD_SEARCH] if len(data) > conf.MAX_KEYWORD_SEARCH else data
        for row in data:
            bot.send_message(message.chat.id, "{0}\n{1}".format(row[1], row[0]),
                             reply_markup=menu_keyboard)
    else:
        bot.send_message(message.chat.id, "По этому запросу ничего не найдено.",
                         reply_markup=menu_keyboard)
