import sqlite3
import os

# Use environment variable for database path, fallback to local
DBNAME = os.environ.get('DB_PATH', 'database.db')

# Ensure data directory exists for Docker
os.makedirs(os.path.dirname(DBNAME) if os.path.dirname(DBNAME) else '.', exist_ok=True)

def init_db():
    with sqlite3.connect(DBNAME) as conn:
        cursor = conn.cursor()
        query = """
        CREATE TABLE IF NOT EXISTS URLS(
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        URL TEXT NOT NULL,
        SHORT_URL TEXT NOT NULL,
        CREATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        cursor.execute(query)
        conn.commit()


def insert_url(url, short_url):
    with sqlite3.connect(DBNAME) as conn:
        cursor = conn.cursor()
        query = """
        INSERT INTO URLS(URL, SHORT_URL) VALUES (?, ?)
        """
        cursor.execute(query, (url, short_url))
        conn.commit()

def get_url(short_url):
    with sqlite3.connect(DBNAME) as conn:
        cursor = conn.cursor()
        query = """
        SELECT URL FROM URLS WHERE SHORT_URL = ?
        """
        cursor.execute(query, (short_url,))
        result = cursor.fetchone()
        return result

def deleteUrl(short_url: str):
    with sqlite3.connect(DBNAME) as conn:
        cursor = conn.cursor()
        query = """
        DELETE FROM URLS WHERE SHORT_URL = ?
        """
        cursor.execute(query, (short_url,))
        conn.commit()  

def getAllUrls():
    with sqlite3.connect(DBNAME) as conn:
        cursor = conn.cursor()
        query = """
        SELECT URL, SHORT_URL FROM URLS ORDER BY CREATED_AT DESC
        """
        cursor.execute(query)
        results = cursor.fetchall()
        return [{"url": row[0], "short_url": row[1]} for row in results]  
        