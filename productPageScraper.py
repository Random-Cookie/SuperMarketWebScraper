from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import time

driver = webdriver.Chrome('D:\Joe\DevPython\cd.exe')

urls = ["https://www.tesco.com/groceries/en-GB/products/289647218", "https://www.tesco.com/groceries/en-GB/products/300111410", "https://www.tesco.com/groceries/en-GB/products/303151530", "https://www.tesco.com/groceries/en-GB/products/273796618"]

products = []
prices = []
portions = []

#prod_no = 303151553
for url in urls:
	driver.get(url)

	content = driver.page_source

	soup = BeautifulSoup(content)
	for a in soup.find_all('div', attrs={'class':'grocery-product__main-col styled-tbp4qh-0 jaPXLD'}):
		try:
			product = a.find('h1', attrs={'class':'product-details-tile__title'})
			price = a.find('span', attrs={'class': 'value'})
			portion = a.find('div', attrs={'id':'uses'}).find('p', attrs={'class':'product-info-block__content'})
			products.append(product.text)
			prices.append(price.text)
			portions.append(portion.text)
		except:
			pass

print(products)
print(prices)
print(portions)

driver.close()