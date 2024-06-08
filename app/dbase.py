import psycopg2
from psycopg2.extras import RealDictCursor
from .config import settings
import time

conn = None
cursor = None

while True:
    try:
        conn = psycopg2.connect(host=settings.database_url,database=settings.database_name,user=settings.database_username,password=settings.database_password,cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print("Connected to the database")
        break
    except Exception as e:
        print(e)
        print("I am unable to connect to the database")
        time.sleep(3)

# def roles():
#     return ['admin', 'user', 'guest']