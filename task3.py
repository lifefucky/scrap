'''3. Написать функцию, которая будет добавлять в вашу базу данных только новые вакансии с сайта.'''


def db_insert_if_not_exists(coll, cond, data):
    '''Function inserts data to chosen collection if not already exists'''
    coll.update_one(cond, {'$set': data}, upsert=True)