from datetime import datetime
from elasticsearch import Elasticsearch, helpers
import json, ast, re
from scrapy.exporters import JsonItemExporter
import logging
import uuid

class ElasticSearchPipeline(object):
    def __init__(self, timestamp):
        self.elasticsearch = ['localhost:9200']
        self.es = self.init_elastic()
        self.timestamp = timestamp

    @classmethod
    def from_crawler(cls, crawler):
        timestamp = getattr(crawler.spider, 'timestamp')
        return cls(timestamp)

    def init_elastic(self):
        es_settings = dict()
        es_settings['hosts'] = self.elasticsearch

        elastic = Elasticsearch(**es_settings)
        return elastic

    def open_spider(self, spider):
        pass

    def indexed(self, item):
        self.items_list = []

        index_action = {
            '_index': f'scrapy_test-{self.timestamp}',
            '_type': 'eentype',
            '_source': dict(item)
        }
        self.items_list.append(index_action)
        #logging.debug(self.items_list)
        try:
            helpers.bulk(self.es, self.items_list)
        except Exception as err:
            logging.error(err)
        return item

    def process_item(self, item, spider):
        self.indexed(item)
        #logging.debug('Item sent to Elastic Search')
        return item

    def close_spider(self, spider):
        pass


class JsonLineWriterPipeline(object):

    def open_spider(self, spider):
        self.file = open('app/db/info_uk.jl', 'w')

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        line = json.dumps(dict(item)) + "\n"
        self.file.write(line)
        return item

class JsonWriterPipeline(object):

    def open_spider(self, spider):
        self.file = open("app/db/info_uk.json", 'wb')
        self.exporter = JsonItemExporter(self.file, encoding='utf-8', ensure_ascii=False)
        self.exporter.start_exporting()

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item

class Cleaner(object):

    def open_spider(self, spider):
        pass

    def close_spider(self, spider):
        pass

    def process_item(self, item, spider):
        for k,v in item.items():
            if k == 'function':
                v = ast.literal_eval(v)
            #item[k] = [x.strip() for x in v if isinstance(v, list)]
            if isinstance(v, list):
                subbed = [re.sub('<[^<]+?>', '', x) for x in v]
                item[k] = ' '.join([x.strip() for x in subbed])
            else:
                item[k] = v
            # if k == 'function':
            #     #print(type(v))
            #     veee = v.replace('[','').replace(']','').replace('"', '').replace(',','')
            #     item['function'] = veee
        return item

class ReadableNames(object):
        def open_spider(self, spider):
            pass

        def close_spider(self, spider):
            pass

        def process_item(self, item, spider):

            print(item)
            # prety_2d = {
            #     'id': uuid.uuid4(),
            #     'country': 'uk',
            #     'config_name': item['config_name'],
            #     'company_name': item['company'],
            #     'root_url': item['url'],
            #     'vacancy_title': item['title'],
            #     'location': item['location'],
            #     'job_category': item['function'],
            #     'contract_type': item['job_type'],
            #     'introduction': item['short_desc'],
            #     'description': item['long_desc']
            # }
            # item = prety_2d
            # print(item)
            return item

class Labelyzer(object):

    def open_spider(self, spider):
        self.file = open('uk_vacancies_labels.txt', 'a')

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        for k,v in item.items():
            #print("__label__" + k + " " + v)
            if k != 'url' and k != 'config_name' and v != "not-found":
                    self.file.write("__label__" + k + " " + v + "\n")

        return item


import pymongo

class MongoPipeline(object):

    collection_name = 'scrapy_items'

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE', 'items')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        self.db[self.collection_name].insert_one(dict(item))
        return item
