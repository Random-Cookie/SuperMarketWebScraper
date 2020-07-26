import re

from Scrapers.common import *


class ProductPageScraper(Scraper):
	""""Scraper to scrape a product page for product information"""
	def __init__(self, driver: WebDriver):
		""""Constructor for ProductPageScraper

		Calls superclass constructor
		:parameter driver: Driver for the scraper to use
		:type driver: WebDriver
		"""
		Scraper.__init__(self, driver)

	def scrape(self, url: str) -> Product:
		""""Scrape a Product page

		:parameter url: URL to scrape
		:type url: str
		:returns: Product data from the given url
		:rtype: Product
		"""
		self._current_URL = url
		soup = self._make_soup(url)
		main_col = soup.find('div', attrs={'class': 'product-details-page'})
		product = Product()
		try:
			product.id = self._current_URL.split('/')[-1]
			try:
				product.name = main_col.find('h1', attrs={'class': 'product-details-tile__title'}).text
			except:
				pass
			try:
				product.price = float(main_col.find('span', attrs={'class': 'value'}).text)
			except:
				pass
			try:
				portions_text = main_col.find('div', attrs={'id': 'uses'}).find('p', attrs={'class': 'product-info-block__content'}).text
				portions = re.findall(r'\d+', portions_text)
				if portions and portions[0] != "0":
					product.servings = portions[0]
					product.price_per_serving = round(product.price / int(product.servings), 2)
			except:
				pass
			try:
				allergen_tags = main_col.find('div', attrs={'id': 'ingredients'}).find_all('strong')
				for allergen_tag in allergen_tags:
					if allergen_tag.text not in product.allergens and "INGREDIENTS" not in allergen_tag.text:
						product.allergens.append(allergen_tag.text)
			except:
				pass
		except Exception as e:
			print("My good sir, you seem to have encountered an error:")
			print(" Product: " + str(product))
			print(e.with_traceback(e.__traceback__))
		return product


class CategoryPageScraper(ContinuousScraper):
	""""Scraper to scrape a all pages in a category

	:ivar url_prefix: a prefix for the scraped urls to make a full URL
	:vartype url_prefix: str
	"""
	def __init__(self, driver: WebDriver, init_url: str = "", url_prefix: str = ""):
		"""Constructor for CategoryPageScraper
		:parameter driver: Driver for the scraper to use
		:type driver: WebDriver
		:parameter init_url: Initial URL to scrape
		:type init_url: str
		:parameter url_prefix: A prefix for the scraped urls to make a full URL
		:type url_prefix: str
		"""
		ContinuousScraper.__init__(self, driver, url_prefix + init_url)
		self.url_prefix = url_prefix

	@staticmethod
	def __find_next_url(soup: BeautifulSoup) -> str:
		"""Find the next url to be scraped

		:parameter soup: Soup to search for the next URL
		:type soup: BeautifulSoup
		:returns: Next URL
		:rtype: str
		"""
		return soup.find('a', attrs={'title': 'Go to results page'}).get('href')

	def scrape(self, url: str) -> List[str]:
		""""Scrape all pages in a category

		:parameter url: URL to scrape
		:type url: str
		:returns: Product URLs from the given category page
		:rtype: List[str]
		"""
		urls = []
		soup = self._make_soup(url)
		for a in soup.find_all('li', attrs={'class': 'product-list--list-item'}):
			try:
				urls.append(a.find('a').get('href'))
			except:
				pass
		try:
			self._current_URL = self._next_URL
			self._next_URL = self.url_prefix + self.__find_next_url(soup)
		except:
			pass
		return urls


class HomePageScraper(Scraper):
	""""Scraper to scrape the homepage for category USLs

	:ivar url_prefix: A prefix for the scraped urls to make a full URL
	:vartype url_prefix: str
	:ivar __MAX_DEPS: Maximum number of categories to return
	"""
	def __init__(self, driver: WebDriver, url_prefix: str = "", max_deps: int = 5):
		""""
		:parameter driver: Driver for the scraper to use
		:type driver: WebDriver
		:parameter url_prefix: a prefix for the scraped urls to make a full URL
		:type url_prefix: str
		:parameter max_deps: Maximum number of categories to return
		:type max_deps: int
		"""
		Scraper.__init__(self, driver)
		self.url_prefix = url_prefix
		self.__MAX_DEPS = max_deps

	def scrape(self, url: str) -> List[str]:
		""""Scrape all pages in a category

		:parameter url: URL to scrape
		:type url: str
		:returns: Return category URLs from the homepage
		:rtype: List[str]
		"""
		urls = []
		self._current_URL = url
		soup = self._make_soup(url)
		super_dep_menu = soup.find('ul', attrs={'class': 'menu menu-superdepartment'})
		super_deps = super_dep_menu.find_all('a')
		for i in range(self.__MAX_DEPS):
			dep_menu = self._make_soup(self.url_prefix + super_deps[i].get('href'))
			list_item = dep_menu.find('li', attrs={'class': 'list-item list-subheader'})
			a = list_item.find('a')
			urls.append(a.get('href'))
		return urls
