from selenium import webdriver
from bs4 import BeautifulSoup
from typing import List


class Scraper:
	def __init__(self, driver: webdriver):
		self.__driver = driver

	def _make_soup(self, url: str) -> BeautifulSoup:
		self.__driver.get(url)
		content = self.__driver.page_source
		return BeautifulSoup(content)

	def scrape(self, url: str) -> List[str]:
		return []


class ProductPageScraper(Scraper):
	def __init__(self, driver: webdriver):
		Scraper.__init__(self, driver)

	def scrape(self, url: str) -> List[str]:
		soup = self._make_soup(url)
		for a in soup.find_all('div', attrs={'class': 'grocery-product__main-col styled-tbp4qh-0 jaPXLD'}):
			try:
				product = a.find('h1', attrs={'class': 'product-details-tile__title'}).text
				price = a.find('span', attrs={'class': 'value'}).text
				portion = a.find('div', attrs={'id': 'uses'}).find('p', attrs={'class': 'product-info-block__content'}).text
				return [product, price, portion]
			except:
				pass
		return []


class CategoryPageScraper(Scraper):
	def __init__(self, driver: webdriver, url_prefix: str = "", init_url: str = ""):
		Scraper.__init__(self, driver)
		self.url_prefix = url_prefix
		self._next_URL = init_url

	@staticmethod
	def find_next_url(soup: BeautifulSoup) -> str:
		return soup.find('a', attrs={'title': 'Go to results page'}).get('href')

	def scrape(self, url: str) -> List[str]:
		urls = []
		soup = self._make_soup(url)
		urls.append(soup.find('li', attrs={'class':'product-list--list-item first'}).find('a').get('href'))
		for a in soup.find_all('li', attrs={'class': 'product-list--list-item'}):
			try:
				urls.append(a.find('a').get('href'))
			except:
				pass
		try:
			self._next_URL = self.find_next_url(soup)
		except:
			pass
		return urls

	def scrape_next_page(self):
		return self.scrape(self.url_prefix + self._next_URL)
