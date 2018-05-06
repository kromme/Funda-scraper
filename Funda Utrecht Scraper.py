import time
import datetime
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
import telegram
from config import *

driver = webdriver.Firefox(firefox_profile = profile, executable_path= webdriver_path)
bot = telegram.Bot(token=telegramtoken)

with open('db.csv', 'r') as f:
    db = f.readlines()
    
for i in range(len(db)):
    db[i] = db[i].replace('\n','')


driver.get(url)



retrieved_urls = []
for i in driver.find_elements_by_class_name('search-result-header'):
    retrieved_urls.append(i.find_element_by_xpath(" .//a[@data-object-url-tracking='resultlist']").get_attribute('href'))


for url in retrieved_urls:
    if url not in db:
        #print url
        bot.send_message(chat_id=chat_id, text= url )
        # add to db
        with open('db.csv','a') as f:
            f.write('%s\n' % url)


driver.close()