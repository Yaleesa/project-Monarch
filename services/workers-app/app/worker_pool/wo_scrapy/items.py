import scrapy


class Vacancy(scrapy.Item):
    url = scrapy.Field()
    config_name = scrapy.Field()
    company_name = scrapy.Field()
    vacancy_title = scrapy.Field()
    introduction = scrapy.Field()
    contract_type = scrapy.Field()
    job_category = scrapy.Field()
    location = scrapy.Field()

class Vacancy_ugly(scrapy.Item):
    url = scrapy.Field()
    config_name = scrapy.Field()
    company = scrapy.Field()
    title = scrapy.Field()
    short_desc = scrapy.Field()
    long_desc = scrapy.Field()
    job_type = scrapy.Field()
    function = scrapy.Field()
    location = scrapy.Field()
