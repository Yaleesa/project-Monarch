import requests
from bs4 import BeautifulSoup
from lxml.html import parse, etree
import re
import json
from flask import current_app as app


user_header = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}

class APIRequester:
    def __init__(self):
        pass

    def request(self, message):
        url = message['url']
        response = {"requested_url": url}
        site = requests.get(url, headers=user_header)
        response['status_code'] = site.status_code
        if 'params' in message:
            if 'source' in message['params']:
                response['source'] = site.text

        return {'response_requests': response}





'''
Mini wiki

print(site.url)
soup = BeautifulSoup(site.content, 'html.parser')
unit = soup.find_all('a', href='')
links = [link.get('href') for link in unit if 'edit' not in link.get('href')]
soup = BeautifulSoup(site.content, 'html.parser')
title = soup.h1.a.text
table = soup.find('tbody')
table_rows = table.find_all('tr')
x = [td.text.strip() for td in row.find_all('td') if td.text.strip() and td.text.strip() != '']
output['config'].update({x[0]:x[1]})
cleaned1 = [re.sub(r"[\n\t\s]*", "", i) for i in row]
cleaned = list(filter(None, cleaned1))
'''
