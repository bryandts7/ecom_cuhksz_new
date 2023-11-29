import sqlite3

#Open database
conn = sqlite3.connect('database.db')

conn.execute('''DROP TABLE chatRoom''')
conn.execute('''DROP TABLE chatHistory''')

conn.execute(''' CREATE TABLE chatRoom
        (chatRoomId INTEGER PRIMARY KEY,
        customerUserId INTEGER,
        sellerUserId INTEGER,
        FOREIGN KEY (customerUserId) REFERENCES users(userId),
        FOREIGN KEY (sellerUserId) REFERENCES users(userId)
        )''')

conn.execute(''' CREATE TABLE chatHistory
        (chatId INTEGER PRIMARY KEY,
        chatRoomId INTEGER,
        senderId INTEGER,
        sendingTime TEXT,
        message TEXT,
        FOREIGN KEY (chatRoomId) REFERENCES chatRoom(chatRoomId),
        FOREIGN KEY (senderId) REFERENCES users(userId)
        )''')

conn.commit()