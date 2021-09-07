# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface

from itemadapter import ItemAdapter
from pymongo import MongoClient



class JobparserPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongo_base = client.vacancy0709

    def process_item(self, item, spider):
        if spider.name == 'hhru':
            item['min_salary'], item['max_salary'], item['currency'] = self.process_salary_hh(item['salary'])
        else:
            item['min_salary'], item['max_salary'], item['currency'] = self.process_salary_sj(item['salary'])
            item['salary'] = ''.join(item['salary'])
        collection = self.mongo_base[spider.name]
        collection.insert_one(item)
        return item

    def process_salary_hh(self, salary):
        '''Обработка зарплаты у вакансии'''
        min_salary = []
        max_salary = []
        salary = salary.replace('\xa0', '')
        if '–' in salary or '-' in salary or ('от' in salary and 'до' in salary):
            salary_next_index = 0
            for ind, i in enumerate(salary.replace('от', '').strip()):
                if i.isdigit():  # and i != '-' and i != '–' and i != 'до':
                    min_salary.append(i)
                else:
                    salary_next_index = ind
                    break
            for i in salary[salary_next_index:]:
                if i.isdigit():
                    max_salary.append(i)
        elif salary.strip() == '':
            min_salary = None
            max_salary = None
            currency = None
        else:
            if 'до' in salary:
                for i in salary:
                    if i.isdigit():
                        max_salary.append(i)
            else:
                for i in salary:
                    if i.isdigit():
                        min_salary.append(i)
        if salary != '':
            currency = salary.split()[-1]
        if min_salary != None and min_salary != []:
            min_salary = int(''.join(min_salary))
        else:
            min_salary = None
        if max_salary != None and max_salary != []:
            max_salary = int(''.join(max_salary))
        else:
            max_salary = None
        return min_salary, max_salary, currency

    def process_salary_sj(self, salary):
        # Обработка зп у вакансии sj
        if salary == [''] or salary == ['По договорённости'] or salary == []:
            currency = None
            min_salary = None
            max_salary = None
        else:
            currency = 'руб.'
            min_salary = None
            max_salary = None
            for i in range(len(salary)):
                salary[i] = salary[i].replace('\xa0', '')
            if '—' in salary:
                min_salary = int(salary[0])
                max_salary = int(salary[4])
            elif 'от' in salary:
                dig_salary = []
                for j in salary[2]:
                    if j.isdigit():
                        dig_salary.append(j)
                min_salary = int(''.join(dig_salary))
            elif 'до' in salary:
                dig_salary = []
                for j in salary[2]:
                    if j.isdigit():
                        dig_salary.append(j)
                max_salary = int(''.join(dig_salary))
        return min_salary, max_salary, currency
