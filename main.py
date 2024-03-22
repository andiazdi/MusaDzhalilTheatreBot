import telebot
from telebot.types import LabeledPrice
from functions import *
from Text import *
from fuzzywuzzy import fuzz
import json

news = []
timing = []
user_news = {}
user_history = {}
user_review = {}
hall_size = [i for i in range(1, 570)]
url = 'https://quotes.toscrape.com/'
bot = telebot.TeleBot('TOKEN')
channel_id = -1001124641095
base = Ratio()
base.read_json()


@bot.message_handler(commands=['start'])
def start(message):
    global user_news

    if message.chat.id not in user_news.keys():
        user_news[message.chat.id] = 0
    if message.chat.id not in user_history.keys():
        user_history[message.chat.id] = 0

    msg = f'Приветствуем, {message.from_user.first_name}, в телеграм боте-помощнике ' \
          f'к Татарскому академическому театру оперы и балета имени Муса Джалиля.\n\n'
    msg += 'Здесь вы сможете:\n'
    msg += '    📌 Посмотреть актуальные новости.\n'
    msg += '    📌 Просмотреть афишу\n'
    msg += '    📌 Купить билеты и забронировать места\n'
    msg += '    📌 Узнать об истории театра'
    bot.send_message(message.chat.id, msg, reply_markup=main_murkup())


@bot.message_handler(content_types=['successful_payment'])
def got_payment(message):
    bot.send_message(message.chat.id, 'Успешная покупка')


@bot.message_handler(commands=['buy_ok'])
def ok(message):
    bot.send_message(message.chat.id, 'Успешная покупка')


