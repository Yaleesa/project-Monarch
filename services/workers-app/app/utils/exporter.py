
prety = {
    'id': xx,
    'country': xx,
    'config_name':xx,
    'company_name': xx,
    'vacancy_title':xx,
    'location':xx,
    'job_category':xx,
    'contract_type':xx,
    'introduction':xx,
    'description':xx,
}


class ElasticBulkExporter:
    def __init__(self, timestamp):
        self.elasticsearch = ['localhost:9200']
        self.es = self.init_elastic()
        self.timestamp = timestamp

    def init_elastic(self):
        es_settings = dict()
        es_settings['hosts'] = self.elasticsearch

        elastic = Elasticsearch(**es_settings)
        return elastic

    def indexed(self, item):
        self.items_list = []

        index_action = {
            '_index': f'vacancy_test-1',
            '_source': dict(item)
        }
        self.items_list.append(index_action)
        #logging.debug(self.items_list)
        try:
            helpers.bulk(self.es, self.items_list)
        except Exception as err:
            logging.error(err)
        return item

    def process_item(self, item):
        self.indexed(item)
        app.logger.info('Item sent to Elastic Search')
        return item
