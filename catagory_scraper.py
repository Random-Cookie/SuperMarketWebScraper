from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

driver = webdriver.Chrome('D:/Joe/DevPython/cd.exe')

urls = []

driver.get("https://www.tesco.com/groceries/en-GB/shop/fresh-food/all")

content = driver.page_source

soup = BeautifulSoup(content)
for a in soup.find_all('li', attrs={'class':'product-list--list-item'}):
	try:
		urls.append(a.find('a').get('href'))
	except:
		pass

print(urls)

driver.close()
quit(0)
