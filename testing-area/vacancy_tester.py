import requests as r

import time, json, csv, random

'''
This file is used to test the worker APP,
and is not a representation of the (future) real deal
'''

def import_jsonfile(path):
        with open(f'{path}.json', 'r') as f:
            return json.load(f)

def write_jsonfile(data, filename):
    with open(f"{filename}.json", "w+") as write_file:
        json.dump(data, write_file, ensure_ascii=False)

class vacancy:
    def request_links(self, message):
        message['event'] = {'type':'request_workers', 'workers':['selenium']}
        message['module'] = 'actionchain'
        payload = json.dumps(message)
        postie = r.post('http://127.0.0.1:5000/api/v1/orchestrator/', data=payload)
        return postie.json()

    def request_contents(self, message):
        message['event'] = {'type':'request_workers', 'workers':['scrapy']}
        message['module'] = 'actionchain'
        payload = json.dumps(message)
        postie = r.post('http://127.0.0.1:5000/api/v1/orchestrator/', data=payload)
        return postie.json()

    def request_source(self, message):
        message['event'] = {'type':'request_workers', 'workers':['requests']}
        message['module'] = 'actionchain'
        message['params'] = ['source']
        payload = json.dumps(message)
        postie = r.post('http://127.0.0.1:5000/api/v1/orchestrator/', data=payload)
        return postie.json()


configs = import_jsonfile('./uk_configs_2.0')
configs_combined = import_jsonfile('./uk_combined_02')
#print(configs[0])

response = vacancy().request_source({'url': 'http://digitaldirectory.nl'})
print(response)

# all_configs = []
# for config in configs:
#     response = vacancy().request_links(config)
#     print(response)
#     break
#     if response['response']['status'] == False:
#         break
    # config.update(vacancy_unit['response']['results'])
    # all_configs.append(config)




### output
## ./api/v1/vacancies/{Customer}/{Country}/{UUID}
