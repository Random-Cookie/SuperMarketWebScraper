from abc import abstractmethod
from dataclasses import dataclass, field
from typing import List

from bs4 import BeautifulSoup
from selenium.webdriver.chrome.webdriver import WebDriver


@dataclass
class Product:
	""""Data class to store product details"""
	id: str = "invalid"
	name: str = "n/a"
	price: float = -1
	servings: float = -1
	price_per_serving: float = -1
	allergens: List[str] = field(default_factory=lambda: [])

	def __str__(self):
		return ("Product: " + self.id + ", " + self.name + ", " + str(self.price) + ", " +
				str(self.servings) + ", " + str(self.price_per_serving) + ", " + str(self.allergens))


class Scraper:
	""""Abstract class to represent a general scraper

	:ivar __driver: Private - Webdriver used to get source content from urls to be scraped
	:vartype __driver: webdriver
	:ivar _current_URL: Protected - The current url being scraped / has just been scraped
	:vartype _current_url: str
	"""
	def __init__(self, driver: WebDriver):
		""""Constructor for Scraper class

		:parameter driver: Driver for the scraper to use
		:type driver: WebDriver
		"""
		self.__driver = driver
		self._current_URL = ""

	def get_current_url(self):
		""""Getter for _current_URL

		:returns: URL currently being scraped
		:rtype: str
		"""
		return self._current_URL

	def _make_soup(self, url: str) -> BeautifulSoup:
		""""Make soup from a url

		:param url
		:type url: str
		"""
		self.__driver.get(url)
		content = self.__driver.page_source
		return BeautifulSoup(content, 'html.parser')

	def close_driver(self):
		self.__driver.close()
		self.__driver.quit()

	@abstractmethod
	def scrape(self, url: str):
		""""Abstract scrape method

		This method should scrape a url for data, return type may vary depending on scraper

		:param url
		:type url: str

		:returns Scraped data
		"""
		self._current_URL = url
		return []


class ContinuousScraper(Scraper):
	""""Abstract class to represent a continuous scraper

	This class represents a scraper which will scrape a series of consecutive pages

	:ivar _next_URL: Protected - The next url to be scraped
	:vartype: str
	"""
	def __init__(self, driver: WebDriver, init_url: str = ""):
		""""Constructor for ContinuousScraper class

		:parameter driver: Driver for the scraper to use
		:type driver: WebDriver
		:parameter init_url: initial url to scrape(default value "")
		:type init_url: str
		"""
		Scraper.__init__(self, driver)
		self._next_URL = init_url

	@staticmethod
	@abstractmethod
	def __find_next_url(soup: BeautifulSoup) -> str:
		""""Abstract find next url method

		This method should find the next URL to scrape

		:parameter soup: soup to search for the next URL
		:type soup: BeautifulSoup
		"""
		return ""

	def get_next_url(self):
		""""Getter for _next_URL

		:returns: Next URL to be scraped
		:rtype: str
		"""
		return self._next_URL

	def scrape_next_page(self):
		""""Scrape page in _next_URL

		:returns Scraped data from next URL
		"""
		return self.scrape(self._next_URL)

	@abstractmethod
	def scrape(self, url: str) -> List[str]:
		""""Abstract scrape method

		This method should scrape a url for data, return type may vary depending on scraper

		:param url
		:type url: str

		:returns Scraped data
		"""
		self._current_URL = url
		return []
