from Scrapers.common import *

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
		return urls
