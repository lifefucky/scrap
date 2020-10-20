'''
Необходимо собрать информацию о вакансиях на вводимую должность (используем input или через аргументы) с
сайтов Superjob и HH. Приложение должно анализировать несколько страниц сайта (также вводим через input или аргументы).
Получившийся список должен содержать в себе минимум:
Наименование вакансии.
Предлагаемую зарплату (отдельно минимальную, максимальную и валюту).
Ссылку на саму вакансию.
Сайт, откуда собрана вакансия.
По желанию можно добавить ещё параметры вакансии (например, работодателя и расположение).
Структура должна быть одинаковая для вакансий с обоих сайтов. Общий результат можно вывести с помощью dataFrame
через pandas.'''

from bs4 import BeautifulSoup as bs
import requests
from pprint import pprint
job_title='повар'
main_link='https://hh.ru'
headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.80 Safari/537.36'}
href='/search/vacancy?clusters=true&area=1&search_field=name&enable_snippets=true&salary=&st=searchVacancy&text='+job_title
length = 200

def salary_to_dict(salary):
    dict = {'from': None, 'to': None, 'currency': None}
    dict0 = [f for f in salary.replace('-',' ').split(' ')]
    num = []
    for n in dict0:
        try:
            num.append(int(n.replace(u'\xa0', '')))
        except:
            pass
    if len(num)>1:
        dict['from']=num[0]
        dict['to']=num[1]
    elif dict0[0]=='от':
        dict['from']=num[0]
    else:
        dict['to']=num[0]
    dict['currency']=dict0[2]
    return dict

all_jobs = []
while True:
    response = requests.get(main_link+href,  headers=headers)
    soup =  bs(response.text, 'html.parser')
    try:
        href=soup.find('a',{'data-qa':'pager-next'})['href']
    except:
        print('didnt found href tag')
        break
    jobs_list = soup.findAll('div',{'data-qa':'vacancy-serp__vacancy'})
    all_jobs.extend(jobs_list)
    print(main_link + href+', found :'+str(len(jobs_list))+', total is:'+str(len(all_jobs)))
    if len(all_jobs)>length:
        all_jobs = all_jobs[:length]
        print('shortened list')
        break
    if len(jobs_list)==0:
        print('exceeds empty page')
        break


job = []
for jobs in all_jobs:
    job_data = {}
    job_name = jobs.find('a', {'data-qa': 'vacancy-serp__vacancy-title'})
    try:
        job_salary = jobs.find('span', {'data-qa': 'vacancy-serp__vacancy-compensation'}).getText()
        job_salary = salary_to_dict(job_salary)
    except:
        job_salary = {'from': None, 'to': None, 'currency': None}
    job_link = job_name['href']
    job_name = job_name.getText()

    emp_info = jobs.find('div', {'class':'vacancy-serp-item__meta-info'})
    emp_name = emp_info.find('a', {'data-qa': 'vacancy-serp__vacancy-employer'}).getText()
    try:
        emp_location = jobs.find('span', {'data-qa': 'vacancy-serp__vacancy-address'}).getText()
    except:
        emp_location = None

    job_data['name'] = job_name
    job_data['employer'] = emp_name
    job_data['location'] = emp_location
    job_data['salary'] = job_salary
    job_data['link'] = job_link
    print(job_data)
    job.append(job_data)


