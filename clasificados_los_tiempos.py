import pandas as pd
import numpy as np
import requests
import json
import re
import math
from datetime import datetime
from pyquery import PyQuery as pq

MONTHS_SPANISH = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
BASE_URL = "https://clasificados.lostiempos.com"
URL = f"{BASE_URL}/inmuebles?sort_by=created&sort_order=DESC&page="
HEADERS = {'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) "
                         "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50"
                         ".0.2661.102 Safari/537.36"}

posts = []
response = requests.get(f"{URL}{0}", headers=HEADERS)
doc = pq(response.content)


def append_elements(doc, posts):
    l = doc.find('.views-row')
    for i, element in enumerate(l):
        data = get_data(element)
        posts.append(data)


# clean the text
def clean_text(s):
    return s.replace('\n', '').strip()


# get data from text like 'Publicado: 23 Marzo 2023'
def get_date(s):
    original_date = s.replace('Publicado: ', '')
    dt = original_date.split(' ')
    return f"{dt[2]}-{str(MONTHS_SPANISH.index(dt[1])).zfill(2)}-{dt[0].zfill(2)}"


# Get celphone and phone number 
def get_phones(s):
    return re.findall(r"([\d]{8}|[\d]{7})", s)


def get_price(s):
    # TODO: hacer el calculo de precios.
    pass


def get_data(element):
    if(len(element.getchildren()) == 6):
        title = element.getchildren()[0].text_content()
        date = element.getchildren()[1].text_content()
        description = element.getchildren()[2].text_content()
        price = element.getchildren()[3].text_content()
        keys = element.getchildren()[4].text_content()
        path = element.getchildren()[5].getchildren()[0].getchildren()[0].getchildren()[0].attrib['href']
    else:
        title = element.getchildren()[1].text_content()
        date = element.getchildren()[2].text_content()
        description = element.getchildren()[3].text_content()
        price = element.getchildren()[4].text_content()
        keys = element.getchildren()[5].text_content()
        path = element.getchildren()[6].getchildren()[0].getchildren()[0].getchildren()[0].attrib['href']
    return {
        'title': clean_text(title),
        'date': get_date(clean_text(date)),
        'description': clean_text(description),
        'price': clean_text(price),
        'keys': clean_text(keys),
        'path': clean_text(path),
    }


number_elements = int(re.findall(r'\d+', doc.find('.resume-search')[0].text_content())[0])
NUMBER_OF_PAGES = math.ceil(number_elements / 20)

print("total:", number_elements, "- paginas:", NUMBER_OF_PAGES)

append_elements(doc, posts)

for n in range(1, NUMBER_OF_PAGES):
    print("get data from:", f"{URL}{n}")
    response = requests.get(f"{URL}{n}", headers=HEADERS)
    doc = pq(response.content)
    append_elements(doc, posts)

print("total de publicaciones:", len(posts))