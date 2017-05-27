#!/usr/bin/env python
# -*- coding: utf-8 -*-


import telebot
import numpy.random as random
import time
import sys
from requests import exceptions as req_exceptions

from weather import Weather
from google import google_image
from yandex_translate import translate
from string_text_requests_handlers import get_poem
from string_text_requests_handlers import date_to_season
from parse_message import return_message_sense_parts


token = '311170855:AAHBaYI8Fin2obVg-9JzXvDZn9_xhrMUmpQ'
bot = telebot.TeleBot(token)
init_country = ''
init_country_en = ''
getting_country = False


def send_error_msg(chat_id):
    err_msg = \
        'Не могу найти запрос в базе OpenWeather. Попробуйте ещё раз :)'
    bot.send_message(chat_id, err_msg)


@bot.message_handler(commands=['start', 'country'])
def handle_start_help(message):
    hello_msg = ''
    if 'start' in message.text:
        hello_msg = "Доброго времени суток!\n"
    hello_msg += "Введите полное название страны, в которой вы находитесь:"
    globals()['getting_country'] = True
    globals()['init_country'] = ''
    bot.send_message(message.chat.id, hello_msg)


@bot.message_handler(commands=['help'])
def handle_start_help(message):
    help_msg =\
        ('Введите название города и день, чтобы получить прогноз погоды.' +
            '\nМожно узнать прогноз погоды не более чем на 5 дней вперёд.' +
            'Формат даты: гггг-мм-дд.'
            '\nПо умолчанию выдаётся прогноз погоды на сегодня.' +
            '\nЧтобы сменить страну, введите /country')
    bot.send_message(message.chat.id, help_msg)


@bot.message_handler(content_types=['text'])
def listener(message):
    if globals()['getting_country']:
        globals()['getting_country'] = False
        globals()['init_country'] = message.text.lower()
        globals()['init_country_en'] = translate(message.text).lower()
        hello_msg_continue =\
            'Введите команду /help для получения дополнительной информации'
        bot.send_message(message.chat.id, hello_msg_continue)
        return
    try:
        chat_id = message.chat.id
        # print(chat_id)
        msg_date = time.strptime(time.ctime(message.date))
        en_msg_text = translate(message.text).lower()
        if en_msg_text == '':
            return send_error_msg(chat_id)

        msg_parts = return_message_sense_parts(en_msg_text, msg_date)
        forecast_date = msg_parts['date']
        forecast_time = msg_parts['time']
        city_en = msg_parts['city_en']
        country_en = msg_parts['country_en']
        cond = msg_parts['cond']
        print (cond)
        if city_en == '':
            return send_error_msg(chat_id)

        weather = Weather(city_en, country_en, globals()['init_country_en'])
        if isinstance(weather.get_weather(forecast_date, forecast_time), str):
            error_msg =\
                'Не могу найти запрос в базе OpenWeather. Попробуйте ещё раз :)'
            bot.send_message(message.chat.id, error_msg)
            return
        # print("Got the forecast!", file=sys.stderr)

        if weather.conditions['country'] != '':
            country_en = weather.conditions['country'].lower()
        country_ru = ''
        if country_en != '':
            country_ru = ', ' + translate(country_en, 'en', 'ru')
        city_ru = translate(city_en, 'en', 'ru')
        weather_forecast = 'Прогноз погоды на ' + weather.conditions['date'] +\
                           ', ' + city_ru + country_ru + ':\n'
        description_ru =\
            translate(weather.conditions['description'], 'en', 'ru')

        weather_forecast += description_ru + ', '
        if 'temperature' in weather.conditions:
            weather_forecast += weather.conditions['temperature']
        if 'wind_speed' in weather.conditions:
            weather_forecast += ', ветер, м/с: ' + weather.conditions['wind_speed']
            if 'wind_direction' in weather.conditions:
                weather_forecast += ', ' + weather.conditions['wind_direction']

        default_conditions = {
            'snow': 'снег',
            'rain': 'дожд',
            'sun': 'солнц',
            'cloud': 'облак',
            'sky': 'неб'
        }
        conditions = ''
        for weather_feature in default_conditions:
            if weather_feature in weather.conditions['description']:
                conditions = conditions + ' ' + weather_feature

#        poem = ''
#        if len(conditions) != 0:
#            poem_condition = default_conditions[conditions.split()[0]]
#            poem = get_poem(poem_condition)
#        else:
#            print('No such weather conditions!\n',
#                  weather.conditions['description'],
#                  file=sys.stderr)

        poem = 'a'
        season = date_to_season(weather.conditions['date'])
        need_cats = 1
        if poem != '':
            need_cats = random.binomial(1, 0.153)
        image_query = 'cute cats ' * need_cats +\
                      (city_en + ' city ' +
                       country_en + ' ' + season) *\
                      (1 - need_cats) + ' ' + conditions
        images_amount = google_image(image_query, 3)
        # print("Googled images!", file=sys.stderr)

        images_indexes = list(range(images_amount))
        images_counter = random.choice(images_indexes)
        images_indexes.remove(images_counter)
        while images_counter < images_amount:
            try:
                image = open('./images/image_{}.jpg'.format(images_counter), 'rb')
                break
            except IOError:
                print('cannot open the image, trying more...')
                if len(images_counter) == 0:
                    images_counter = images_amount
                    break
                images_counter = random.choice(images_indexes)
                images_indexes.remove(images_counter)
        # print("Opened image!", file=sys.stderr)

        warning_msg = ''
        if 'warning' in weather.conditions:
            warning_msg = '(Нашлось несколько городов с таким названием!)\n\n'
        bot.send_message(chat_id,
                         warning_msg + weather_forecast + '\n\n' +
                         'All you need is cats!' * need_cats +
                         poem * (1 - need_cats))
        bot.send_chat_action(chat_id, 'upload_photo')
        if cond == '1':
            if images_counter < images_amount:
                bot.send_photo(chat_id, image, reply_to_message_id=message.message_id)
                image.close()
            else:
                bot.send_message(chat_id, 'Загрузить картинку не получилось :(')
    except ConnectionError:
            bot.send_message(chat_id,
                             'Соединение было прервано, попробуйте ещё раз')


if __name__ == '__main__':
    error_report_chat_id = 99901662
    while True:
        try:
            bot.polling(none_stop=True)
        except req_exceptions.Timeout:
            bot.send_message(error_report_chat_id, "Timeout occurred")
