import mysql.connector

# 用 utf8mb4 連線拿拿看資料
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="2365533",
    database="taipei_day_trip",
    charset="utf8mb4"
)
cursor = conn.cursor()
cursor.execute("SELECT id, name, address FROM attraction LIMIT 3")

for row in cursor.fetchall():
    print(row)