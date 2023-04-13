import telebot
from telebot import types
import time
import requests
from io import BytesIO
from PIL import Image
from bs4 import BeautifulSoup



TOKEN = '5303697194:AAGTRzvH-wnrn-OX3yqunEdNF5v1zheBamo'

client = telebot.TeleBot(TOKEN)


# Функция для получения изображения индекса страха и жадности
def get_fear_greed_index():
    url = 'https://invest-top.ru/indeks-straha-i-zhadnosti/'
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    img_url = soup.find('div', {'class': 'index-img'}).find('img')['src']
    response = requests.get(img_url)
    img = Image.open(BytesIO(response.content))
    return img


@client.message_handler(commands=['start'])
def answer(message):
    markup_inline = types.InlineKeyboardMarkup()
    item_index = types.InlineKeyboardButton(text='Индекс Страха и Жадности', callback_data='index')
    item_price = types.InlineKeyboardButton(text='Узнать цену входа', callback_data='price')
    markup_inline.add(item_price)
    markup_inline.add(item_index)
    client.send_message(message.chat.id, f"""Привет, нажми что тебе надо""", reply_markup=markup_inline)


@client.callback_query_handler(func=lambda call: True)
def get_user_info(call):
    if call.data == 'price':
        client.send_message(call.message.chat.id, "Напиши свои данные. Пример:\n"
                                                  "твх1\n"
                                                  "кол-во1\n"
                                                  "твх2\n"
                                                  "кол-во2")
    elif call.data == 'index':
        img = get_fear_greed_index()
        bio = BytesIO()
        img.save(bio, 'PNG')
        bio.seek(0)
        client.send_photo(call.message.chat.id, bio)

@client.message_handler(content_types=['text'])
def average_buy_price(message):
    a = message.text.split('\n')
    for i in range(len(a)):
        try:
            if '.' in a[i]:
                a[i] = float(a[i])
            elif ',' in a[i]:
                a[i] = float(a[i].replace(',', '.'))
            else:
                a[i] = int(a[i])
        except:
            client.send_message(message.chat.id, "Введен недопустимый символ")
    price1 = a[0]
    quantity1 = a[1]
    price2 = a[2]
    quantity2 = a[3]
    total_cost = price1 * quantity1 + price2 * quantity2
    total_quantity = quantity1 + quantity2
    average_price = total_cost / total_quantity
    client.send_message(message.chat.id, f"""Вот твоя средняя твх: {average_price}""")


def main():
    while True:
        try:
            client.polling(none_stop=True, interval=0)
        except Exception as e:
            print(e)
            time.sleep(3)


if __name__ == '__main__':
    main()
