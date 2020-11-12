import scrapy


class LeroymerlinSpider(scrapy.Spider):
    name = 'leroymerlin'
    allowed_domains = ['leroymerlin.ru']
    start_urls = ['http://leroymerlin.ru/']

    def parse(self, response):
        pass
