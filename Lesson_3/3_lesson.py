# https://spb.hh.ru/search/vacancy?area=2&fromSearchLine=true&st=searchVacancy&text=python

import requests
from bs4 import BeautifulSoup as bs
from pprint import pprint
import re
from pymongo import MongoClient

client = MongoClient('127.0.0.1', 27017)
db = client['vacancies']
jobs = db.jobs


url = 'https://spb.hh.ru'

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                         '(KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36'}

page = 0

while True:
    my_params = {'area': '2', 'fromSearchLine': 'true', 'st': 'searchVacancy', 'text': 'python', 'page': page}
    response = requests.get(url + '/search/vacancy/', params=my_params, headers=headers)
    soup = bs(response.text, 'html.parser')
    vacancies = soup.find_all('div', {'class': 'vacancy-serp-item'})
    page += 1
    if not soup.find(text='дальше'):
        break

    for vacancy in vacancies:
        vacancies_data = {}

        info = vacancy.find('a', {'class': 'bloko-link'})
        name = info.text
        link = info.get('href')
        try:
            salary = vacancy.find('div', {'class': 'vacancy-serp-item__sidebar'}).text
            number = re.findall('\d+', salary)

            if len(number) == 4:
                number_min = float(''.join(number[:2]))
                number_max = float(''.join(number[2:]))
            if len(number) == 2:
                if 'от ' in salary:
                    number_min = float(''.join(number[:2]))
                    number_max = None
                if 'до' in salary:
                    number_min = None
                    number_max = float(''.join(number[:2]))
            if len(number) < 2:
                number_min = None
                number_max = None

            if salary == '':
                salary = None

            if 'руб' in salary:
                currency = 'руб.'
            if 'USD' in salary:
                currency = 'долл. США'
            if 'EUR' in salary:
                currency = 'евро'

        except:
            salary = None
            currency = None
            number = None
            number_min = None
            number_max = None

        vacancies_data['Наименование вакансии'] = name
        vacancies_data['Ссылка на вакансию'] = link
        vacancies_data['Минимальная зарплата'] = number_min
        vacancies_data['Максимальная зарплата'] = number_max
        vacancies_data['Валюта'] = currency

        jobs.insert_many([vacancies_data])

        for item in jobs.find({}):
            pprint(item)


for item in jobs.find({}):
    pprint(item)

# 2. Написать функцию, которая производит поиск и выводит на экран вакансии с заработной платой больше введённой суммы.

for item in jobs.find({'Минимальная зарплата': {'$gt': 150000}}):
    pprint(item)

# 3. Написать функцию, которая будет добавлять в вашу базу данных только новые вакансии с сайта.

#  Это как вариант, но боюсь делать это ))
# jobs.update_many({}, {'$set': jobs.find({})}, upsert=True)