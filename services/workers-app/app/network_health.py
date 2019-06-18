import time, os
import json, pprint, ast
import csv
import requests
from app.config import config



def check_hub():
    #check the hub for open capacity
    try:
        hub_status = requests.get(config['selenium']['status']).json()
        return {'ready': hub_status['value']['ready'], 'message': hub_status['value']['message']}
    except requests.exceptions.RequestException as err:
        return {'ready': False, 'message': 'No response from Selenium Hub, is the service running? check docker'}
