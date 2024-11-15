"""
ESQUEMA PARA LA GUARDAR LOS POLYGONOS
"""

from sqlalchemy import create_engine, Column, Integer, String, JSON
from sqlalchemy.orm import sessionmaker, declarative_base
from geoalchemy2 import Geometry


Base = declarative_base()

class Sector(Base):
    __tablename__ = 'sectores'
    
    id = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)
    geom = Column(Geometry(geometry_type='POLYGON', srid=4326))

    def __repr__(self):
        return f"<Sector(nombre={self.nombre}, latitud={self.latitud}, longitud={self.longitud})>"

# Define la URL de la base de datos
DATABASE_URL = 'postgresql://postgres:elvin123@localhost:5432/apagones_db'

# Crear el motor
engine = create_engine(DATABASE_URL)

# Crear todas las tablas en la base de datos (si no existen)
Base.metadata.create_all(engine)

# Crear una sesión
Session = sessionmaker(bind=engine)
session = Session()
