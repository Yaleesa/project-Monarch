from scrapy.http.request import Request

class StartRequestsCountMiddleware(object):

    start_urls = {}

    def process_start_requests(self, start_requests, spider):
        for i, request in enumerate(start_requests):
            self.start_urls[i] = request.url
            request.meta.update(start_request_index=i)
            yield request

    def process_spider_output(self, response, result, spider):
        for output in result:
            if isinstance(output, Request):
                output.meta.update(
                    start_request_index=response.meta['start_request_index'],
                )
            else:
                spider.crawler.stats.inc_value(
                    'start_requests/item_scraped_count/{}'.format(
                        self.start_urls[response.meta['start_request_index']],
                    ),
                )
            yield output
