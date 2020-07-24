import sqlite3
import time

from Scrapers.common import *


def create_connection(db_file):
	connection = None

	try:
		connection = sqlite3.connect(db_file)
	except Exception as e:
		print(e)

	return connection


def write_product(connection, product: Product):
	prod_list = [product.id, product.name, product.price, product.servings, product.price_per_serving]
	sql = ('INSERT INTO Products(ProductID, Name, Price, Servings, PricePerServing)\n'
			'VALUES(?, ?, ?, ?, ?)')
	cur = connection.cursor()
	cur.execute(sql, prod_list)
	connection.commit()
	return cur.lastrowid


database = r"..\test.db"
conn = create_connection(database)

start_time = time.time()
prod = Product()
prod.id = "1"
prod.name = "test_item"
prod.price = 2.5
prod.servings = 10
prod.price_per_serving = 0.25
prod.allergens = ["milk"]
write_product(conn, prod)
print(time.time() - start_time)
conn.close()
