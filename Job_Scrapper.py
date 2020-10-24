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
import pandas as pd

def salary_to_dict_HH(salary):
    '''Function works with scrapped string with salary data from HeadHunter and returns net values'''
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
    return dict['from'], dict['to'], dict['currency']

def salary_to_dict_sj(salary):
    '''Function works with scrapped string with salary data from SuperJob and returns net values'''
    dict = {'from': None, 'to': None, 'currency': None}
    if not salary.lower().startswith('по'):
        dict0 = [_ for _ in salary.split('\xa0')]

        if dict0[0].lower() == 'от':
            dict['from'] = float(dict0[1] + dict0[2])
        elif dict0[0].lower() == 'до':
            dict['to'] = float(dict0[1] + dict0[2])
        elif not dict0.count('-'):
            dict['to'] = float(dict0[0] + dict0[1])
            dict['from'] = float(dict0[0] + dict0[1])
        else:
            dict['from'] = float(dict0[0] + dict0[1])
            dict['to'] = float(dict0[3] + dict0[4])
        dict['currency'] = dict0[-1]
    return dict['from'], dict['to'], dict['currency']

print('I will find some jobs for you, be ready for relocation, case when you live in another city, but offer seems attractive!)')

job_title=input('Please write the key word for your search:')
length = input("Please insert minimal number of jobs you want to see from each of services or write 'Y' to see all:")
if length.lower() == 'y':
    length = 100000
else:
    length = int(length)

headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.80 Safari/537.36'}

''' 
    HedHunter 
    Scrapping 
    Block
'''
main_link='https://hh.ru'
href='/search/vacancy?clusters=true&area=1&search_field=name&enable_snippets=true&st=searchVacancy&text='+job_title

raw_jobdata = []
while True:
    response = requests.get(main_link+href,  headers=headers)
    soup =  bs(response.text, 'html.parser')
    try:
        href=soup.find('a',{'data-qa':'pager-next'})['href']
    except:
        print("didn't found href tag")
        break
    jobs_list = soup.findAll('div',{'data-qa':'vacancy-serp__vacancy'})
    raw_jobdata.extend(jobs_list)

    if len(raw_jobdata)>length:
        raw_jobdata = raw_jobdata[:length]
        print('HeadHunter: ' + str(len(raw_jobdata)) + ' jobs scrapped!')
        break
    if not jobs_list:
        number = int(soup.find('p', {'class': 'vacancysearch-xs-header'}).text.split('\xa0')[0])
        if len(raw_jobdata)<number:
            print('HeadHunter: '+str(len(raw_jobdata))+' jobs scrapped, to get more('+str(number)+' jobs found) please open website!')
        break

job = []
for jobs in raw_jobdata:
    job_data = {}
    job_name = jobs.find('a', {'data-qa': 'vacancy-serp__vacancy-title'})
    try:
        job_salary = jobs.find('span', {'data-qa': 'vacancy-serp__vacancy-compensation'}).getText()
        job_salary_from, job_salary_to, job_salary_currency = salary_to_dict_HH(job_salary)
    except:
        job_salary_from, job_salary_to, job_salary_currency = None, None, None
    job_link = job_name['href']

    job_name = job_name.text

    company_info = jobs.find('div', {'class':'vacancy-serp-item__meta-info'})
    company_name = company_info.find('a', {'data-qa': 'vacancy-serp__vacancy-employer'}).text

    company_location = jobs.find('span', {'data-qa': 'vacancy-serp__vacancy-address'}).text

    job_data['service']='HeadHunter'
    job_data['name'] = job_name
    job_data['employer'] = company_name
    job_data['location'] = company_location
    job_data['SalaryFrom'] = job_salary_from
    job_data['SalaryTo'] = job_salary_to
    job_data['SalaryCurrency'] = job_salary_currency
    job_data['link'] = job_link
    job.append(job_data)

job_df_hh = pd.DataFrame.from_dict(job)

'''
    SuperJob
    Scrapping
    Block
'''
main_link='https://www.superjob.ru'

current_page = 1
jobs_list = []
company_list = []
while current_page <= length:
    params = {'keywords': job_title,
              'noGeo': True,  # поиск без фильтров на локацию
              'page': current_page
              }
    response = requests.get(main_link+'/vacancy/search/', params=params, headers=headers)
    soup = bs(response.text,'html.parser')
    total_count= int(soup.find('span',{'class':'_1ZlLP'}).text.split(' ')[1])
    vacancies  = soup.findAll('div', {'class': 'jNMYr'})
    companies = soup.findAll('div', {'class', '_3_eyK _3P0J7 _9_FPy'})
    if not vacancies:
        if len(jobs_list)<total_count:
            print('SuperJob: Scrapped '+str(len(jobs_list))+' jobs. To get more info you should log in!')
        else:
            print('Got empty page, please check webpage structure')
        break
    jobs_list.extend(vacancies)
    company_list.extend(companies)
    current_page +=1

job_names=[]
job_salaries_from=[]
job_salaries_to=[]
job_salaries_currency=[]
job_links=[]

for jobs in jobs_list:
    job_name=jobs.find('a',{'class':'_6AfZ9'})
    job_links.append(main_link+job_name['href'])
    job_names.append(job_name.text)
    job_salary=jobs.find('span',{'class':'_2Wp8I'}).text
    job_salary_from, job_salary_to, job_salary_currency = salary_to_dict_sj(job_salary)
    job_salaries_from.append(job_salary_from)
    job_salaries_to.append(job_salary_to)
    job_salaries_currency.append(job_salary_currency)

company_names = []
company_locations = []

for company in company_list:
    company_name = company.find('a', {'class': '_25-u7'})
    company_names.append(company_name.text)

    company_location = company.find('span', {'class':'f-test-text-company-item-location'}).text.split(' ')
    delimiter_ = company_location.index('•')
    company_locations.append(' '.join(company_location[delimiter_+1:]))

dict = {'service':'Superjob','name':job_names, 'employer':company_names, 'location':company_locations, 'SalaryFrom':job_salaries_from, 'SalaryTo':job_salaries_to,'SalaryCurrency':job_salaries_currency,'link': job_links}

job_df_sj = pd.DataFrame.from_dict(dict)

result_df=pd.concat([job_df_hh,job_df_sj])
result_df.to_csv('Vacancies.csv', header=True, index=False)
print('Данные сохранены в файл Vacancies.csv')
