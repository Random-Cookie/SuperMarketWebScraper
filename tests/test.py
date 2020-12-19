from selenium import webdriver
from selenium.webdriver.chrome.options import Options

import Scrapers.morrisons
import Scrapers.tesco

USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'
DRIVER_OPTIONS = Options()
DRIVER_OPTIONS.headless = True
DRIVER_OPTIONS.add_argument('user-agent={0}'.format(USER_AGENT))
DRIVER_OPTIONS.add_argument('log-level=3')

driver = webdriver.Chrome('res/chromedriver.exe', options=DRIVER_OPTIONS)
scraper = Scrapers.morrisons.CategoryPageScraper(driver, '/browse/meat-fish-179549', 'https://groceries.morrisons.com')
scraper.scrape('https://groceries.morrisons.com/browse/meat-fish-179549')
