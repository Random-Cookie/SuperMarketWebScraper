import concurrent.futures
import sqlite3
import subprocess
import time

from selenium.webdriver.chrome.options import Options

from Scrapers.Tesco import *

CHROMEDRIVER_PATH = 'res/chromedriver.exe'
URL_PREFIX = "https://www.tesco.com"
DATABASE = "test.db"
USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'
DEBUG_INFO = True


# create a connection to a database file
def create_connection(db_file):
	connection = None
	try:
		connection = sqlite3.connect(db_file)
	except Exception as e:
		print(e)
	return connection


# write a product to the database
def write_product(connection, product: Product):
	cur = connection.cursor()
	try:
		prod_list = [product.id, product.name, product.price, product.servings, product.price_per_serving]
		sql = ('INSERT INTO Products(ProductID, Name, Price, Servings, PricePerServing)\n'
									'VALUES(?, ?, ?, ?, ?)')
		cur.execute(sql, prod_list)
		connection.commit()
	except Exception as e:
		print(e)


def convert(seconds):
	seconds = seconds % (24 * 3600)
	hour = seconds // 3600
	seconds %= 3600
	minutes = seconds // 60
	seconds %= 60

	return "%d:%02d:%02d" % (hour, minutes, seconds)


def scrape_category(cat_url):
	opts = Options()
	opts.headless = True
	opts.add_argument('user-agent={0}'.format(USER_AGENT))
	driver = webdriver.Chrome(CHROMEDRIVER_PATH, options=opts)
	conn = create_connection(DATABASE)
	cat_scraper = CategoryPageScraper(driver, cat_url, URL_PREFIX)
	prod_scraper = ProductPageScraper(driver)
	cat_start_time = time.time()
	cat_product_count = 0
	while not cat_scraper.get_next_url() is None:
		urls = cat_scraper.scrape_next_page()
		page_start_time = time.time()
		product_count = 0
		for url in urls:
			prod_info = prod_scraper.scrape(URL_PREFIX + url)
			if prod_info:
				write_product(conn, prod_info)
				product_count += 1
			if DEBUG_INFO:
				# pass
				print(str(prod_info))
		if DEBUG_INFO:
			print("     Scraped: " + cat_scraper.get_current_url())
			print("         Added " + str(product_count) + " products in " + convert(time.time() - page_start_time))
		cat_product_count += product_count
	driver.close()
	conn.close()
	print("Scraped: " + cat_url)
	print(" Added " + str(cat_product_count) + " products in " + convert(time.time() - cat_start_time))


h_opts = Options()
h_opts.headless = True
h_opts.add_argument('user-agent={0}'.format(USER_AGENT))
home_driver = webdriver.Chrome(CHROMEDRIVER_PATH, options=h_opts)

home_scraper = HomePageScraper(home_driver, URL_PREFIX)
cat_urls = home_scraper.scrape(URL_PREFIX + '/groceries/en-GB/')
home_driver.close()
print("Category URLS: " + str(cat_urls))

with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
	executor.map(scrape_category, cat_urls)


subprocess.call([r"res\killChromeDriver.bat"])
quit(0)
