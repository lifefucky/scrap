import requests
import json

access_token=#YOUR TOKEN
userid=#YOUR USER ID

r = requests.get('https://api.vk.com/method/groups.get?access_token='+access_token+'&user_id='+userid+'&extended=1&fields=name&v=5.103')

data = json.loads(r.text)

for i in data['response']['items']:
    print(i['name'])

