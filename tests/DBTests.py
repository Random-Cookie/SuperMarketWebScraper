import concurrent.futures
import sqlite3
import time
from threading import Lock

from Scrapers.common import *

write_lock = Lock()


def create_connection(db_file_path: str):
	connection = None

	try:
		connection = sqlite3.connect(db_file_path)
	except Exception as e:
		print(e)

	return connection


def write_product(connection, product: Product):
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
	with write_lock:
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


def test(products):
	connection = create_connection(database)
	for product in products:
		write_product(connection, product)


database = r"..\test.db"
conn = create_connection(database)

start_time = time.time()
prod = Product()
prod.id = "1"
prod.name = "test_item"
prod.price = 2.5
prod.servings = 10
prod.price_per_serving = 0.25
prod.allergens = ["milk", "milk"]

t_prod_list = [prod] * 50
prods_list = [t_prod_list] * 5


with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
	executor.map(test, prods_list)
print(time.time() - start_time)
conn.close()
