''' Посмотреть документацию к API GitHub, разобраться как вывести список репозиториев для конкретного
пользователя, сохранить JSON-вывод в файле *.json.'''

import requests
import json

login='lifefucky'
password=input('Press the password:')

r = requests.get('https://api.github.com/user/repos', auth=(login, password))

with open(login+'_public_repos.json', 'w', encoding='utf-8') as json_file:
    json.dump(r.json(), json_file, ensure_ascii=False, indent=4)

for repo in r.json():
    if not repo['private']:
        print(repo['name'])
