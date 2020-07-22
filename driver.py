from scrapers import *
import sqlite3


def create_connection(db_file):
	connection = None
	try:
		connection = sqlite3.connect(db_file)
	except Exception as e:
		print(e)
	return connection


def write_product(connection, product):
	sql = ('INSERT INTO Products(Name, Price, Servings, PricePerServing)\n'
								'VALUES(?,?,?,?)')
	cur = connection.cursor()
	cur.execute(sql, product)
	connection.commit()
	return cur.lastrowid


URL_PREFIX = "https://www.tesco.com"
DATABASE = "TTDB.db"
conn = create_connection(DATABASE)

driver = webdriver.Chrome('D:/Joe/DevPython/chromedriver.exe')

home_scraper = HomePageScraper(driver, URL_PREFIX)

cat_urls = home_scraper.scrape(URL_PREFIX + '/groceries/en-GB/')
print("Category URLS: " + str(cat_urls))
for cat_url in cat_urls:
	cat_scraper = CategoryPageScraper(driver, URL_PREFIX, cat_url)
	prod_scraper = ProductPageScraper(driver)
	while not cat_scraper.get_next_url() is None:

		urls = cat_scraper.scrape_next_page()

		for url in urls:
			prod_info = prod_scraper.scrape(URL_PREFIX + url)
			print(prod_info)
			if prod_info:
				write_product(conn, tuple(prod_info))

driver.close()
quit(0)
