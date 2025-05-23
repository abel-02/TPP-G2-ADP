import psycopg2
from psycopg2 import pool  # Opcional para connection pooling
import os


# Cargar variables de entorno desde .env


class Database:
    # Configuración para Supabase (actualizada)
    _config = {
        "dbname": "database_labo",  # Nombre de la BD en Supabase (por defecto es 'postgres')
        "user": "database_labo_owner",    # Usuario por defecto en Supabase
        "password": "npg_T2tevF4uMhZB",  # Contraseña (DEBES configurarla en .env)
        "host": "ep-gentle-poetry-a48jtsf3-pooler.us-east-1.aws.neon.tech",  # Endpoint de Supabase
        "port": "5432",        # Puerto por defecto
        # Opcional: forzar SSL (recomendado para Supabase)

    }

    def __init__(self):
        try:
            self.pool = pool.SimpleConnectionPool(1, 10, **self._config)
            print("✅ Pool de conexiones a PostgreSQL iniciado")
        except Exception as e:
            print(f"❌ Error al crear pool de conexiones: {e}")
            raise

    def get_conn_cursor(self):
        """Obtiene una conexión y cursor, debes cerrarlos después de usarlos."""
        conn = self.pool.getconn()
        return conn, conn.cursor()

    def put_conn(self, conn):
        """Devuelve la conexión al pool"""
        if conn:
            self.pool.putconn(conn)

    def close_all(self):
        """Cierra todas las conexiones del pool"""
        self.pool.closeall()
        print("🔌 Todas las conexiones cerradas")


# Instancia global
db = Database() 