from Scrapers.common import *


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

	def scrape(self, url: str) -> List[str]:
		""""Scrape all pages in a category

		:parameter url: URL to scrape
		:type url: str
		:returns: Product URLs from the given category page
		:rtype: List[str]
		"""
		urls = []
		soup = self._make_soup(url + '?display=2500')
		# divs = soup.find_all('div', attrs={'class': 'fop-contentWrapper', 'role': 'presentation'})
		# lis = soup.find_all('li', attrs={'class': 'fops-item fops-item--featured'})
		# ays = soup.find_all('a')
		# aysr = soup.find_all('a') #doesnt find all as
		uls = soup.find_all('ul', attrs={'class': "fops fops-regular fops-shelf"}) # doesnt find all uls
		for ul in uls:
			lis = ul.find_all('li')
			for li in lis:
				try:
					urls.append(li.find('a').get('href'))
				except:
					pass
		# for a in soup.find_all('li', attrs={'class': 'fops-item fops-item--featured'}):
		# 	try:
		# 		urls.append(a.find('a').get('href'))
		# 	except:
		# 		pass
		# for a in soup.find_all('li', attrs={'class': 'fops-item fops-item--on_offer'}):
		# 	try:
		# 		urls.append(a.find('a').get('href'))
		# 	except:
		# 		pass
		# for a in soup.find_all('li', attrs={'class': 'fops-item fops-item--new'}):
		# 	try:
		# 		urls.append(a.find('a').get('href'))
		# 	except:
		# 		pass
		# for a in soup.find_all('li', attrs={'class': 'fops-item fops-item--other'}):
		# 	try:
		# 		urls.append(a.find('a').get('href'))
		# 	except:
		# 		pass
		try:
			self._current_URL = self._next_URL
			next_url = self.__find_next_url(soup)
			if next_url is not None:
				self._next_URL = self.url_prefix + next_url
			else:
				self._next_URL = next_url
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
		# grab departments
		super_dep_menu = soup.find('div', attrs={'class': 'grocery-section level-0'})
		depts = super_dep_menu.find('ul')
		list_items = depts.find_all('li')
		for i in range(self.__MAX_DEPS):
			a = list_items[i].find('a')
			urls.append(a.get('href'))
		return urls
