# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

'''
Typical uses of item pipelines are:
    cleansing HTML data
    validating scraped data (checking that the items contain certain fields)
    checking for duplicates (and dropping them)
    storing the scraped item in a database
'''
# useful for handling different item types with a single interface

from pymongo import MongoClient

class BookshelfPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongobase = client['BookSpider']

    def process_item(self, item, spider):
        collection = self.mongobase[spider.name]
        collection.update_one({'link': item.get('link')}, {'$set': item},  upsert=True)
        return item


