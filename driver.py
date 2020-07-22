from scrapers import *
import sqlite3
import time
import concurrent.futures

CHROMEDRIVER_PATH = 'D:/Joe/DevPython/chromedriver.exe'
URL_PREFIX = "https://www.tesco.com"
DATABASE = "test.db"


# create a connection to a database file
def create_connection(db_file):
	connection = None
	try:
		connection = sqlite3.connect(db_file)
	except Exception as e:
		print(e)
	return connection


# write a product to the database
def write_product(connection, product):
	sql = ('INSERT INTO Products(Name, Price, Servings, PricePerServing)\n'
								'VALUES(?,?,?,?)')
	cur = connection.cursor()
	cur.execute(sql, product)
	connection.commit()
	return cur.lastrowid


def convert(seconds):
	seconds = seconds % (24 * 3600)
	hour = seconds // 3600
	seconds %= 3600
	minutes = seconds // 60
	seconds %= 60

	return "%d:%02d:%02d" % (hour, minutes, seconds)


def scrape_category(cat_url):

	driver = webdriver.Chrome(CHROMEDRIVER_PATH)
	conn = create_connection(DATABASE)
	cat_scraper = CategoryPageScraper(driver, URL_PREFIX, cat_url)
	prod_scraper = ProductPageScraper(driver)
	cat_start_time = time.time()
	product_count = 0
	while not cat_scraper.get_next_url() is None:

		urls = cat_scraper.scrape_next_page()

		for url in urls:
			prod_info = prod_scraper.scrape(URL_PREFIX + url)
			print(prod_info)
			if prod_info:
				write_product(conn, tuple(prod_info))
				product_count += 1
	driver.close()
	conn.close()
	print("Scraped: " + cat_url)
	print("Added " + str(product_count) + " products in " + convert(time.time() - cat_start_time))


home_driver = webdriver.Chrome(CHROMEDRIVER_PATH)

home_scraper = HomePageScraper(home_driver, URL_PREFIX)
cat_urls = home_scraper.scrape(URL_PREFIX + '/groceries/en-GB/')
home_driver.close()
print("Category URLS: " + str(cat_urls))

with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
	executor.map(scrape_category, cat_urls)

quit(0)
