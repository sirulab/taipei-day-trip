# review week5 connect db
# https://dev.mysql.com/doc/connector-python/en/connector-python-examples.html

import json
import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="2365533",
    database="taipei_day_trip",
    charset="utf8mb4"
) 
# 沒有也可以 charset="utf8mb4"
# 沒有也可以 DEFAULT CHARSET=utf8mb4

cursor = conn.cursor()

cursor.execute('DROP TABLE IF EXISTS image') ### 假設資料常變動與不常變動
cursor.execute('DROP TABLE IF EXISTS attraction') 

# IF NOT EX IST S | ?每個都 NOT NULL | ?不要事後改 | info_date 或 build_date
cursor.execute('''CREATE TABLE IF NOT EXISTS attraction (
    id INT PRIMARY KEY,
    name VARCHAR(255),
    rate INT,
    direction TEXT,
    date DATE,
    longitude DOUBLE,
    latitude DOUBLE,
    mrt VARCHAR(100),
    serial_no VARCHAR(100),
    cat VARCHAR(100),
    memo_time TEXT,
    description TEXT,
    address TEXT,
    imgurls TEXT) DEFAULT CHARSET=utf8mb4'''
    ) 

#  ON DELETE CASCADE # AUTO_INCREMENT
cursor.execute('''CREATE TABLE IF NOT EXISTS image (
    id INT AUTO_INCREMENT PRIMARY KEY,
    attraction_id INT NOT NULL,
    url VARCHAR(500) NOT NULL,
    FOREIGN KEY (attraction_id) REFERENCES attraction(id)) DEFAULT CHARSET=utf8mb4'''
    )

cursor.execute('TRUNCATE TABLE image') # 清空現有圖片資料

with open('taipei-attractions.json', 'r', encoding ='utf-8') as file:
    data = json.load(file)

attractions = data.get("list", []) # default 避免錯誤
img_host = data.get("img_host", "")

for attr in attractions:
    attr_id = attr.get("_id")

    raw_date = attr.get("date", "")
    formatted_date = raw_date.replace('/', '-') if raw_date else None ###

    sql_attr = """
        INSERT INTO attraction 
        (id, name, rate, direction, date, longitude, latitude, mrt, serial_no, cat, memo_time, description, address, imgurls)
        VALUES (%s,  %s,  %s,  %s,  %s,  %s,  %s,  %s,  %s,  %s,  %s,  %s,  %s, %s)
        """

    val_attr = (
        attr_id,
        attr.get("name"),
        attr.get("rate"),
        attr.get("direction"),
        formatted_date,
        attr.get("longitude"),
        attr.get("latitude"),
        attr.get("MRT"),
        attr.get("SERIAL_NO"),
        attr.get("CAT"),
        attr.get("MEMO_TIME"),
        attr.get("description"),
        attr.get("address"),
        attr.get("imgurls")
        )
    
    cursor.execute(sql_attr, val_attr)

    ###
    imgurls_raw = attr.get("imgurls", "")
    paths = []
    split_result = imgurls_raw.split('/imgs/')
    for p in split_result:
        if p:
            url = f"{img_host}/imgs/{p}"
            sql_img = "INSERT INTO image (attraction_id, url) VALUES (%s, %s)"
            cursor.execute(sql_img, (attr_id, url))

conn.commit()
cursor.close()
conn.close()

print(f"成功從json匯入sql: {len(attractions)} 筆資料與圖片")