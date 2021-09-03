from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from pymongo import MongoClient
import json

chrome_options = Options()
chrome_options.add_argument("--start-maximized")

driver = webdriver.Chrome(executable_path='/usr/local/bin/chromedriver', options=chrome_options)
driver.get('https://www.mvideo.ru')

client = MongoClient('127.0.0.1', 27017)
db = client['m_video_new_items']
m_video_new_items = db.m_video_new_items

page = driver.find_element_by_tag_name('html')
page.send_keys(Keys.END)

new = driver.find_element_by_xpath('//div[@class = "gallery-title-wrapper"]/h2[contains(text(), "Новинки")]/../../..//ul')
driver.execute_script("arguments[0].scrollIntoView();", new)
for el in range(7):
    el = page.send_keys(Keys.ARROW_UP)

next_button = new.find_element_by_xpath('//div[@class = "gallery-title-wrapper"]/h2[contains(text(), "Новинки")]/../../..//ul/../../a[contains(@class, "next-btn")]')

while 'disabled' not in next_button.get_attribute('class'):
    driver.execute_script("arguments[0].click();", next_button)

m_video_new_item = driver.find_elements_by_xpath('//div[@class = "gallery-title-wrapper"]/h2[contains(text(), "Новинки")]/../../..//ul/li[@class = "gallery-list-item"]')

for item in m_video_new_item:
    new_items_dict = {}
    url = item.find_element_by_tag_name('a').get_attribute('href')
    name = item.find_element_by_tag_name('a').get_attribute('data-track-label')
    price = float(json.loads(item.find_element_by_tag_name('a').get_attribute('data-product-info'))['productPriceLocal'])

    new_items_dict['url'] = url
    new_items_dict['name'] = name
    new_items_dict['price'] = price

    m_video_new_items.update_one({'url': url}, {'$set': new_items_dict}, upsert=True)

for item in m_video_new_items.find({}):
    print(item)
