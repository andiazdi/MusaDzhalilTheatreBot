from telebot import types
import requests
from bs4 import BeautifulSoup
import json


def main_murkup():
    menu = types.ReplyKeyboardMarkup(row_width=2)
    catalog = types.KeyboardButton('🗓 Афиша')
    news = types.KeyboardButton('📰 Новости')
    history = types.KeyboardButton('📰 История музея')
    review = types.KeyboardButton('📨 Оставить отзыв')
    contacts = types.KeyboardButton('✉️ Контакты')
    reci = types.KeyboardButton('⭐️Рекомендации')
    menu.add(catalog, news, history, review, contacts, reci)

    return menu


def markup_next():
    products = types.InlineKeyboardMarkup(row_width=2)
    prev = types.InlineKeyboardButton('Вперед  ▶', callback_data='next_news')
    next = types.InlineKeyboardButton('◀️ Назад', callback_data='prev_news')
    products.add(next, prev)

    return products


def markup_prev():
    products = types.InlineKeyboardMarkup(row_width=2)
    prev = types.InlineKeyboardButton('Вперед  ▶', callback_data='next_history')
    next = types.InlineKeyboardButton('◀️ Назад', callback_data='prev_history')
    products.add(next, prev)

    return products


def get_news():
    url = 'https://kazan-opera.ru/about/news/'
    url_n = 'https://kazan-opera.ru'
    news = []

    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    quotes_t = soup.find_all('p', class_='news-item__text')
    quotes_d = soup.find_all('p', class_='news-item__date')
    quotes_i = soup.find_all('a', class_='news-item__img-wrap')
    quotes_a = soup.find_all('div', class_='news-item')

    for i, quote in enumerate(quotes_t):
        news_ = quote.text.strip()
        news.append(f'{news_};')

    for i, quote in enumerate(quotes_d):
        news_ = quote.text.strip()
        news[i] = f'{news[i]}{news_};'

    for i, quote in enumerate(quotes_i):
        img = f"{url_n}{quote.find('img')['src']}"
        if '.png' in img or '.jpg' in img or '.JPG' in img or '.PNG' in img:
            news[i] = f'{news[i]}{img};'

    for i, quote in enumerate(quotes_a):
        news_url = f"{url_n}{quote.find('a')['href']}"
        news[i] = f'{news[i]}{news_url}'

    to_r = []
    for i in news:
        to_r.append(i.split(';'))
    return to_r


def get_timing():
    url = 'https://kazan-opera.ru/playbill/'
    news = []

    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html')
    quotes_t = soup.find_all('a', class_='poster-item__info-name')
    quotes_d = soup.find_all('span', class_='poster-item__date-number')
    quotes_m = soup.find_all('p', class_='poster-item__date-month')
    quotes_time = soup.find_all('p', class_='poster-item__date-day')
    for i, quote in enumerate(quotes_t):
        news_ = quote.text.strip()
        news.append(f'{news_}_')

    for i, quote in enumerate(quotes_d):
        news_ = quote.text.strip()
        news[i] = f'{news[i]}{news_}_'

    for i, quote in enumerate(quotes_m):
        news_ = quote.find('span').text.strip().lower()
        news[i] = f'{news[i]}{news_}_'

    for i, quote in enumerate(quotes_time):
        news_ = '_'.join(quote.text.strip().split())
        news[i] = f'{news[i]}{news_}'

    to_r = []
    for i in news:
        to_r.append(i.split('_'))
    print(to_r)
    return to_r


def cancel_review():
    markup = types.InlineKeyboardMarkup()
    cancel = types.InlineKeyboardButton(text='Отменить оформление ❌', callback_data='cancel_review')
    markup.add(cancel)

    return markup


def markup_confirm():
    markup = types.InlineKeyboardMarkup()
    ok = types.InlineKeyboardButton(text='Подтвердить ✅', callback_data='review_ok')
    bad = types.InlineKeyboardButton(text='Ввести номер заново ❌', callback_data='review_bad')
    markup.add(ok, bad)

    return markup


def markup_confirm_title():
    markup = types.InlineKeyboardMarkup()
    ok = types.InlineKeyboardButton(text='Подтвердить ✅', callback_data='review_title_ok')
    bad = types.InlineKeyboardButton(text='Ввести номер заново ❌', callback_data='review_title_bad')
    markup.add(ok, bad)

    return markup


def markup_confirm_text():
    markup = types.InlineKeyboardMarkup()
    ok = types.InlineKeyboardButton(text='Подтвердить ✅', callback_data='review_text_ok')
    bad = types.InlineKeyboardButton(text='Ввести номер заново ❌', callback_data='review_text_bad')
    markup.add(ok, bad)

    return markup


def markup_confirm_grade():
    markup = types.InlineKeyboardMarkup()
    ok = types.InlineKeyboardButton(text='Подтвердить ✅', callback_data='review_grade_ok')
    bad = types.InlineKeyboardButton(text='Ввести номер заново ❌', callback_data='review_grade_bad')
    markup.add(ok, bad)

    return markup


def markup_paymant_start():
    products = types.InlineKeyboardMarkup(row_width=2)
    next = types.InlineKeyboardButton('🎟 Купить билет', callback_data='start_pay')
    products.add(next)

    return products


def markup_confirm_event():
    markup = types.InlineKeyboardMarkup()
    ok = types.InlineKeyboardButton(text='Подтвердить ✅', callback_data='review_event_ok')
    bad = types.InlineKeyboardButton(text='Ввести номер заново ❌', callback_data='review_event_bad')
    markup.add(ok, bad)

    return markup


def success_markup():
    markup = types.InlineKeyboardMarkup()
    ok = types.InlineKeyboardButton(text='Оплачено ✅', callback_data='success')
    markup.add(ok)

    return markup


class Ratio():
    def __init__(self):
        self.base = {}

    def add(self, title, ratio):
        if title in list(self.base.keys()):
            self.base[title] = self.base[title], ratio
        else:
            self.base[title] = ratio

    def avg(self, title):
        if type(self.base[title]) == type(0):
            return self.base[title] / 1
        return sum(self.base[title]) / len(self.base[title])

    def write_to_json(self):
        with open('base.json', 'w') as f:
            json.dump(self.base, f)

    def read_json(self):
        try:
            with open('base.json', 'r') as f:
                data = json.load(f)
                self.base = data
        except Exception as e:
            print('READ_JSON', e)

    def top5(self):
        top = []
        for title in self.base.keys():
            top.append([title, self.avg(title)])
        top = sorted(top, key=lambda x: x[1], reverse=True)
        return top[:5]
