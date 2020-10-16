import requests
from getpass import getpass


login='lifefucky'
password=input('Press the password:')

r = requests.get('https://api.github.com/user/repos', auth=(login, password))
for repo in r.json():
    if not repo['private']:
        print(repo['name'])
