import faust
from selenium import webdriver
import logging
import network_health


#from tests import write_jsonfile

from selenium.common.exceptions import WebDriverException
# logging.basicConfig(level=logging.DEBUG,
#                     format='%(asctime)s [%(levelname)s] %(message)s')
# logger = logging.getLogger(__name__)
#
# def file_reader():
#     with open('app/modules/schemafinder/Scraping_suggesties_nl.csv') as csvfile:
#         readCSV = csv.reader(csvfile, delimiter=',')
#         urls = [row[1] for row in readCSV]
#     return urls
#
# def to_kafka(urls):
#     for url in urls:
#         print(url)
# {"url":"https://werkenbijkfc.nl/vacatures/?formSubmit=true&formAction=Filter&vacancyType=&employment=Parttime"}


class SeleniumWorkerSession():
    # Connection to de Selenium Hub, which runs in a Docker container
    def __init__(self):
        self.driver = webdriver.Remote(
            command_executor='http://localhost:4444/wd/hub',
            desired_capabilities={
                "browserName": "chrome",
                'loggingPrefs': {'performance': 'ALL'}
            }
        )
        print('initiated driver')

    async def __aenter__(self):
        print('return driver')
        await self.driver

    async def __aexit__(self, type, value, traceback):
        print('Closing Driver')
        await self.driver.quit()


def SeleniumTaskHandler(url):
    try:
        with SeleniumWorkerSession() as browser:
            print('unit')
            browser.get(url)
            logger.info(browser.title)
            # return(browser.title)
            # browser.implicitly_wait(5)
        # browser.find_element_by_xpath('//h1')
    except Exception as err:
        logger.exception(err)


app = faust.App('scraper-ding', broker='kafka://localhost:29092')
source_topic = app.topic('input-scrape')
output_topic = app.topic('output-scrape')

# stream = app.stream(source_topic)  # or: my_topic.stream()
#
# @app.task
# async def on_started():
#     print('APP STARTED')
#     with SeleniumWorkerSession() as browser:
#         async for value in stream:
#             print(value)
#             browser.get(value['url'])
#             print(browser.title)

@app.agent(source_topic)
async def perform_crawl(configs):
    # async with SeleniumWorkerSession() as browser:
    async for config in configs:
        driver = webdriver.Remote(
            command_executor='http://localhost:4444/wd/hub',
            desired_capabilities={
                "browserName": "chrome",
                'loggingPrefs': {'performance': 'ALL'}
            }
        )

        print('in loop')
        health = network_health.check_hub()
        if health['ready']:
            url = config['url']
            driver.get(url)

            #1
            crawl_pagina = CrawlPage(ding)
            'pagina_data.akjfakfkajf'

            type(crawlPage)
            'ref:crawlPage'



            #2
            crawl_pagina = CrawlPage(ding)



class CrawlPage:
    topic.send(resultaten)



            # print(browser.title)
            # return 'done'

            #
            #
            # else:
            #     print('Hub full')
            #     return 'Hub full'
