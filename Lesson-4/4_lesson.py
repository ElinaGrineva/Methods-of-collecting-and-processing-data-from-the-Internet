from lxml import html
import requests
from pymongo import MongoClient
from pprint import pprint

client = MongoClient('127.0.0.1', 27017)
db = client['news']
news = db.news

header = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36'}

response = requests.get('https://lenta.ru', headers=header)

dom = html.fromstring(response.text)

items = dom.xpath("//section[contains(@class, 'b-top7-for-main')]/div[@class='span4']/div[@class='first-item']/h2|"
                  "//section[contains(@class, 'b-top7-for-main')]/div[@class='span4']/div[@class='item']")


items_list = []
for item in items:
    items_data = {}

    name = item.xpath("./a/text()")[0].replace('\xa0', ' ')
    link = item.xpath("./a/@href")[0]
    if link[0] == '/':
        link = f'{"https://lenta.ru"}{link}'
        source = 'Лента.ру'
    else:
        source = 'Мослента.ру' # я проверила, другие источники не появлялись.
    date = item.xpath(".//time[@class='g-time']//@datetime")[0]

    items_data['name'] = name
    items_data['link'] = link
    items_data['date'] = date
    items_data['source'] = source

    items_list.append(items_data)

    news.update_one({'name': items_data['name']}, {'$set': items_data},
                    upsert=True)

for item in news.find({}):
    pprint(item)

