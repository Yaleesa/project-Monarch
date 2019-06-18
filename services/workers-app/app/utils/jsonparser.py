import time, json, pprint, ast, csv, os
import requests as r


def write_jsonfile(data, filename, type):
    with open(f"{filename}.json", type) as write_file:
        json.dump(data, write_file, ensure_ascii=False)

def import_jsonfile(path):
        with open(f'{path}.json', 'r') as f:
            return json.load(f)
