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

class vacancyTester:
    def request_worker(self, message, workers):
        message['event'] = {'type':'singleton', 'name':'config_tester','workers':workers}
        payload = json.dumps(message)
        postie = r.post('http://127.0.0.1:5000/api/v1/orchestrator/', data=payload)
        return postie.json()


configs = import_jsonfile('./uk_configs_2.0')
configs_combined = import_jsonfile('./uk_combined_02')
#print(configs[0])

# postbody = import_jsonfile('post_body')
# response = vacancyTester().request_worker(postbody,['selenium'])
# print(response)

message = import_jsonfile('post_body')
payload = json.dumps(message)
response = r.post('http://127.0.0.1:5000/api/v1/orchestrator/', data=payload)
print(response.json())
# all_configs = []
# for config in configs:
#     response = vacancyTester().request_worker(config, ['selenium'])
#     print(response)
#     break
#     if response['response']['status'] == False:
#         break
    # config.update(vacancy_unit['response']['results'])
    # all_configs.append(config)


'''
Example Input:
config = [
    {
        "name": "your_config_name",
        "country": "UK",
        "config": {
            "start_url": "your start_url",
            "vacancy_xc_path": "//*[@class=\"apply\"]/a",
            "function": "[\"\", \"catering\", \"facility\"]",
            "long_desc": "//*[@class=\"career_description\"][2]",
            "title": "//*[@class=\"career_title applysuggest\"]/parent::div",
            "location": "//*[@class=\"career_description\"][1]",
            "job_type": "//tr[contains(., \"Contract type\")]/td",
            "next_page_xc_path": "//*[@id=\"PaginationThePages\"]/a[last()]",
            "company": "company_name",
            "customer_name": "customer_name"
        }
    }
]
'''

### output?
## ./api/v1/vacancies/{Customer}/{Country}/{UUID}
