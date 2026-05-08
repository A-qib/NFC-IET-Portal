import pymysql
import os

DB_CONFIG = {
    'host':     os.environ.get('DB_HOST', 'localhost'),
    'user':     os.environ.get('DB_USER', 'root'),
    'password': os.environ.get('DB_PASSWORD', 'aqib913114'),
    'port':     int(os.environ.get('DB_PORT', 3306)),
    'cursorclass': pymysql.cursors.DictCursor
}

db  = pymysql.connect(**DB_CONFIG)
cur = db.cursor()

cur.execute("CREATE DATABASE IF NOT EXISTS nfc_portal")
cur.execute("USE nfc_portal")

print("Database created!")
db.commit()
cur.close()
db.close()