from bs4 import BeautifulSoup
from selenium import webdriver
from typing import List


class Scraper:
	def __init__(self, driver: webdriver):
		self.__driver = driver

	def _make_soup(self, url: str) -> BeautifulSoup:
		self.__driver.get(url)
		content = self.__driver.page_source
		return BeautifulSoup(content, 'html.parser')

	def scrape(self, url: str) -> List[str]:
		return []