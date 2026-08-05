import mysql.connector
from mysql.connector import pooling

import os
from dotenv import load_dotenv
load_dotenv()

dbconfig = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": "taipei_day_trip",
    "charset": "utf8mb4"
}

cnxpool = pooling.MySQLConnectionPool(
    pool_name="taipei_pool",
    pool_size=5,
    **dbconfig
)

def get_db_connection():
    return cnxpool.get_connection()