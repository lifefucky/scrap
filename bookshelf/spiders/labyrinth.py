import scrapy


class LabyrinthSpider(scrapy.Spider):
    name = 'labyrinth'
    allowed_domains = ['labirint.ru']
    start_urls = ['http://labirint.ru/']

    def parse(self, response):
        pass