@bot.message_handler(content_types=['text'])
def text(message):
    global news, user_news

    if message.chat.id not in user_news.keys():
        user_news[message.chat.id] = 0
    if message.chat.id not in user_history.keys():
        user_history[message.chat.id] = 0

    if message.text == '🗓 Афиша':
        global timing
        msg = ''
        timing = get_timing()
        for id, i in enumerate(timing):
            msg += f'{id + 1}){i[0]}'
            msg += f' - {i[1]} {i[2]}, {i[3]} {i[4]}\n\n'
        bot.send_message(message.chat.id, msg, reply_markup=markup_paymant_start())

    if message.text == '📰 Новости':
        msg = ''
        user_news_c = user_news[message.chat.id]
        news = get_news()
        print(news)
        img = "static/" + news[user_news_c + 1][2]

        msg += f'{news[user_news_c + 1][0]}\n\n'
        msg += f'Дата написания - {news[user_news_c +1 ][1]}\n\n'
        bot.send_photo(message.chat.id, photo=img, caption=msg, reply_markup=markup_next())

    if message.text == '📰 История музея':
        msg = ''
        user_history_с = user_history[message.chat.id]

        img = "static/" + imgs[user_history_с]
        msg = texts[user_history_с]

        with open(img, 'rb') as f:
            bot.send_photo(message.chat.id, photo=f, caption=msg, reply_markup=markup_prev())

    if message.text == '📨 Оставить отзыв':
        bot.delete_message(message.chat.id, message.id)
        timing = get_timing()
        msg1 = ''
        for id, i in enumerate(timing):
            msg1 += f'{id + 1}){i[0]}'
            msg1 += f' - {i[1]} {i[2]}, {i[3]} {i[4]}\n\n'
        bot.send_message(message.chat.id, msg1)
        msg = bot.send_message(message.chat.id, 'Введите номер мероприятия:', reply_markup=cancel_review())
        bot.register_next_step_handler(msg, start_register)

    if message.text == '✉️ Контакты':
        msg = 'Канал с отзывами - https://t.me/MusaDzhalilTheatre\n\n'
        msg += 'Канал с новостями министерства культуры - , https://t.me/mincultnews \n' \
               'Каждое воскресенье будут разыграны 2 билета на спектакль, среди подписчиков канала\n\n'
        msg += 'Сайт театра оперы и балета имени Мусы Джалиля - https://kazan-opera.ru/\n\n'
        msg += 'Cайт министерства культуры - https://culture.gov.ru/'
        bot.send_message(message.chat.id, msg)

    if message.text == '⭐️Рекомендации':
        msg = ''
        top5 = base.top5()
        if not top5:
            bot.send_message(message.chat.id, 'Рейтинг еще пуст, но ты можешь его открыть 😉')
            return
        for i, item in enumerate(top5):
            msg += f'{item[0]} - {item[1]} 💫\n'
            if i + 1 == len(top5):
                break
        bot.send_message(message.chat.id, msg)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    global user_news
    global timing

    if call.message.chat.id not in user_news.keys():
        user_news[call.message.chat.id] = 0
    if call.message.chat.id not in user_history.keys():
        user_history[call.message.chat.id] = 0

    if call:
        if call.data == 'next_news':
            user_news[call.message.chat.id] += 1
            user_news_c = user_news[call.message.chat.id]
            news = get_news()
            if user_news_c < 0:
                user_news[call.message.chat.id] = 11
            elif user_news_c == 12:
                user_news[call.message.chat.id] = 0
            user_news_c = user_news[call.message.chat.id]
            msg = ''
            img = "static/" + news[user_news_c][2]
            msg += f'{news[user_news_c][0]}\n\n'
            msg += f'{news[user_news_c][3]}\n'
            msg += f'Дата написания - {news[user_news_c][1].lower()}\n\n'

            bot.delete_message(call.message.chat.id, call.message.id)
            bot.send_photo(call.message.chat.id, photo=img, caption=msg, reply_markup=markup_next())

        elif call.data == 'prev_news':
            user_news[call.message.chat.id] -= 1
            user_news_c = user_news[call.message.chat.id]
            news = get_news()
            if user_news_c < 0:
                user_news[call.message.chat.id] = 11
            elif user_news_c == 12:
                user_news[call.message.chat.id] = 0
            user_news_c = user_news[call.message.chat.id]
            msg = ''
            img = "static/" + news[user_news_c][2]
            msg += f'{news[user_news_c][0]}\n\n'
            msg += f'{news[user_news_c][3]}\n'
            msg += f'Дата написания - {news[user_news_c][1].lower()}\n\n'

            bot.delete_message(call.message.chat.id, call.message.id)
            bot.send_photo(call.message.chat.id, photo=img, caption=msg, reply_markup=markup_next())

        elif call.data == 'next_history':
            user_history[call.message.chat.id] += 1
            user_history_c = user_history[call.message.chat.id]
            if user_history_c < 0:
                user_history[call.message.chat.id] = 2
            elif user_history_c > 3:
                user_history[call.message.chat.id] = 1
            user_history_c = user_history[call.message.chat.id]
            img = "static/" + imgs[user_history_c]
            msg = texts[user_history_c]

            with open(img, 'rb') as f:
                bot.delete_message(call.message.chat.id, call.message.id)
                bot.send_photo(call.message.chat.id, photo=f, caption=msg, reply_markup=markup_prev())

        elif call.data == 'prev_history':
            user_history[call.message.chat.id] -= 1
            user_history_c = user_history[call.message.chat.id]
            if user_history_c < 0:
                user_history[call.message.chat.id] = 2
            elif user_history_c > 3:
                user_history[call.message.chat.id] = 1
            user_history_c = user_history[call.message.chat.id]
            img = "static/" + imgs[user_history_c]
            msg = texts[user_history_c]

            with open(img, 'rb') as f:
                bot.delete_message(call.message.chat.id, call.message.id)
                bot.send_photo(call.message.chat.id, photo=f, caption=msg, reply_markup=markup_prev())

        elif call.data == 'review_start':
            bot.delete_message(call.message.chat.id, call.message.id)
            timing = get_timing()
            msg1 = ''
            for id, i in enumerate(timing):
                msg1 += f'{id + 1}){i[0]}'
                msg1 += f' - {i[1]} {i[2]}, {i[3]} {i[4]}\n\n'
            bot.send_message(call.message.chat.id, msg1)
            msg = bot.send_message(call.message.chat.id, 'Введите номер мероприятия:', reply_markup=cancel_review())

            print('REVIEW_START IS ENDED')
            bot.register_next_step_handler(msg, start_register)

        elif call.data == 'cancel_review':
            bot.delete_message(call.message.chat.id, call.message.id)
            bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
            msg = ''
            user_news_c = user_news[call.message.chat.id]
            news = get_news()
            img = "static/" + news[user_news_c][2]
            msg += f'{news[user_news_c][0]}\n\n'
            msg += f'Дата написания - {news[user_news_c][1]}\n\n'

            bot.send_photo(call.message.chat.id, photo=img, caption=msg, reply_markup=markup_next())

        elif call.data == 'review_ok':
            bot.delete_message(call.message.chat.id, call.message.id)
            msg = bot.send_message(call.message.chat.id, 'Введите название отзыва')
            bot.register_next_step_handler(msg, title_register)

        elif call.data == 'review_bad':
            bot.delete_message(call.message.chat.id, call.message.id)
            msg = bot.send_message(call.message.chat.id, 'Введите название отзыва')
            bot.register_next_step_handler(msg, start_register)

        elif call.data == 'review_title_ok':
            bot.delete_message(call.message.chat.id, call.message.id)
            msg = bot.send_message(call.message.chat.id, 'Введите текст отзыва')
            bot.register_next_step_handler(msg, text_register)

        elif call.data == 'review_title_bad':
            bot.delete_message(call.message.chat.id, call.message.id)
            msg = bot.send_message(call.message.chat.id, 'Введите название отзыва:')
            user_review[call.message.chat.id] = ';'.join(user_review[call.message.chat.id].split(';')[:-1])
            bot.register_next_step_handler(msg, title_register)

        elif call.data == 'review_text_ok':
            bot.delete_message(call.message.chat.id, call.message.id)
            msg = bot.send_message(call.message.chat.id, 'Введите оценку отзыва от 1 до 5')
            bot.register_next_step_handler(msg, grade_register)

        elif call.data == 'review_text_bad':
            bot.delete_message(call.message.chat.id, call.message.id)
            msg = bot.send_message(call.message.chat.id, 'Введите текст')
            bot.register_next_step_handler(msg, text_register)

        elif call.data == 'review_grade_ok':
            bot.delete_message(call.message.chat.id, call.message.id)
            msg = bot.send_message(call.message.chat.id, 'Успешное оформление отзыва')
            print(user_review[call.message.chat.id])
            print(user_review[call.message.chat.id].split(';'))
            num, title, text, grade = user_review[call.message.chat.id].split(';')
            print(num, title, text, grade)
            msg = f'{title}\n\n'
            msg += f'{text}\n'
            msg += f'Мероприятие - {timing[int(num) - 1][0]}\n'
            msg += f'Оценка - {grade}'
            base.add(timing[int(num) - 1][0], int(grade))
            base.write_to_json()
            bot.send_message(-1001124641095, msg)
            user_review[call.message.chat.id] = ''
            bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)

        elif call.data == 'review_grade_bad':
            bot.delete_message(call.message.chat.id, call.message.id)
            msg = bot.send_message(call.message.chat.id, 'Введите оценку мероприятия')
            bot.register_next_step_handler(msg, grade_register)

        elif call.data == 'start_pay':
            bot.delete_message(call.message.chat.id, call.message.id)
            msg1 = ''
            timing = get_timing()
            for id, i in enumerate(timing):
                msg1 += f'{id + 1}){i[0]}'
                msg1 += f' - {i[1]} {i[2]}, {i[3]} {i[4]}\n\n'

            bot.send_message(call.message.chat.id, msg1)
            msg = bot.send_message(call.message.chat.id, 'Введите номер мероприятия:', reply_markup=cancel_review())

            print('START_PAY IS ENDED')
            bot.register_next_step_handler(msg, get_event)

        elif call.data == 'review_event_ok':
            bot.delete_message(call.message.chat.id, call.message.id)
            msg = bot.send_message(call.message.chat.id, f'Введите место от 1 до {len(hall_size)}')
            bot.register_next_step_handler(msg, get_sit)

        elif call.data == 'review_event_bad':
            bot.delete_message(call.message.chat.id, call.message.id)
            msg = bot.send_message(call.message.chat.id, f'Введите мероприятие от 1 до 12')
            bot.register_next_step_handler(msg, get_event)

        if call.data == 'success':
            bot.delete_message(call.message.chat.id, call.message.id)
            bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
            bot.send_message(call.message.chat.id, 'Спасибо за покупку')


