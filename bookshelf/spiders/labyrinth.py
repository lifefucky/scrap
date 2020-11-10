import scrapy
from scrapy.http import HtmlResponse
from bookshelf.items import BookshelfItem

class LabyrinthSpider(scrapy.Spider):
    name = 'labyrinth'
    allowed_domains = ['labirint.ru']
    start_urls = ['https://www.labirint.ru/books/?price_min=0']
    def parse(self, response: HtmlResponse):
        links = response.xpath("//div[contains(@data-title,'Все в жанре')]//a[@class='cover']/@href").extract()
        next_page = response.xpath("//div[@class='pagination-next']/a/@href").extract_first()
        main_mask = 'https://www.labirint.ru'
        for link in links:
            yield response.follow( main_mask+link, callback=self.vacancy_parse)
        if next_page:
            yield response.follow( 'https://www.labirint.ru/books/'+next_page.replace('amp;', ''), callback=self.parse)


    def vacancy_parse(self,response:HtmlResponse):
        name = response.xpath("//h1/text()").extract_first()
        author = response.xpath("//div[@class='authors']/a/text()").extract_first()
        basic_price = float(response.xpath("//div[@id='product-info']/@data-price").extract_first())
        actual_price = float(response.xpath("//div[@id='product-info']/@data-discount-price").extract_first())
        book_rate = float(response.xpath("//div[@id='rate']/text()").extract_first())
        link = response.url
        yield BookshelfItem(    name = name,
                                author = author,
                                basic_price = basic_price,
                                actual_price = actual_price,
                                book_rate =book_rate,
                                link =  link
                            )




