# ------------------------------------------------------------------- #
# -------          _____                                      ------- #
# -------        / ____|                                      ------- #
# -------       | (___   ___ _ __ __ _ _ __   ___ _ __        ------- #
# -------        \___ \ / __| '__/ _` | '_ \ / _ \ '__|       ------- #
# -------        ____) | (__| | | (_| | |_) |  __/ |          ------- #
# -------       |_____/ \___|_|  \__,_| .__/ \___|_|          ------- #
# -------                             | |                     ------- #
# -------                             |_|                     ------- #
# ------------------------------------------------------------------- #


import time
import datetime
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
import telegram
import pandas as pd
import logging
import random

class FundaScraper(object):
    """Wrapper for funda scraper.
    
    USAGE:
    sf = FundaScraper(funda_url = '',
                      telegram_token = '',
                      telegram_chat_id = '',
    )
    
    sf.run()
    """
    def __init__(self, 
                 funda_url : str, 
                 telegram_token : str,
                 telegram_chat_id : str,
                 webdriver_path : str = 'geckodriver.exe',
                 output_path : str = 'db.csv',
                 use_proxy : bool = True):
        self.funda_url = funda_url
        self.webdriver_path = webdriver_path
        self.output_path = output_path
        self.proxies = pd.DataFrame()
        self.use_proxy = use_proxy
        self.telegram_token = telegram_token
        self.telegram_chat_id = telegram_chat_id
        
        # set logging
        self._define_logger()
        
        # set driver profile
        self._set_profile()
        
        # set driver
        self.DRIVER = self.get_driver()
        self.find_proxy()
        
        self.XPATH_HOUSES = 'search-result-header'
        self.XPATH_HOUSE = " .//a[@data-object-url-tracking='resultlist']"
    
    def _define_logger(self):
        def get_logger(name, logfile="log.log"):
            log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            logging.basicConfig(
                level=logging.DEBUG, format=log_format, filename=logfile, filemode="w"
            )
            console = logging.StreamHandler()
            console.setLevel(logging.DEBUG)
            console.setFormatter(logging.Formatter(log_format))
            logging.getLogger(name).addHandler(console)
            return logging.getLogger(name)

        self.logger = get_logger("funda_scraper")
        
    def get_driver(self):
        return webdriver.Firefox(firefox_profile = self.profile, 
                                        executable_path= self.webdriver_path)
        
    def _change_useragent(self):
        """Change the user agent
        """ 
        
        uas = ['Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'
        ,'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36'
        ,'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'
        ,'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36'
        ,'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/603.3.8 (KHTML, like Gecko) Version/10.1.2 Safari/603.3.8'
        ,'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36'
        ,'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36'
        ,'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:55.0) Gecko/20100101 Firefox/55.0']

        ua = random.choice(uas)
        
        self.profile.set_preference("general.useragent.override", ua)
        self.profile.update_preferences() 
        self.logger.info(f'User agent set to {ua}')
        
    def _set_profile(self):
        """Create a profile for FF
        """
        self.profile = webdriver.FirefoxProfile()
        
        # to make sure we can close the windows: https://stackoverflow.com/questions/45510338/selenium-webdriver-3-4-0-geckodriver-0-18-0-firefox-which-combination-w
        self.profile.set_preference("browser.tabs.remote.autostart", False)
        self.profile.set_preference("browser.tabs.remote.autostart.1", False)
        self.profile.set_preference("browser.tabs.remote.autostart.2", False)

        # turn off auto update
        self.profile.set_preference('app.update.auto',False)
        self.profile.set_preference('app.update.enabled',False)
        self.profile.set_preference('app.update.silent',False)
        
        # set user agent
        self._change_useragent()
        
        self.logger.info(f'Profile set')

    def _change_proxy(self, proxyNo : int = 0):
        if self.proxies == []:
            self._get_proxy_list()
        
        # get next proxy values
        proxy = self.proxies.iloc[proxyNo].host
        port = int(self.proxies.iloc[proxyNo].port)

        # set proxy
        self.profile.set_preference("network.proxy.type", 1)
        self.profile.set_preference("network.proxy.http", proxy)
        self.profile.set_preference("network.proxy.http_port", port)
        self.profile.set_preference("network.proxy.ssl", proxy)
        self.profile.set_preference("network.proxy.ssl_port", port)
        self._change_useragent()
        self.profile.update_preferences() 
        
        self.logger.info(f'Proxy change to {proxy}')
        
    def _get_proxy_list(self):
        """Get list of proxies we can use
        """
        driver = self.get_driver()
        
        # go to page
        driver.get('https://www.sslproxies.org/')
        
        # set to 80 results
        driver.find_element_by_xpath("//.[@name='proxylisttable_length']").send_keys('80')
        
        # get table results
        table = driver.find_element_by_xpath("//.[@id='proxylisttable']")
        rows = table.text.split('\n')[1:80]
        driver.close()
        
        # to dataframe
        hosts = []
        ports = []

        for row in rows:
            try:
                hosts.append(row.split(' ')[0])
                ports.append(row.split(' ')[1])
            except:
                continue
        
        self.proxies = pd.DataFrame({'host': hosts, 'port': ports})
        self.logger.info(f'Got {len(self.proxies)} proxies')

    def find_proxy(self):
        """Trying whether the proxy actually works
        """
        # do not use when no proxy is needed
        if not self.use_proxy:
            return
        success = False
        proxyNo = 0

        while not success:
            self.logger.info(f'Trying proxy number {proxyNo}')
            self._change_proxy(proxyNo = proxyNo)
            
            # start driver
            driver = self.get_driver()
            
            # go to duckduckgo to check ip
            driver.get('https://duckduckgo.com/?q=my+ip&t=hb&ia=answer')
            
            # wait for ip
            wait = WebDriverWait(driver,10)
            wait.until(lambda driver: driver.find_element_by_class_name('zci__body'))
            ip = driver.find_element_by_class_name('zci__body').text
                
            # if that works, check if iens is reachable
            driver.get('https://www.funda.nl')
            
            # check if proxy isnt blocked. other go to except.
            if not ('blocked' in driver.title or 'error' in driver.title.lower()):
                proxyNo += 1
                
                self.DRIVER.close()
                self.DRIVER = self.get_driver()
                self._change_proxy(proxyNo = proxyNo)
                
                if proxyNo >= 79:
                    break
                
            # if works, end loop
            self.logger.info(f'Now working from {ip}')
            success = True
            driver.close()
            
    def send_telegram(self, url):
        """Send a message to Telegram
        """
        try:
            bot = telegram.Bot(token=self.telegram_token)
            text = 'I found a new house on Funda for you: {url}'
            bot.send_message(chat_id=self.telegram_chat_id, text = text )
            self.logger.info(f'Message succesfully send to Telegram')
        except Exception as e:
            self.logger.error('Could not sent message to Telegram', exc_info=e)

    def load_data(self):
        with open(self.output_path, 'r') as f:
            db = f.readlines()
            
        return [i.replace('\n','') for i in db]

    def run(self):
        # load previously found url's
        db = self.load_data()
        
        # go to Funda
        self.DRIVER.get(self.funda_url)
        
        # find houses
        for house in self.DRIVER.find_elements_by_class_name(self.XPATH_HOUSES):
            
            # get the url of the house
            url = house.find_element_by_xpath(self.XPATH_HOUSE).get_attribute('href')
            
            # send message
            if url not in db:
                self.send_telegram(url=url)
                
            # update db
            with open(self.output_path,'a') as f:
                f.write('%s\n' % url)

        self.DRIVER.close()
        
        