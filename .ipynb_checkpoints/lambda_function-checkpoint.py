import json
import re
import math
import requests
import boto3
import pandas as pd
from datetime import datetime
from bs4 import BeautifulSoup
from pytz import timezone

def lambda_handler(event, context):
    
    # CONSTANTS

    BASE_URL = "https://clasificados.lostiempos.com"
    URL = f"{BASE_URL}/inmuebles?sort_by=created&sort_order=DESC&page="
    
    HEADERS = {'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) "
                             "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50"
                             ".0.2661.102 Safari/537.36"}
    posts = []
    
    MONTHS_SPANISH = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]

    response = requests.get(f"{URL}{0}", headers=HEADERS)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # METHODS
    
    def append_elements(doc, posts):
        l = soup.find_all(class_='views-row')
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

    def get_data(element):
        title = element.find(class_='title').text
        date = element.find(class_='publish-date').text
        description = element.find(class_='body').text
        price = element.find(class_='ads-price').text
        keys = element.find(class_='description').text
        path = element.find(class_='title').find('a')['href']
    
        return {
            'title': clean_text(title),
            'date': get_date(clean_text(date)),
            'description': clean_text(description),
            'price': clean_text(price),
            'keys': clean_text(keys),
            'path': clean_text(path),
        }

    # Get the number of pages
    
    number_elements = int(re.findall(r'\d+', soup.find(class_='resume-search').text)[0])
    NUMBER_OF_PAGES = math.ceil(number_elements / 20)

    # Scraping each page

    for n in range(1, NUMBER_OF_PAGES):
        print("get data from:", f"{URL}{n}")
        response = requests.get(f"{URL}{n}", headers=HEADERS)
        soup = BeautifulSoup(response.content, 'html.parser')
        append_elements(soup, posts)
    
    print("total de publicaciones:", len(posts))


    # Upload JSON String to an S3 Object
    client = boto3.client('s3')
    
    data_string = json.dumps(posts, indent=2, default=str)
    
    client.put_object(
        Bucket='s3-lostiempos-data', 
        Key=f'json/los_tiempos_clasificados_{datetime.now(timezone("US/Eastern")).isoformat()[:10]}.json',
        Body=data_string
    )

    return {
        'statusCode': 200,
        'body': json.dumps('Done!')
        
    }
