import requests
import json

my_headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36'}

response = requests.get('https://api.github.com/users/ElinaGrineva/repos', headers=my_headers)

my_lst = []

if response.ok:
    j_data = response.json()
    for el in j_data:
        if not el['private']:
            my_lst.append(el['name'])

with open("data_file.json", "w") as write_file:
    json.dump(my_lst, write_file)