def start_register(message):
    global timing
    print('start_register')

    try:
        int(message.text)
    except Exception as e:
        print('NOT INT IN START MESSAGE')
        msg = bot.send_message(message.chat.id, 'Введите корректный номер мероприятия')
        bot.register_next_step_handler(msg, start_register)
        return

    timing = get_timing()
    if int(message.text) < 1 or int(message.text) > len(timing):
        msg = ''
        for id, i in enumerate(timing):
            msg += f'{id + 1}){i[0]}'
            msg += f' - {i[1]} {i[2]}, {i[3]} {i[4]}\n\n'
        bot.send_message(message.chat.id, msg)

        msg = bot.send_message(message.chat.id, 'Введите корректный номер мероприятия')
        bot.register_next_step_handler(msg, start_register)
        return
    bot.send_message(message.chat.id, f'Подтвердите мероприятие - {timing[int(message.text) - 1][0]}', reply_markup=markup_confirm())
    user_review[message.chat.id] = f"{message.text};"


def title_register(message):
    global user_review
    print('title_register')
    ban = False
    for i in message.text.split():
        for j in curse_words:
            if fuzz.WRatio(i.lower(), j.lower()) > 50:
                ban = True
                break

    if ban:
        msg = bot.send_message(message.chat.id, 'Использование матерных слов - запрещено!')
        bot.register_next_step_handler(msg, title_register)
        return

    user_review[message.chat.id] += f'{message.text};'
    msg = bot.send_message(message.chat.id, f'Подтвердите название: {message.text}', reply_markup=markup_confirm_title())
    # bot.register_next_step_handler(msg, text_register)


