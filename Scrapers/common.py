from bs4 import BeautifulSoup
from selenium import webdriver
from typing import List
from abc import abstractmethod


class Scraper:
	def __init__(self, driver: webdriver):
		self.__driver = driver
		self._current_URL = ""

	def get_current_url(self):
		return self._current_URL

	def _make_soup(self, url: str) -> BeautifulSoup:
		self.__driver.get(url)
		content = self.__driver.page_source
		return BeautifulSoup(content, 'html.parser')

	@abstractmethod
	def scrape(self, url: str) -> List[str]:
		self._current_URL = url
		return []


class ContinuousScraper(Scraper):
	def __init__(self, driver: webdriver, init_url: str = ""):
		Scraper.__init__(self, driver)
		self._next_URL = init_url

	@staticmethod
	@abstractmethod
	def __find_next_url(soup: BeautifulSoup) -> str:
		return ""

	def get_next_url(self):
		return self._next_URL

	def scrape_next_page(self):
		return self.scrape(self._next_URL)

	@abstractmethod
	def scrape(self, url: str) -> List[str]:
		self._current_URL = url
		return []
