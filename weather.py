#!/usr/bin/env python
# -*- coding: utf-8 -*-


import urllib.request as urllib
import json
import os

from string_text_requests_handlers import find_owm_name


def deg_to_dir(dir_degree):
    deg_to_dir_def = {
        'С': (348.75, 360 + 11.25),
        'СВ': (11.25, 78.75),
        'В': (78.75, 101.25),
        'ЮВ': (101.25, 168.75),
        'Ю': (168.75, 191.25),
        'ЮЗ': (191.25, 258.75),
        'З': (258.75, 281.25),
        'СЗ': (281.25, 348.76)
    }
    if dir_degree < 11.25:
        dir_degree += 360

    for wdir in deg_to_dir_def.keys():
        if deg_to_dir_def[wdir][0] <= dir_degree < deg_to_dir_def[wdir][1]:
            return wdir


def return_forecast_day(forecast_list, day='', daytime=''):
    if day == '' and daytime != '':
        for local_forecast in forecast_list:
            if daytime in local_forecast['dt_txt']:
                return local_forecast
    elif day != '' and daytime == '':
        for local_forecast in forecast_list:
            if day in local_forecast['dt_txt']:
                return local_forecast
    else:
        for local_forecast in forecast_list:
            if day in local_forecast['dt_txt'] and\
                    daytime in local_forecast['dt_txt']:
                return local_forecast
    return forecast_list[0]


class Weather(object):
    def __init__(self, city, country='', home_country=''):
        self.city = city.lower()
        self.country = country.lower()
        self.home_country = home_country.lower()
        self.weather_query_format = 'http://api.openweathermap.org/data/2.5/forecast?id={}&APPID=14b5109c8e2d86a0218fd3f81400dd10'
        self.conditions = {}

    def get_weather(self, day='', daytime=''):
        kelvin_shift = 273
        celsius_grad = '°C'
        city_file = './cities/{}_cities.json'.format(self.city[0])

        if not os.path.exists(city_file):
            return "Something bad happened, there's no such city in the list'"
        with open(city_file) as cities_list:
            cities_ids = json.load(cities_list)
        owm_city_name = find_owm_name(self.city, cities_ids)
        if owm_city_name == '':
            return 'Could not find the city!'

        with open('countries_iso_codes.json', 'r') as countries_file:
            countries_codes = json.load(countries_file)
        city_id = ''
        if self.country != '':
            owm_country_name = find_owm_name(self.country, countries_codes)
            if owm_country_name == '':
                return 'Could not find the country!'
            country_code = countries_codes[owm_country_name]
            if country_code in cities_ids[owm_city_name]:
                city_id = cities_ids[owm_city_name][country_code]
        if city_id == '':
            country_code = list(cities_ids[owm_city_name].keys())[0]
            city_id = cities_ids[owm_city_name][country_code]
            with open('iso_codes_to_countries.json', 'r') as countries_file:
                codes_list = json.load(countries_file)
            owm_country_name = codes_list[country_code]
            if len(cities_ids[owm_city_name]) > 1:
                self.conditions['warning'] =\
                    'there are many cities with this name, taking any of them'
                if self.home_country != '':
                    owm_home_country_name =\
                        find_owm_name(self.home_country, countries_codes)
                    if owm_home_country_name != '':
                        country_code = countries_codes[owm_home_country_name]
                        if owm_home_country_name != '' and\
                              country_code in cities_ids[owm_city_name]:
                            self.conditions.pop('warning')
                            city_id = cities_ids[owm_city_name][country_code]
                            owm_country_name = owm_home_country_name
        try:
            city_forecast_url =\
                urllib.urlopen(self.weather_query_format.format(city_id))
        except:
            return 'Could not get the forecast!'
        self.conditions['country'] = owm_country_name

        raw_forecast = city_forecast_url.read()
        # JSON default
        url_encoding = city_forecast_url.info().get_content_charset('utf8')
        forecast = json.loads(raw_forecast.decode(url_encoding))
        forecast = return_forecast_day(forecast['list'], day, daytime)

        if 'main' not in forecast:
            return 'Could not get the forecast!'

        if 'temp' in forecast['main'] and forecast['main']['temp'] is not None:
            self.conditions['temperature'] =\
                str(int(forecast['main']['temp'] - kelvin_shift)) +\
                celsius_grad
        if 'wind' in forecast:
            if 'speed' in forecast['wind'] and\
                    forecast['wind']['speed'] is not None:
                self.conditions['wind_speed'] = str(forecast['wind']['speed'])
            if 'deg' in forecast['wind'] and\
                    forecast['wind']['deg'] is not None:
                self.conditions['wind_direction'] =\
                    deg_to_dir(forecast['wind']['deg'])
        if 'weather' in forecast and\
                len(forecast['weather']) != 0 and\
                'description' in forecast['weather'][0]:
            self.conditions['description'] =\
                forecast['weather'][0]['description']
        if 'rain' in forecast and\
                '3h' in forecast['rain'] and\
                forecast['rain']['3h'] is not None:
            self.conditions['rain'] = forecast['rain']['3h']
        elif 'snow' in forecast and\
                  '3h' in forecast['snow'] and\
                  forecast['snow']['3h'] is not None:
            self.conditions['snow'] = forecast['snow']['3h']
        self.conditions['date'] = forecast['dt_txt'].split()[0]

        city_forecast_url.close()


if __name__ == '__main__':
    weather = Weather('moscow', 'russia')
    weather.get_weather(daytime='09')
    print(weather.conditions)
    weather.get_weather()
    print(weather.conditions)
