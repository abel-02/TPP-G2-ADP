from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Index
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy.dialects.postgresql import UUID
import uuid

Base = declarative_base()


class Empleado(Base):
    __tablename__ = 'empleados'

    # Usamos UUID como PK (opcional pero recomendado en PostgreSQL)
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dni = Column(String(20), unique=True, nullable=False, index=True)  # Índice para búsquedas frecuentes
    nombre = Column(String(100), nullable=False)
    apellido = Column(String(100), nullable=False)
    registros = relationship("RegistroHorario", back_populates="empleado", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_empleado_dni', 'dni'),  # Índice adicional para el DNI
    )


class RegistroHorario(Base):
    __tablename__ = 'registros_horario'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    empleado_id = Column(UUID(as_uuid=True), ForeignKey('empleados.id'), nullable=False)
    tipo = Column(String(10), nullable=False)  # 'entrada' o 'salida'
    fecha_hora = Column(DateTime(timezone=True), default=datetime.utcnow)  # UTC para consistencia
    empleado = relationship("Empleado", back_populates="registros")

    __table_args__ = (
        Index('idx_registro_empleado_fecha', 'empleado_id', 'fecha_hora'),  # Índice compuesto
    )


# Conexión a PostgreSQL (ajusta los parámetros)
DATABASE_URL = "postgresql+psycopg2://user:password@localhost:5432/nombre_db"
engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)