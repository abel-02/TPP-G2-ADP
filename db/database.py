import psycopg2

DATABASE_URL = "dbname=nombre_db user=user password=password host=localhost port=5432"

def get_db():
    conn = psycopg2.connect(DATABASE_URL)
    try:
        yield conn
    finally:
        conn.close()