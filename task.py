from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from pymongo import MongoClient
import time

client = MongoClient('127.0.0.1', 27017)
db = client['Email']
collection = db['mail_list']

chrome_options = Options()
chrome_options.add_argument('start-maximized')

driver = webdriver.Chrome('/users/mrlebovsky/Downloads/chromedriver',options=chrome_options)
driver.get('https://mail.ru')

login = WebDriverWait(driver, 5).until(
    ec.visibility_of_element_located((By.ID, 'mailbox:login-input'))
)
login.send_keys('study.ai_172@mail.ru')
login.send_keys(Keys.ENTER)

passw = WebDriverWait(driver, 5).until(
            ec.visibility_of_element_located((By.NAME, 'password'))
        )
passw.send_keys('NextPassword172')
passw.send_keys(Keys.ENTER)

a=0
mes_links = []
while True:
    l_ = len(mes_links)
    letters_ = driver.find_elements_by_class_name('js-letter-list-item')
    if len(letters_)==0:
        letters_= WebDriverWait(driver, 5).until(
            ec.presence_of_all_elements_located((By.CLASS_NAME, 'js-letter-list-item'))
        )
    links_ = [i.get_attribute('href') for i in letters_]
    mes_links.extend(links_)
    mes_links = list(dict.fromkeys(mes_links))
    actions = ActionChains(driver)
    actions.move_to_element(letters_[-1])
    actions.perform()
    if l_==len(mes_links):
        break

print('Scrapped '+str(len(mes_links))+' mails!')

collection.delete_many({})
for link in mes_links:
    mess_data={}
    driver.get(link)
    try:
        contact = driver.find_element_by_class_name('letter-contact')
    except:
        contact = WebDriverWait(driver, 10).until(
            ec.presence_of_element_located((By.CLASS_NAME, 'letter-contact'))
            )
    mess_data['MailFrom']=contact.get_attribute('title')
    try:
        date = driver.find_element_by_class_name('letter__date')
    except:
        date = WebDriverWait(driver, 10).until(
            ec.presence_of_element_located((By.CLASS_NAME, 'letter__date'))
            )
    mess_data['MailDate']=date.text
    mess_data['MailSubject']=driver.find_element_by_tag_name('h2').text
    mess_data['MailText']=driver.find_element_by_class_name('letter-body').text.replace('\n','')
    collection.insert_one(mess_data)

driver.close()
print('Finished!')

