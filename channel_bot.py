import telebot
from bs4 import BeautifulSoup
import requests
from time import sleep

bot = telebot.TeleBot('1778803722:AAH3lIhQmiP6c84pPxyUJfEb8UHVKAUFrc8')
chat_id = -1001197322364
last_news = ''
url = 'https://culture.gov.ru/press/news/'


while True:
    url_n = 'https://culture.gov.ru'

    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    quotes_t = soup.find_all('div', class_='b-default__title')
    if quotes_t[0].text.strip() != last_news:
        quotes_d = soup.find_all('div', class_='b-article__date')
        quotes_i = soup.find_all('div', class_='b-news-list__cover')
        quotes_a = soup.find_all('a', class_='b-news-list__item')

        last_news = quotes_t[0].text.strip()
        image = url_n + quotes_i[0]['style'][23:-2]
        a = url_n + quotes_a[0]['href']
        date = quotes_d[0].text.strip()

        msg = f'{last_news}\n\n'
        msg += f'{a}\n'
        msg += f'{date}'
        bot.send_photo(chat_id, image, caption=msg)

    sleep(5)
