from Scrapers.common import *
import re


class ProductPageScraper(Scraper):
	def __init__(self, driver: webdriver):
		Scraper.__init__(self, driver)

	def scrape(self, url: str) -> List[str]:
		soup = self._make_soup(url)
		for a in soup.find_all('div', attrs={'class': 'product-details-page'}):
			product = ""
			try:
				try:
					product = a.find('h1', attrs={'class': 'product-details-tile__title'}).text
				except:
					product = "n/a"
				try:
					price = float(a.find('span', attrs={'class': 'value'}).text)
				except:
					price = 0
				try:
					portions_text = a.find('div', attrs={'id': 'uses'}).find('p', attrs={'class': 'product-info-block__content'}).text
				except:
					portions_text = ""
				portions = re.findall(r'\d+', portions_text)
				price_per_portion = "n/a"
				if portions and portions[0] != "0":
					price_per_portion = round(price / int(portions[0]), 2)
				else:
					portions = ["n/a"]
				return [product, price, portions[0], price_per_portion]
			except Exception as e:
				print("My good sir, you seem to have encountered an error:")
				print("Product: " + product)
				print(e.with_traceback(e.__traceback__))
				return []


class CategoryPageScraper(Scraper):
	def __init__(self, driver: webdriver, url_prefix: str = "", init_url: str = ""):
		Scraper.__init__(self, driver)
		self.url_prefix = url_prefix
		self._next_URL = init_url
		self._current_URL = ""

	@staticmethod
	def find_next_url(soup: BeautifulSoup) -> str:
		return soup.find('a', attrs={'title': 'Go to results page'}).get('href')

	def get_current_url(self):
		return self._current_URL

	def get_next_url(self):
		return self._next_URL

	def scrape(self, url: str) -> List[str]:
		urls = []
		soup = self._make_soup(url)
		for a in soup.find_all('li', attrs={'class': 'product-list--list-item'}):
			try:
				urls.append(a.find('a').get('href'))
			except:
				pass
		try:
			self._current_URL = self._next_URL
			self._next_URL = self.find_next_url(soup)
		except:
			pass
		return urls

	def scrape_next_page(self):
		return self.scrape(self.url_prefix + self._next_URL)


class HomePageScraper(Scraper):
	def __init__(self, driver: webdriver, url_prefix: str = "", max_deps: int = 5):
		Scraper.__init__(self, driver)
		self.url_prefix = url_prefix
		self.__MAX_DEPS = max_deps

	def scrape(self, url: str) -> List[str]:
		urls = []
		soup = self._make_soup(url)
		super_dep_menu = soup.find('ul', attrs={'class': 'menu menu-superdepartment'})
		super_deps = super_dep_menu.find_all('a')
		for i in range(self.__MAX_DEPS):
			dep_menu = self._make_soup(self.url_prefix + super_deps[i].get('href'))
			list_item = dep_menu.find('li', attrs={'class': 'list-item list-subheader'})
			a = list_item.find('a')
			urls.append(a.get('href'))
		return urls
