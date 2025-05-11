import psycopg2
from psycopg2 import pool  # Opcional para connection pooling
import os

class Database:
    # Configuración centralizada
    _config = {
        "dbname": "shain_flow",
        "user": "equipo_tp",
        "password": "NicoYazawa",  # ¡Usa variables de entorno en producción!
        "host": "100.107.247.95",
        "port": "5432"
    }

    def __init__(self):
        self.conn = None
        self.connect()

    def connect(self):
        """Establece la conexión a la BD"""
        try:
            self.conn = psycopg2.connect(**self._config)
            print("✅ Conexión exitosa a PostgreSQL")
        except Exception as e:
            print(f"❌ Error al conectar: {e}")
            raise

    def get_cursor(self):
        """Devuelve un cursor para ejecutar queries"""
        return self.conn.cursor()

    def close(self):
        """Cierra conexión y cursor"""
        if self.conn:
            self.conn.close()
            print("🔌 Conexión cerrada")

# Instancia global
db = Database()