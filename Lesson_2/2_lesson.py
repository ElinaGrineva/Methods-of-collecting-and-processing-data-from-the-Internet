# https://spb.hh.ru/search/vacancy?area=2&fromSearchLine=true&st=searchVacancy&text=python

import requests
from bs4 import BeautifulSoup as bs
from pprint import pprint
import re
import json

url = 'https://spb.hh.ru'

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                         '(KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36'}

vacancies_list = []

# тянет максимум до 20 циклов.
for el in range(20):
    my_params = {'area': '2', 'fromSearchLine': 'true', 'st': 'searchVacancy', 'text': 'python', 'page': 0}
    my_params['page'] = el
    response = requests.get(url + '/search/vacancy/', params=my_params, headers=headers)
    soup = bs(response.text, 'html.parser')
    vacancies = soup.find_all('div', {'class': 'vacancy-serp-item'})

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

        vacancies_list.append(vacancies_data)

pprint(vacancies_list)

with open("vacancies_list.json", "w") as write_file:
    json.dump(vacancies_list, write_file)
