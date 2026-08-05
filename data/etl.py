# review week5 connect db
# https://dev.mysql.com/doc/connector-python/en/connector-python-examples.html

import json
import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="2365533",
    database="taipei_day_trip"
)

# IF NOT EX IST S | ?每個都 NOT NULL | ?不要事後改 | # RowNumber | info_date 或 build_date
cursor.execute('''CREATE TABLE IF NOT EXISTS attraction (
    id INT PRIMARY KEY,
    name VARCHAR(255),
    rate INT,
    direction TEXT,
    date DATE,
    avBegin DATE,
    idpt DATE,
    MEMO_TIME VARCHAR(255),
    longitude DOUBLE,
    latitude DOUBLE,    
    MRT VARCHAR(100),
    SERIAL_NO VARCHAR(255),
    CAT VARCHAR(255),
    POI VARCHAR(10),
    description TEXT,
    langinfo VARCHAR(10),
    REF_WP''') 

#  ON DELETE CASCADE # AUTO_INCREMENT
cursor.execute('''CREATE TABLE IF NOT EXISTS image (
    id INT AUTO_INCREMENT PRIMARY KEY,
    attraction_id INT NOT NULL,
    url VARCHAR(500) NOT NULL,
    FOREIGN KEY (attraction_id) REFERENCES attraction(id))
    ''')

with open('taipei-attractions', 'r', encoding ='utf-8') as file:
    data_dict = json.load(file)
