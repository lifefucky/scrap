'''3. Написать функцию, которая будет добавлять в вашу базу данных только новые вакансии с сайта.'''
import requests
import bs4
from pymongo import MongoClient


def salary_to_dict_HH(salary):
    '''Function works with scrapped string with salary data from HeadHunter and returns net values'''
    dict = {'from': None, 'to': None, 'currency': None}
    dict0 = [f for f in salary.replace('-',' ').split(' ')]
    num = []
    for n in dict0:
        try:
            num.append(float(n.replace(u'\xa0', '')))
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


client = MongoClient('127.0.0.1', 27017)
db = client['jobs']
collection = db['jobs_list']

def db_insert_not_exists(cond, data):
    '''Function inserts data to chosen collection if not already exists'''
    collection.update_one(cond, {'$set': data}, upsert=True)

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
    soup =  bs4.BeautifulSoup(response.text, 'html.parser')
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
    job_data['name'] = job_name.replace('\xa0', ' ')
    job_data['employer'] = company_name
    job_data['location'] = company_location
    job_data['SalaryFrom'] = job_salary_from
    job_data['SalaryTo'] = job_salary_to
    job_data['SalaryCurrency'] = job_salary_currency
    job_data['link'] = job_link
    db_insert_not_exists({'link': job_data.get('link')}, job_data)



'''
    SuperJob
    Scrapping
    Block
'''
main_link='https://www.superjob.ru'

current_page = 1
jobs_list = []
company_list = []
while len(jobs_list)<length:
    params = {'keywords': job_title,
              'noGeo': True,  # поиск без фильтров на локацию
              'page': current_page
              }
    response = requests.get(main_link+'/vacancy/search/', params=params, headers=headers)
    soup = bs4.BeautifulSoup(response.text,'html.parser')
    total_count = int(soup.find('span',{'class':'_1ZlLP'}).text.split(' ')[1])
    vacancies = soup.findAll('div', {'class': 'jNMYr'})
    companies = soup.findAll('div', {'class', '_3_eyK _3P0J7 _9_FPy'})

    if not vacancies:
        if len(jobs_list)<total_count:
            print('SuperJob: Scrapped '+str(len(jobs_list))+' jobs. To get more info you should log in!')
        else:
            print('Got empty page, please check webpage structure')
        break
    jobs_list.extend(vacancies)
    company_list.extend(companies)
    if len(jobs_list)>length:
        jobs_list = jobs_list[:length]
        company_list = company_list[:length]
        break
    current_page +=1

job_names=[]
job_salaries_from=[]
job_salaries_to=[]
job_salaries_currency=[]
job_links=[]

for jobs in jobs_list:
    job_name=jobs.find('a',{'class':'_6AfZ9'})
    job_links.append(main_link+job_name['href'])
    job_names.append(job_name.text.replace('\xa0', ' '))
    job_salary=jobs.find('span',{'class':'_2Wp8I'}).text
    job_salary_from, job_salary_to, job_salary_currency = salary_to_dict_sj(job_salary)
    job_salaries_from.append(job_salary_from)
    job_salaries_to.append(job_salary_to)
    job_salaries_currency.append(job_salary_currency)

company_names = []
company_locations = []
test_list =[]

for company in company_list:
    company_name = company.find('a', {'class': '_25-u7'})
    company_names.append(company_name.text)

    company_location = company.find('span', {'class':'f-test-text-company-item-location'}).text.split(' ')
    delimiter_ = company_location.index('•')
    company_locations.append(' '.join(company_location[delimiter_+1:]))

for i in range(len(jobs_list)):
    dict = {'service':'Superjob','name':job_names[i], 'employer':company_names[i], 'location':company_locations[i], 'SalaryFrom':job_salaries_from[i], 'SalaryTo':job_salaries_to[i],'SalaryCurrency':job_salaries_currency[i],'link': job_links[i]}
    print([_ for _ in collection.find({'link':dict.get('link')})])
    db_insert_not_exists({'link': dict.get('link')}, dict)


for raw in collection.find():
    print(raw)
