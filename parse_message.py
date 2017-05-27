#!/usr/bin/env python
# -*- coding: utf-8 -*-


import time
import re
import json

from string_text_requests_handlers import find_owm_name


def is_alpha(s):
    return s.isalpha() or s.replace('-', '').isalpha()


def return_month(msg_parts):
    months = ('january', 'jan', 'february', 'feb',
              'march', 'mar', 'april', 'apr', 'may', 'may',
              'june', 'jun', 'july', 'jul', 'august', 'aug',
              'september', 'sep', 'october', 'oct', 'november', 'nov',
              'december', 'dec')
    for month_index, month in enumerate(months):
        if month in msg_parts:
            if month_index < 18:
                return '0' + str(month_index // 2 + 1)
            return str(month_index // 2 + 1)


def return_forecast_time(msg_parts):
    time_words = {'morning': '09:', 'afternoon': '15:',
                  'evening': '18:', 'night': '21:'}
    for time_word in time_words:
        if time_word in msg_parts:
            msg_parts.remove(time_word)
            return msg_parts, time_words[time_word]
    return msg_parts, ''


def return_forecast_date(msg_parts, msg_date):
    seconds_per_day = 24 * 3600
    day_shift = 0
    msg_date_part = [part for part in msg_parts
                     if part != '' and not is_alpha(part)]
    for part in msg_date_part:
        msg_parts.remove(part)

    if 'tomorrow' in msg_parts or\
            (len(msg_date_part) == 0 and 'day' in msg_parts):
        if 'tomorrow' in msg_parts:
            msg_parts.remove('tomorrow')
        else:
            msg_parts.remove('day')
        day_shift = 1
    elif 'today' in msg_parts or 'now' in msg_parts:
        if 'today' in msg_parts:
            msg_parts.remove('today')
        else:
            msg_parts.remove('now')
        day_shift = 0
    elif len(msg_date_part) != 0:
        msg_date_part = msg_date_part[0]
        if len(msg_date_part) < 3:
            date_month = return_month(msg_parts)
            if date_month is not None:
                if len(msg_date_part) < 2:
                    msg_date_part = '0' + msg_date_part
                current_year = str(time.gmtime().tm_year)
                forecast_day = time.strptime(
                    msg_date_part + ' ' + date_month + ' ' + current_year,
                    '%d %m %Y')
                return msg_parts, time.strftime('%Y-%m-%d', forecast_day)
            else:
                day_shift = int(msg_date_part)
                if 'after' in msg_parts:
                    msg_parts.remove('after')
                elif 'in' in msg_parts:
                    msg_parts.remove('in')
                elif 'later' in msg_parts:
                    msg_parts.remove('later')
        else:
            return msg_parts, msg_date_part

    msg_date_since_epoch = time.mktime(msg_date)
    day_shift *= seconds_per_day
    forecast_day = time.strptime(time.ctime(msg_date_since_epoch + day_shift))

    return msg_parts, time.strftime('%Y-%m-%d', forecast_day)


def return_city(in_msg_parts):
    msg_parts = [part for part in in_msg_parts if is_alpha(part)]

    city_en = ''
    for part_index, part in enumerate(msg_parts):
        next_part = ''
        if part_index < len(msg_parts) - 1:
            next_part = part + ' ' + msg_parts[part_index + 1]

        with open('./cities/{}_cities.json'.format(part[0])) as cities_list:
            cities = json.load(cities_list)

        owm_city = find_owm_name(part, cities)
        if owm_city != '':
            city_en = part
        if next_part != '':
            owm_city = find_owm_name(next_part, cities)
            if owm_city != '':
                city_en = next_part

        if city_en != '':
            in_msg_parts.remove(part)
            if city_en == next_part:
                in_msg_parts.remove(msg_parts[part_index + 1])
            break

    return in_msg_parts, city_en


def return_country(in_msg_parts):
    msg_parts = [part for part in in_msg_parts if is_alpha(part)]

    with open('countries_iso_codes.json', 'r') as countries_list:
        countries = json.load(countries_list)

    country_en = ''
    for part_index, part in enumerate(msg_parts):
        next_part = ''
        if part_index < len(msg_parts) - 1:
            next_part = part + ' ' + msg_parts[part_index + 1]

        owm_country = find_owm_name(part, countries)
        if owm_country != '':
            country_en = part
        if next_part != '':
            owm_country = find_owm_name(next_part, countries)
            if owm_country != '':
                country_en = next_part

        if country_en != '':
            in_msg_parts.remove(part)
            if country_en == next_part:
                in_msg_parts.remove(msg_parts[part_index + 1])
            break

    return in_msg_parts, country_en

def return_message_sense_parts(msg, msg_date):
    number_words = ('one', 'two', 'three', 'four', 'five')
    parts = {}
    msg_parts = re.sub('[,?;]', ' ', msg)
    msg_parts = re.split('[\s]', msg_parts)
    parts['cond'] = msg_parts[-1]
    for number, number_word in enumerate(number_words):
        try:
            number_word_index = msg_parts.index(number_word)
            msg_parts[number_word_index] = str(number + 1)
        except:
            pass
    msg_parts, parts['city_en'] = return_city(msg_parts)
    msg_parts, parts['country_en'] = return_country(msg_parts)
    msg_parts, parts['date'] = return_forecast_date(msg_parts, msg_date)
    msg_parts, parts['time'] = return_forecast_time(msg_parts)
    return parts
