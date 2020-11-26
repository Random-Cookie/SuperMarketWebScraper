import argparse
import concurrent.futures
import sqlite3
import subprocess
import time
from threading import Lock

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

import Scrapers.morrisons
import Scrapers.tesco
from Scrapers.common import *

# parser setup
parser = argparse.ArgumentParser(description="ArgParser")
parser.add_argument("--supermarket", type=str, default="tesco", help="choose supermarket preset", required=True)
parser.add_argument("--CHROMEDRIVER_PATH", type=str, default="res/chromedriver.exe", help="path for chromedriver.exe")
parser.add_argument("--URL_PREFIX", type=str, default="https://www.tesco.com", help="url prefix for the scraper")
parser.add_argument("--DATABASE", type=str, default="test.db", help="database to connect to")
parser.add_argument("--MAX_CATEGORY_WORKERS", type=int, default=1, help="number of concurrent categories")
parser.add_argument("--PRODUCTS_ON_PAGE", type=int, default=24, help="Number of products per page")
parser.add_argument("--TOTAL_CATEGORIES", type=int, default=5, help="Total Number of categories")
parser.add_argument("--DEBUG_INFO", action='store_true', default=False, dest='DEBUG_INFO', help="print debug data?")
args = parser.parse_args()
if args.supermarket == "tesco":
	if args.DATABASE == "TTDB.db":
		args.DATABASE = "tesco"
if args.supermarket == "asda":
	if args.URL_PREFIX == "":
		args.URL_PREFIX = ""  # TODO
	if args.DATABASE == "TTDB.db":
		args.DATABASE = "asda.db"
	if args.PRODUCTS_ON_PAGE == 24:
		args.PRODUCTS_ON_PAGE = 0  # TODO
	if args.TOTAL_CATEGORIES == 5:
		args.TOTAL_CATEGORIES = 0  # TODO
if args.supermarket == "morrisons":
	if args.URL_PREFIX == "":
		args.URL_PREFIX = "https://groceries.morrisons.com/browse"
	if args.DATABASE == "TTDB.db":
		args.DATABASE = "morrisons.db"
	if args.PRODUCTS_ON_PAGE == 24:
		args.PRODUCTS_ON_PAGE = 0  # TODO
	if args.TOTAL_CATEGORIES == 5:
		args.TOTAL_CATEGORIES = 0  # TODO
if args.supermarket == "sainsburys":
	if args.URL_PREFIX == "":
		args.URL_PREFIX = ""  # TODO
	if args.DATABASE == "TTDB.db":
		args.DATABASE = "sainsburys.db"
	if args.PRODUCTS_ON_PAGE == 24:
		args.PRODUCTS_ON_PAGE = 0  # TODO
	if args.TOTAL_CATEGORIES == 5:
		args.TOTAL_CATEGORIES = 0  # TODO

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
# driver options
DRIVER_OPTIONS = Options()
DRIVER_OPTIONS.headless = True
DRIVER_OPTIONS.add_argument('user-agent={0}'.format(USER_AGENT))
DRIVER_OPTIONS.add_argument('log-level=3')


def convert(seconds) -> str:
	"""convert seconds to H:M:S

	:param seconds: number of seconds
	:return: "H:M:S"
	"""
	seconds = seconds % (24 * 3600)
	hour = seconds // 3600
	seconds %= 3600
	minutes = seconds // 60
	seconds %= 60
	return "%d:%02d:%02d" % (hour, minutes, seconds)


# create and return a connection to a database file
def create_connection(db_file) -> sqlite3.Connection:
	"""Create a connection to the database

	:param db_file: database to connect to
	:return: a database connection
	"""
	connection = None
	try:
		connection = sqlite3.connect(db_file)
	except Exception as e:
		print(e)
	return connection


# write a product to the database
def write_product(connection, product: Product) -> int:
	"""Write a product to the database

	:param connection: connection to the database
	:param product: product to write
	:return: lastrowid
	"""
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


def create_driver(chromedriver_path) -> webdriver.Chrome:
	"""Create a driver for the scrapers

	:param chromedriver_path: Path of the chromedriver.exe
	:return: a driver
	"""
	return webdriver.Chrome(chromedriver_path, options=DRIVER_OPTIONS)


def create_home_scraper(driver) -> Scraper:
	"""Create a home page scraper

	:param driver: Driver to use
	:return: a homepage scraper
	"""
	if args.supermarket == "asda":
		pass
	elif args.supermarket == "morrisons":
		return Scrapers.morrisons.HomePageScraper(driver, URL_PREFIX, 6)
	elif args.supermarket == "sainsburys":
		pass
	else:
		return Scrapers.tesco.HomePageScraper(driver, URL_PREFIX, TOTAL_CATEGORIES)


def create_category_scraper(driver, cat_url) -> ContinuousScraper:
	"""Create a category scraper

	:param driver: Driver to use
	:param cat_url: the category url
	:return: a category scraper
	"""
	if args.supermarket == "asda":
		pass
	elif args.supermarket == "morrisons":
		pass
	elif args.supermarket == "sainsburys":
		pass
	else:
		return Scrapers.tesco.CategoryPageScraper(driver, cat_url, URL_PREFIX)


def create_prod_scraper(driver) -> Scraper:
	"""Create a product scraper

	:param driver: driver to use
	:return: a product scraper
	"""
	if args.supermarket == "asda":
		pass
	elif args.supermarket == "morrisons":
		pass
	elif args.supermarket == "sainsburys":
		pass
	else:
		return Scrapers.tesco.ProductPageScraper(driver)


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
	driver = create_driver(CHROMEDRIVER_PATH)
	# Setup cat scraper and cat variables
	cat_scraper = create_category_scraper(driver, cat_url)
	cat_start_time = time.time()
	cat_product_count = 0
	chromedriver_paths = [CHROMEDRIVER_PATH] * PRODUCTS_ON_PAGE
	with concurrent.futures.ThreadPoolExecutor(max_workers=PRODUCTS_ON_PAGE) as driver_prod_maker:
		drivers = list(driver_prod_maker.map(create_driver, chromedriver_paths))
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
	cat_scraper.close_driver()
	for scraper in prod_scrapers:
		scraper.close_driver()


# start of script
overall_start_time = time.time()
home_driver = create_driver(CHROMEDRIVER_PATH)
# Scrape the homepage (driver, URL_PREFIX, #Categories)
home_scraper = create_home_scraper(home_driver)
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
