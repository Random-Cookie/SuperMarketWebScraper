import os

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

os.chdir('D:\Joe\DevPython\SuperMarketWebScraper')


def _make_soup(self, url: str) -> BeautifulSoup:
	""""Make soup from a url

	:param url
	:type url: str
	"""
	self.__driver.get(url)
	content = self.__driver.page_source
	return BeautifulSoup(content, 'html.parser')


USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'
DRIVER_OPTIONS = Options()
DRIVER_OPTIONS.headless = True
DRIVER_OPTIONS.add_argument('user-agent={0}'.format(USER_AGENT))
DRIVER_OPTIONS.add_argument('log-level=3')
URL = 'https://groceries.morrisons.com/browse//meat-fish-179549?display=2500'

driver = webdriver.Chrome('res/chromedriver.exe', options=DRIVER_OPTIONS)
driver.get(URL)
content = driver.page_source
content = BeautifulSoup(content, 'html.parser')
print(content.prettify().encode('UTF-8'))
