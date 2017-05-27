#!/usr/bin/env python
# -*- coding: utf-8 -*-


import urllib.request as urllib
from urllib.parse import quote
import json


def translate(text, lang_from='', lang_to='en'):
    translate_url_format = (u'https://translate.yandex.net/api/v1.5/tr.json/translate?' +
                            'key=trnsl.1.1.20161201T083155Z.b8169a9e91faf796.f3af7e6cbc625f5da83580a2b3c29dce04662d6f' +
                            '&text={}&lang={}{}&options=1')
    if lang_from != '':
        lang_from += '-'
    translate_url = urllib.urlopen(translate_url_format.format(quote(text),
                                                               lang_from,
                                                               lang_to))
    raw_url_data = translate_url.read()
    url_encoding = translate_url.info().get_content_charset('utf8')
    text_translate = json.loads(raw_url_data.decode(url_encoding))
    if 'text' in text_translate:
        return text_translate['text'][0]
    else:
        return ''