def text_register(message):
    global user_review
    print('text_register')
    ban = False
    for i in message.text.split():
        for j in curse_words:
            if fuzz.WRatio(i.lower(), j.lower()) > 50:
                ban = True
                break

    if ban:
        msg = bot.send_message(message.chat.id, 'Использование матерных слов - запрещено!')
        bot.register_next_step_handler(msg, text_register)
        return

    user_review[message.chat.id] += f'{message.text};'
    msg = bot.send_message(message.chat.id, f'Подтвердите текст отзыва: {message.text}', reply_markup=markup_confirm_text())
    # bot.register_next_step_handler(msg, grade_register)


def grade_register(message):
    print('grade_register')
    try:
        int(message.text)
    except Exception as e:
        print('NOT INT IN GRADE MESSAGE')
        msg = bot.send_message(message.chat.id, 'Введите корректную оценку от 1 до 5')
        bot.register_next_step_handler(msg, grade_register)
        return

    if 0 < int(message.text) < 6:
        user_review[message.chat.id] += f'{message.text}'
        bot.send_message(message.chat.id, f'Подтвердите оценку: {message.text}', reply_markup=markup_confirm_grade())
    else:
        msg = bot.send_message(message.chat.id, 'Введите корректную оценку от 1 до 5')
        bot.register_next_step_handler(msg, grade_register)


def get_event(message):
    global timing

    timing = get_timing()
    print('get_event')
    try:
        int(message.text)
    except Exception as e:
        print('NOT INT IN SIT MESSAGE')
        msg = bot.send_message(message.chat.id, f'Введите корректное мероприятие от 1 до 12')
        bot.register_next_step_handler(msg, get_event)
        return

    if 0 < int(message.text) < 13:
        bot.send_message(message.chat.id, f'Подтвердите мероприятие: {timing[int(message.text) - 1][0]}', reply_markup=markup_confirm_event())
    else:
        msg = bot.send_message(message.chat.id, f'Введите корректное мероприятие от 1 до {len(timing)}')
        bot.register_next_step_handler(msg, get_event)


def get_sit(message):
    print('get_sit')
    try:
        int(message.text)
    except Exception as e:
        print('NOT INT IN SIT MESSAGE')
        msg = bot.send_message(message.chat.id, 'Введите корректное место от 1 до 569')
        bot.register_next_step_handler(msg, get_sit)
        return

    if 0 >= int(message.text) or int(message.text) > 570:
        msg = bot.send_message(message.chat.id, 'Введите корректное место от 1 до 569')
        bot.register_next_step_handler(msg, get_sit)
        return

    if hall_size[int(message.text)] == 0:
        msg = bot.send_message(message.chat.id, 'Место уже куплено, выберите другое')
        bot.register_next_step_handler(msg, get_sit)
        return
    hall_size[int(message.text)] = 0
    bot.send_invoice(message.chat.id, title='Покупка билета',
                     description='Покупка билета в театре оперы и балета',
                     invoice_payload='pay',
                     provider_token='381764678:TEST:25691',
                     currency='RUB',
                     start_parameter='test',
                     prices=[LabeledPrice('Билет', 50000)])


bot.polling(none_stop=True)
