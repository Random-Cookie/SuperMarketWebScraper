import concurrent.futures
import sqlite3
import subprocess
import time
from threading import Lock
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from Scrapers.Tesco import *

CHROMEDRIVER_PATH = 'res/chromedriver.exe'  # chromedriver.exe path
URL_PREFIX = "https://www.tesco.com"  # URL prefix for scrapers
DATABASE = "test.db"  # db to connect to
# user agent for chromedriver
USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'
DEBUG_INFO = False  # print debug info?
WRITE_LOCK = Lock()  # lock primitive for db access
MAX_CATEGORY_WORKERS = 3  # max concurrent categories
PRODUCTS_ON_PAGE = 24  # max product page scrapers


def convert(seconds) -> str:
	seconds = seconds % (24 * 3600)
	hour = seconds // 3600
	seconds %= 3600
	minutes = seconds // 60
	seconds %= 60
	return "%d:%02d:%02d" % (hour, minutes, seconds)


# create and return a connection to a database file
def create_connection(db_file) -> sqlite3.Connection:
	connection = None
	try:
		connection = sqlite3.connect(db_file)
	except Exception as e:
		print(e)
	return connection


# write a product to the database
def write_product(connection, product: Product) -> int:
	prod_list = [product.id, product.name, product.price, product.servings, product.price_per_serving]
	prod_sql = ('INSERT OR IGNORE INTO Products(ProductID, Name, Price, Servings, PricePerServing)\n'
				'VALUES(?, ?, ?, ?, ?)')
	allergen_sql = ('INSERT OR IGNORE INTO Allergens(Name)\n'
					'VALUES(?)')
	get_allergen_id = ('SELECT AllergenID\n'
						'FROM Allergens\n'
						'WHERE Name = ?')
	allergen_product_sql = ('INSERT OR IGNORE INTO ProductAllergen(ProductID, AllergenID)\n'
							'VALUES(?, ?)')
	cur = connection.cursor()
	with WRITE_LOCK:
		try:
			cur.execute(prod_sql, prod_list)
			for allergen in product.allergens:
				cur.execute(allergen_sql, [allergen])
				allergen_id = cur.execute(get_allergen_id, [allergen]).fetchone()[0]
				cur.execute(allergen_product_sql, [product.id, allergen_id])
			connection.commit()
		except Exception as e:
			print(e)
		finally:
			return cur.lastrowid


def create_driver(chromedriver_path, options) -> webdriver.Chrome:
	return webdriver.Chrome(chromedriver_path, options=options)


def create_prod_scraper(driver) -> ProductPageScraper:
	return ProductPageScraper(driver)


def scrape_category_page(url, prod_scraper, ret: bool = False) -> bool:
	"""Scrape a category page with products on it

	:param url: url to scrape
	:param prod_scraper: product scraper to use
	:param ret: true if product is written
	:return: ret
	"""
	conn = create_connection(DATABASE)
	prod_info = prod_scraper.scrape(URL_PREFIX + url)
	if prod_info:
		write_product(conn, prod_info)
		conn.close()
		ret = True
	if DEBUG_INFO:
		print(str(prod_info))
	return ret


def scrape_category(cat_url):
	"""Scrape a category

	:param cat_url: category url
	"""
	# Setup for creating drivers
	opt = Options()
	opt.headless = True
	opt.add_argument('user-agent={0}'.format(USER_AGENT))
	driver = webdriver.Chrome(CHROMEDRIVER_PATH, options=opt)
	# Setup cat scraper and cat variables
	cat_scraper = CategoryPageScraper(driver, cat_url, URL_PREFIX)
	cat_start_time = time.time()
	cat_product_count = 0
	chromedriver_paths = [CHROMEDRIVER_PATH] * PRODUCTS_ON_PAGE
	opts = [opt] * PRODUCTS_ON_PAGE
	with concurrent.futures.ThreadPoolExecutor(max_workers=PRODUCTS_ON_PAGE) as driver_prod_maker:
		drivers = list(driver_prod_maker.map(create_driver, chromedriver_paths, opts))
		prod_scrapers = list(driver_prod_maker.map(create_prod_scraper, drivers))
	# For each page in the category
	while not cat_scraper.get_next_url() is None:
		# scrape the next page
		urls = cat_scraper.scrape_next_page()
		page_start_time = time.time()
		# Use one thread to scrape each page using the scrapers and urls is appropriate arrays
		with concurrent.futures.ThreadPoolExecutor(max_workers=PRODUCTS_ON_PAGE) as cat_executor:
			products_counted = list(cat_executor.map(scrape_category_page, urls, prod_scrapers))
		# sum the added products
		product_count = sum(products_counted)
		if DEBUG_INFO:
			print("     Scraped: " + cat_scraper.get_current_url())
			print("         Added " + str(product_count) + " products in " + convert(time.time() - page_start_time))
		# add products to category count
		cat_product_count += product_count
	print("Scraped: " + cat_url)
	print(" Added " + str(cat_product_count) + " products in " + convert(time.time() - cat_start_time))
	# Close the drivers
	driver.close()
	for driver in drivers:
		driver.close()


# start of script
overall_start_time = time.time()
# Create a diver for the home scraper
h_opts = Options()
h_opts.headless = True
h_opts.add_argument('user-agent={0}'.format(USER_AGENT))
home_driver = webdriver.Chrome(CHROMEDRIVER_PATH, options=h_opts)
# Scrape the homepage (driver, URL_PREFIX, #Categories)
home_scraper = HomePageScraper(home_driver, URL_PREFIX, 6)
cat_urls = home_scraper.scrape(URL_PREFIX + '/groceries/en-GB/')
home_driver.close()

print("Category URLS: " + str(cat_urls))
# Scrape the categories
with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_CATEGORY_WORKERS) as executor:
	executor.map(scrape_category, cat_urls)

# kill chrome driver instances
subprocess.call([r"res\killChromeDriver.bat"])
print('\033[92m' + "Finished Execution in: " + convert(time.time() - overall_start_time))
quit(0)
