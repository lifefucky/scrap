
'''2. Написать функцию, которая производит поиск и выводит на экран вакансии с заработной платой больше
введённой суммы. Запрос должен анализировать одновременно минимальную и максимальную зарплату.'''

from pymongo import MongoClient

client = MongoClient('127.0.0.1', 27017)
db = client['jobs']
collection = db['jobs_list']

wish_salary=int(input('please insert your wishing salary:'))

for i in collection.find({'$or':[{'SalaryFrom':{'$gte':wish_salary}},
                       {'$and':[{'SalaryFrom':{'$eq':None}}, {'SalaryTo':{'$gte':wish_salary}}]}
                                ]
                          }):
    print(i)

