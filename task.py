'''Написать приложение, которое собирает основные новости с сайтов news.mail.ru, lenta.ru, yandex-новости.
Для парсинга использовать XPath. Структура данных должна содержать:
название источника;
наименование новости;
ссылку на новость;
дата публикации.
Сложить собранные данные в БД'''


from lxml import html
import requests
from pymongo import MongoClient

client = MongoClient('127.0.0.1', 27017)
db = client['news']
collection = db['news_list']

header = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36'}

def db_insert_not_exists(cond, data):
    '''Function inserts data to chosen collection if not already exists'''
    collection.update_one(cond, {'$set': data}, upsert=True)

'''news.mail.ru module'''
main_link='https://news.mail.ru/'
response =requests.get(main_link, headers=header)
dom = html.fromstring(response.text)
news = dom.xpath("//div[contains(@class, 'daynews__item')] | //a[@class='list__text']")

cnt = 0
for i in news:
    news_data = {}
    title =''.join([a.replace('\xa0',' ') for a in i.xpath(".//text()")])
    link = i.xpath(".//@href")[0]

    response =requests.get(link, headers=header)
    dom2 = html.fromstring(response.text)
    timer = dom2.xpath(".//span[contains(@class,'js-ago')]//@datetime")[0]
    source = ''.join(dom2.xpath("//a[contains(@class, 'breadcrumbs__link')]/*/text()"))

    news_data['title'] = title
    news_data['link'] = link
    news_data['datetime'] = timer
    news_data['source'] = source
    db_insert_not_exists({'link': news_data.get('link')}, news_data)
    cnt+=1
print('First source - '+str(cnt))
'''lenta.ru module'''
main_link='https://lenta.ru'
response =requests.get(main_link, headers=header)
dom = html.fromstring(response.text)
news = dom.xpath("//div[@class='first-item']/*/a | //div[contains(@class,'js-main__content')]/*//div[@class='item']/a")

cnt = 0
for i in news:
    news_data = {}

    title = ''.join([a.replace('\xa0', ' ') for a in i.xpath("./text()")])
    link = main_link+i.xpath("./@href")[0]
    timer = i.xpath("./time/@datetime")[0]

    news_data['title'] = title
    news_data['link'] = link
    news_data['datetime'] = timer
    news_data['source'] = 'Lenta.ru'
    db_insert_not_exists({'link': news_data.get('link')}, news_data)
    cnt+=1
print('Second source - '+str(cnt))
'''yandex news module'''

main_link='https://yandex.ru/news'
response =requests.get(main_link, headers=header)
dom = html.fromstring(response.text)
news = dom.xpath("//div[contains(@class,'news-top-stories')]/div[contains(@class,'mg-grid__col')]")

cnt=0
for i in news:
    news_data = {}

    title = i.xpath(".//a[@rel]//text()")[0]
    link = i.xpath(".//a[@rel]/@href")[0]

    source =  i.xpath(".//div[contains(@class, 'news-card__source')]//span[contains(@class,'mg-card-source__source')]/a/text()")
    timer = i.xpath(".//div[contains(@class, 'news-card__source')]//span[contains(@class,'mg-card-source__time')]/text()")

    news_data['title'] = title
    news_data['link'] = link
    news_data['datetime'] = timer
    news_data['source'] = source
    db_insert_not_exists({'link': news_data.get('link')}, news_data)
    cnt += 1
print('Third source - '+str(cnt))

