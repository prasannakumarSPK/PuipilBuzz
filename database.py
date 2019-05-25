import sqlite3
import os.path

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(BASE_DIR, "database.db")
with sqlite3.connect(db_path) as conn:

	conn.execute('''CREATE TABLE users
		(rollnum TEXT ,name TEXT,email TEXT,password TEXT,PRIMARY KEY(rollnum,email))''')

	conn.execute('''CREATE TABLE posts
		         (rollnum TEXT,title TEXT,post TEXT,postId INTEGER PRIMARY KEY,createddate TIME,Tupvotes INTEGER,Tdownvotes INTEGER,FOREIGN KEY(rollnum) REFERENCES users(rollnum))''')

	conn.execute('''CREATE TABLE comments
		         (postId INTEGER ,comment TEXT,rollnum TEXT,FOREIGN KEY(rollnum) REFERENCES users(rollnum))''')

	conn.execute('''CREATE TABLE votes
		         (postId INTEGER ,upvote INTEGER,downvote INTEGER,rollnum TEXT,FOREIGN KEY(rollnum) REFERENCES users(rollnum))''')

conn.close()




