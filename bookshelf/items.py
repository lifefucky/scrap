# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

#PLACE TO EXTRACT STRUCTURED DATA FROM UNSTRUCTURED SOURCES

import scrapy


class BookshelfItem(scrapy.Item):
    # define the fields for your item here like:
    _id = scrapy.Field()
    name = scrapy.Field()
    author = scrapy.Field()
    basic_price = scrapy.Field()
    actual_price = scrapy.Field()
    book_rate = scrapy.Field()
    link = scrapy.Field()
    pass
