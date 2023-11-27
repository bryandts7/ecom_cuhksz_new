import sqlite3

#Open database
conn = sqlite3.connect('database.db')

# Create table
# conn.execute(''' CREATE TABLE order_payment
#         (ordPayId INTEGER PRIMARY KEY,
#         status INTEGER DEFAULT 0,
#         paymentProof TEXT
#         )''')

# conn.execute(''' CREATE TABLE order_delivery
#         (ordDelId INTEGER PRIMARY KEY,
#         status INTEGER DEFAULT 0,
#         deliveryProof TEXT
#         )''')

# conn.execute('''CREATE TABLE categories
# 		(categoryId INTEGER PRIMARY KEY,
# 		name TEXT
# 		)''')

# conn.execute('''CREATE TABLE seller
# 		(sellerId INTEGER PRIMARY KEY,
# 		weChatPayCode TEXT
# 		)''')

# conn.execute('''CREATE TABLE address
# 		(addressBuilding TEXT PRIMARY KEY
# 		)''')

# conn.execute('''CREATE TABLE users 
# 		(userId INTEGER PRIMARY KEY, 
# 		password TEXT,
# 		email TEXT,
# 		firstName TEXT,
# 		lastName TEXT,
#         addressBuilding TEXT,
# 		phone TEXT,
#         weChatId TEXT,
#         sellerId INTEGER DEFAULT 0,
#         FOREIGN KEY (addressBuilding) REFERENCES address(addressBuilding),
#         FOREIGN KEY (sellerId) REFERENCES seller(sellerId)
# 		)''')

# conn.execute('''CREATE TABLE products
# 		(productId INTEGER PRIMARY KEY,
# 		name TEXT,
# 		price REAL,
# 		description TEXT,
# 		image TEXT,
# 		stock INTEGER,
# 		categoryId INTEGER,
#         sellerId INTEGER,
# 		FOREIGN KEY(categoryId) REFERENCES categories(categoryId),
#         FOREIGN KEY (sellerId) REFERENCES seller(sellerId)
# 		)''')

# conn.execute('''CREATE TABLE cart
# 		(userId INTEGER,
# 		productId INTEGER,
# 		FOREIGN KEY(userId) REFERENCES users(userId),
# 		FOREIGN KEY(productId) REFERENCES products(productId)
# 		)''')

# conn.execute('''CREATE TABLE orders
# 		(orderId INTEGER,
# 		customerId INTEGER,
#         productId INTEGER,
#         ordPayId INTEGER,
#         ordDelId INTEGER,
#         orderStatus TEXT,
#         orderDate TEXT,
# 		FOREIGN KEY(customerId) REFERENCES users(userId),
# 		FOREIGN KEY(productId) REFERENCES products(productId),
#         FOREIGN KEY(ordPayId) REFERENCES order_payment(ordPayId),
#         FOREIGN KEY(ordDelId) REFERENCES order_delivery(ordDelId)
# 		)''')

cur = conn.cursor()
# cur.execute('''INSERT INTO address(addressBuilding)
#         VALUES
#              ('Muse'),
#              ('Ling'),
#              ('Diligentia'),
#              ('Shaw'),
#              ('Harmonia'),
#              ('Minerva'),
#              ('Seventh');
# 		''')

cur.execute('''INSERT INTO categories(categoryId, name)
        VALUES
             (1, 'Fashion'),
             (2, 'Electronics'),
             (3, 'Books'),
             (4, 'Furniture'),
             (5, 'Transportation'),
             (6, 'Stationary'),
             (7, 'Others');
		''')
conn.commit()