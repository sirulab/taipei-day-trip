import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="2365533",
    database="taipei_day_trip",
    charset="utf8mb4"
)
cursor = conn.cursor()
cursor.execute("SHOW COLUMNS FROM attraction")
# DESCRIBE attraction; # SHOW COLUMNS FROM attraction; # SELECT * FROM attraction LIMIT 3
for row in cursor.fetchall():
    print(row)