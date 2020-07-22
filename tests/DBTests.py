import sqlite3
import time


def create_connection(db_file):
	connection = None

	try:
		connection = sqlite3.connect(db_file)
	except Exception as e:
		print(e)

	return connection


def write_product(connection, product):
	sql = ('INSERT INTO Products(name, price, servings, priceperserving)\n'
			'VALUES(?,?,?,?)')
	cur = connection.cursor()
	cur.execute(sql, product)
	connection.commit()
	return cur.lastrowid


database = r"..\TTDB.db"
conn = create_connection(database)

start_time = time.time()
prod = ("Milk", 2.5, 10, 2.5)
write_product(conn, prod)
print(time.time() - start_time)
conn.close()
