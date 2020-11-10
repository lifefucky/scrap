import scrapy


import scrapy
from scrapy.http import HtmlResponse
from bookshelf.items import BookshelfItem


class BookSpider(scrapy.Spider):
    name = 'book24'
    allowed_domains = ['book24.ru']
    start_urls = ['https://book24.ru/best-price']



    def parse(self, response:HtmlResponse):
        links = response.xpath("//div[contains(@class, 'catalog-products__item')]//a[@data-element='image']/@href").extract()
        next_page = response.xpath("//button[contains(@class,'_load-more')]/@data-href").extract_first()
        main_mask = 'https://book24.ru'

        for link in links:
            yield response.follow( main_mask + link, callback=self.vacancy_parse)
        if next_page:
            yield response.follow( main_mask + next_page, callback=self.parse)



    def vacancy_parse(self,response:HtmlResponse):
        name = response.xpath("//h1/text()").extract_first()
        author = response.xpath("//a[@itemprop='author']/text() | //*[@itemprop='author']/@content").extract_first()
        basic_price = response.xpath("//div[@class ='item-actions__price-old']/text()").extract_first()
        try:
            basic_price = float(basic_price.replace(' р.', ''))
        except:
            pass
        actual_price = response.xpath("//div[@class='item-actions__price']/b/text()").extract_first()
        try:
            actual_price = float(actual_price)
        except:
            pass
        book_rate = response.xpath("//span[@class='rating__rate-value']/text()").extract_first()
        try:
            book_rate=float(book_rate.replace(',', '.'))
        except:
            pass
        link = response.url
        yield BookshelfItem(    name = name,
                                author = author,
                                basic_price = basic_price,
                                actual_price = actual_price,
                                book_rate =book_rate,
                                link =  link
                            )



