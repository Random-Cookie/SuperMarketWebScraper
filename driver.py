import argparse
import concurrent.futures
import sqlite3
import subprocess
import time
from threading import Lock

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from Scrapers.Tesco import *

# parser setup
parser = argparse.ArgumentParser(description="ArgParser")
parser.add_argument("--CHROMEDRIVER_PATH", type=str, default="res/chromedriver.exe", help="path for chromedriver.exe")
parser.add_argument("--URL_PREFIX", type=str, default="https://www.tesco.com", help="url prefix for the scraper")
parser.add_argument("--DATABASE", type=str, default="TTDB.db", help="database to connect to")
parser.add_argument("--DEBUG_INFO", action='store_true', default=False, dest='DEBUG_INFO', help="print debug data?")
parser.add_argument("--MAX_CATEGORY_WORKERS", type=int, default=1, help="number of concurrent categories")
parser.add_argument("--PRODUCTS_ON_PAGE", type=int, default=24, help="Number of products per page")
parser.add_argument("--TOTAL_CATEGORIES", type=int, default=5, help="Total Number of categories")
args = parser.parse_args()
# apply commandline args
CHROMEDRIVER_PATH = args.CHROMEDRIVER_PATH
URL_PREFIX = args.URL_PREFIX
DATABASE = args.DATABASE
DEBUG_INFO = args.DEBUG_INFO
MAX_CATEGORY_WORKERS = args.MAX_CATEGORY_WORKERS
PRODUCTS_ON_PAGE = args.PRODUCTS_ON_PAGE
TOTAL_CATEGORIES = args.TOTAL_CATEGORIES
# user agent for chromedriver
USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'
# lock primitive for db access
WRITE_LOCK = Lock()


# convert seconds to H:M:S
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
	opts = Options()
	opts.headless = True
	opts.add_argument('user-agent={0}'.format(USER_AGENT))
	opts.add_argument('log-level=3')
	driver = webdriver.Chrome(CHROMEDRIVER_PATH, options=opts)
	# Setup cat scraper and cat variables
	cat_scraper = CategoryPageScraper(driver, cat_url, URL_PREFIX)
	cat_start_time = time.time()
	cat_product_count = 0
	# Create the drivers and product scrapers for scraping product pages
	drivers = [] * PRODUCTS_ON_PAGE
	prod_scrapers = [] * PRODUCTS_ON_PAGE
	for i in range(PRODUCTS_ON_PAGE):
		# create a driver and prod scraper for each product on a cat page
		drivers.append(webdriver.Chrome(CHROMEDRIVER_PATH, options=opts))  # list drivers for closing later
		prod_scrapers.append(ProductPageScraper(drivers[i]))
	# For each page in the category
	while not cat_scraper.get_next_url() is None:
		# scrape the next page
		urls = cat_scraper.scrape_next_page()
		page_start_time = time.time()
		# Use one thread to scrape each page using the scrapers and urls is appropriate arrays
		with concurrent.futures.ThreadPoolExecutor(max_workers=PRODUCTS_ON_PAGE) as cat_executor:
			products_counted = cat_executor.map(scrape_category_page, urls, prod_scrapers)
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
	for i in range(PRODUCTS_ON_PAGE):
		drivers[i].close()


# start of script
overall_start_time = time.time()
# Create a diver for the home scraper
h_opts = Options()
h_opts.headless = True
h_opts.add_argument('user-agent={0}'.format(USER_AGENT))
home_driver = webdriver.Chrome(CHROMEDRIVER_PATH, options=h_opts)
# Scrape the homepage (driver, URL_PREFIX, #Categories)
home_scraper = HomePageScraper(home_driver, URL_PREFIX, TOTAL_CATEGORIES)
print("Scraping Homepage...")
cat_urls = home_scraper.scrape(URL_PREFIX + '/groceries/en-GB/')
home_driver.close()
print(" Category URLS: " + str(cat_urls))
# Scrape the categories
with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_CATEGORY_WORKERS) as executor:
	executor.map(scrape_category, cat_urls)

# kill chrome driver instances
subprocess.call([r"res\killChromeDriver.bat"])
print('\033[92m' + "Finished Execution in: " + convert(time.time() - overall_start_time))
quit(0)
