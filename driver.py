from scrapers import *
import time
URLPREFIX = "https://www.tesco.com"


driver = webdriver.Chrome('D:/Joe/DevPython/cd.exe')

cat_scraper = CategoryPageScraper(driver, URLPREFIX, "/groceries/en-GB/shop/fresh-food/all")
prod_scraper = ProductPageScraper(driver)

for i in range(3):

	urls = cat_scraper.scrape_next_page()

	for url in urls:
		print(prod_scraper.scrape(URLPREFIX + url))

driver.close()
quit(0)
