from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
import os

#  Configuración de la conexión a PostgreSQL (usa variables de entorno)
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://user:password@localhost:5432/empleados_db")

# Crear el motor de SQLAlchemy
engine = create_engine(
    DATABASE_URL,
    pool_size=10,           # Número máximo de conexiones
    max_overflow=5,         # Conexiones adicionales temporales
    pool_pre_ping=True,     # Verifica conexiones activas
    echo=False             # True para debug (muestra SQL generado)
)

#  Fábrica de sesiones
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

#  Base para los modelos
Base = declarative_base()

#  Dependencia para inyectar sesiones en rutas (FastAPI)
def get_db():
    """Generador de sesiones para FastAPI."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

#  Context manager para uso fuera de FastAPI (scripts, tests)
@contextmanager
def session_scope():
    """Proporciona una sesión transaccional segura."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()