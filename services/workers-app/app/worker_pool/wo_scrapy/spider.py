import scrapy
from scrapy.crawler import CrawlerProcess
from twisted.internet import reactor, defer
from scrapy import Selector
import json, logging, datetime
from scrapy.crawler import CrawlerRunner
import asyncio

from app.worker_pool.wo_scrapy.items import Vacancy
from app.worker_pool.wo_scrapy.items import Vacancy_ugly
#from app.worker_pool.wo_scrapy import pipelines

from flask_restplus import Namespace, Resource, fields
worker = Namespace('workers', description='busy busy beee beee')


class vacancy_spider(scrapy.Spider):
    def __init__(self, *args, **kwargs):
        super(vacancy_spider, self).__init__(*args, **kwargs)
        self.urls = kwargs.get('urls')
        self.config = kwargs.get('config')
        self.name = kwargs.get('config_name')


    name = 'vacancyspider'
    custom_settings = {
        'ITEM_PIPELINES': {
            #'app.workers.wo_scrapy.pipelines.ElasticSearchPipeline': 400
            'app.worker_pool.wo_scrapy.pipelines.Cleaner': 100,
            'app.worker_pool.wo_scrapy.pipelines.ReadableNames': 110,
            'app.worker_pool.wo_scrapy.pipelines.Labelyzer': 200,
            #'app.worker_pool.wo_scrapy.pipelines.JsonLineWriterPipeline': 300,
            'app.worker_pool.wo_scrapy.pipelines.ElasticSearchPipeline': 400,

        },
        'SPIDER_MIDDLEWARES': {
        # 'app.workers.wo_scrapy.middlewares.StartRequestsCountMiddleware': 200,
        }
    }
    def start_requests(self):
        urls = self.urls
        logging.warning(f'url length: {len(urls)}')
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        item = Vacancy_ugly()
        item['url'] = response.request.url
        item['config_name'] = self.name
        for key, value in self.config.items():
            if value.startswith('/'):
                if '/text()' not in value and not value.endswith(')'):
                    value = value + '//text()'

                pre_item = response.xpath(value).getall()
                pre2_item = pre_item
                if pre2_item == '':
                    pre_item = response.xpath(f'normalize-space({value})').getall()
                item[key] = pre_item

            elif value.endswith(')'):
                pre_item = response.xpath(value).getall()
                print(pre_item)
                pre2_item = pre_item
                if pre2_item == '':
                    pre_item = response.xpath(f'normalize-space({value})').getall()

                item[key] = pre_item
            else:
                item[key] = value
        return item

class TestSpider(scrapy.Spider):
    name = 'quotes'
    start_urls = [
        'http://quotes.toscrape.com/tag/humor/',
    ]

    def parse(self, response):
        for quote in response.css('div.quote'):
            yield {
                'text': quote.css('span.text::text').get(),
                'author': quote.xpath('span/small/text()').get(),
            }

        next_page = response.css('li.next a::attr("href")').get()
        if next_page is not None:
            yield response.follow(next_page, self.parse)

@worker.route('/test')
class ScrapyRunner(Resource):
    #@defer.inlineCallbacks
    def get(self):
        runner = CrawlerRunner({
            'USER_AGENT': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'
        })
        timestamp = 'unit'

        # counter = 0
        # counter += len(data['links'])
        # poplist = ['start_url', 'vacancy_xc_path', 'next_page_xc_path', 'apply_url', 'customer_name']
        # unit = {data['config'].pop(key) for key in poplist if key in data['config'].keys()}
        # logging.warning(f"amount of links in config_lijst: {len(data['links'])}")
        # print(counter)
        #runner.crawl(vacancy_spider, config_name=data['name'], urls=data['links'], config=data['config'], timestamp=self.timestamp)
        yield runner.crawl(TestSpider)
        reactor.stop()
        return {'response_scrapy': 'yoo'}


#reactor.run()



# now = datetime.datetime.now()
# timestamp = now.strftime('%m%d%y%H%M%S')
