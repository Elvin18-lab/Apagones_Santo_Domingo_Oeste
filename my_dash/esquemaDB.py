"""
ESTE SIMULA INGRESO DE DATOS PARA TENER UNA FLUTOSIDAD DE DATOS PARA QUE EL MODELO LO ULTILIZE PARA PREDECIR 
LOS DATOS DEL MODELO ESTE SE GUARDA EN LA BASE DE DATOS
( mediciones_sector)
"""

from sqlalchemy import create_engine, Column, Integer, Float, String, Boolean, DateTime, Index
from sqlalchemy.orm import sessionmaker, declarative_base
import random
import names
import numpy as np
from datetime import datetime, timedelta

# Configuración de la base de datos
engine = create_engine('postgresql://postgres:EgRjEpfPLsdgCTCQRAgyfSaIdBatsHQI@postgres.railway.internal:5432/railway')
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine)

# Definición del modelo
class MedicionesSector(Base):
    __tablename__ = "mediciones_sector"
    
    id = Column(Integer, primary_key=True, index=True)
    nombre_completo = Column(String(200), nullable=False)
    correo_electronico = Column(String(200), nullable=False)
    fecha = Column(DateTime, nullable=False)
    dia_semana = Column(Integer, nullable=False)
    mes = Column(Integer, nullable=False)
    hora = Column(Integer, nullable=False)
    sector = Column(String(100), nullable=False)
    temperatura = Column(Float, nullable=False)
    humedad = Column(Float, nullable=False)
    precipitacion = Column(Float, nullable=False)
    velocidad_viento = Column(Float, nullable=False)
    densidad_poblacional = Column(Float, nullable=False)
    edad_infraestructura = Column(Float, nullable=False)
    capacidad_transformadores = Column(Float, nullable=False)
    demanda_actual = Column(Float, nullable=False)
    consumo_promedio = Column(Float, nullable=False)
    pico_demanda = Column(Float, nullable=False)
    dias_ultimo_mantenimiento = Column(Integer, nullable=False)
    estado_transformadores = Column(String(20), nullable=False)
    incidencias_recientes = Column(Integer, nullable=False)
    sobrecarga_red = Column(Boolean, default=False)
    trabajos_planificados = Column(Boolean, default=False)
    alerta_climatica = Column(Boolean, default=False)
    duracion_apagon = Column(Float, nullable=False)

    __table_args__ = (
        Index('idx_fecha_sector_hora', 'fecha', 'sector', 'hora', unique=True),
    )

def generate_continuous_data(start_date, end_date):
    SECTORES = [
        "Zona Industrial de Herrera",
        "Ensanche Altagracia",
        "Hato Nuevo",
        "Bayona",
        "El Abanico",
        "El Libertador",
        "Buenos Aires",
        "Las Palmas",
        "Enriquillo",
        "Manoguayabo",
        "La Venta",
        "Las Caobas",
    ]
    
    ESTADOS_TRANSFORMADORES = ['Excelente', 'Bueno', 'Regular', 'Deficiente']
    
    data = []
    current_date = start_date
    
    while current_date <= end_date:
        for sector in SECTORES:
            # Generar nombre y correo electrónico
            nombre_completo = f"{names.get_first_name()} {names.get_last_name()}"
            correo_electronico = f"{nombre_completo.lower().replace(' ', '.')}@ejemplo.com"
            
            # Generar registro
            registro = MedicionesSector(
                nombre_completo=nombre_completo,
                correo_electronico=correo_electronico,
                fecha=current_date,
                dia_semana=current_date.weekday(),
                mes=current_date.month,
                hora=np.random.randint(0, 24),
                sector=sector,
                temperatura=round(random.uniform(20, 35), 2),
                humedad=round(random.uniform(60, 95), 2),
                precipitacion=round(random.uniform(0, 50), 2),
                velocidad_viento=round(random.uniform(0, 30), 2),
                densidad_poblacional=round(random.uniform(1000, 5000), 2),
                edad_infraestructura=round(random.uniform(1, 30), 2),
                capacidad_transformadores=round(random.uniform(500, 2000), 2),
                demanda_actual=round(random.uniform(300, 1800), 2),
                consumo_promedio=round(random.uniform(400, 1500), 2),
                pico_demanda=round(random.uniform(600, 2000), 2),
                dias_ultimo_mantenimiento=random.randint(1, 365),
                estado_transformadores=random.choice(ESTADOS_TRANSFORMADORES),
                incidencias_recientes=random.randint(0, 10),
                sobrecarga_red=random.choice([True, False]),
                trabajos_planificados=random.choice([True, False]),
                alerta_climatica=random.choice([True, False]),
                duracion_apagon=round(random.uniform(0.5, 12), 2)
            )
    
            data.append(registro)
        
        current_date += timedelta(days=1)
    
    return data

def populate_database():
    start_date = datetime(2018, 1, 1)
    end_date = datetime(2024, 11, 3)
    
    try:
        # Crear las tablas
        Base.metadata.create_all(bind=engine)
        
        # Crear sesión
        session = SessionLocal()
        
        # Generar y guardar datos
        print(f"Generando datos continuos desde {start_date.date()} hasta {end_date.date()}...")
        registros = generate_continuous_data(start_date, end_date)
        
        # Guardar en la base de datos
        for registro in registros:
            # Verificar si ya existe un registro con la misma fecha, sector y hora
            existe = session.query(MedicionesSector).filter(
                MedicionesSector.fecha == registro.fecha,
                MedicionesSector.sector == registro.sector,
                MedicionesSector.hora == registro.hora
            ).first()
            if not existe:
                session.add(registro)
        
        session.commit()
        print(f"Se han guardado {len(registros)} registros exitosamente en la base de datos.")
        
        # Mostrar algunos datos de ejemplo
        print("\nEjemplo de registros guardados:")
        muestra = session.query(MedicionesSector).limit(5).all()
        for registro in muestra:
            print(f"\nNombre Completo: {registro.nombre_completo}")
            print(f"Correo Electrónico: {registro.correo_electronico}")
            print(f"Sector: {registro.sector}")
            print(f"Fecha: {registro.fecha}")
            print(f"Temperatura: {registro.temperatura}°C")
            print(f"Estado Transformadores: {registro.estado_transformadores}")
            print(f"Incidencias Recientes: {registro.incidencias_recientes}")
            print(f"Duración Apagón: {registro.duracion_apagon} horas")
        
    except Exception as e:
        print(f"Error al poblar la base de datos: {e}")
        
    finally:
        session.close()

if __name__ == "__main__":
    populate_database()
