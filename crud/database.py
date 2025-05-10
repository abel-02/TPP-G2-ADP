import psycopg2
from psycopg2 import sql
import os


class Database:
    def __init__(self):
        self.conn = None
        self.connect()

    def connect(self):
        "conectando con la base de datos"
        try:
            self.conn = psycopg2.connect(
                dbname=os.getenv("DB_NAME", "nombre_db_existente"),  # Nombre de tu BD
                user=os.getenv("DB_USER", "tu_usuario"),
                password=os.getenv("DB_PASSWORD", "tu_contraseña"),
                host=os.getenv("DB_HOST", "localhost"),
                port=os.getenv("DB_PORT", "5432")
            )
            print("✅ Conectado a PostgreSQL")
        except Exception as e:
            print(f"❌ Error al conectar: {e}")
            raise

    # Elimina create_tables() si ya existen las tablas
    def close(self):
        if self.conn:
            self.conn.close()


db = Database()