"""
ESTE ARCHIVO GENERADAATOS ESTIAMADO DE LOS DATOS RECOLECTADO DE NUESTRA MUESTRA POR EL FORMULARIO LO 
MAS CERCANO POSIBLE A LA REALIDAD USADOS PARA PREDECIR EN EL MODELO Y SER PROCESADA EN LA BASE DE DATOS
(predicciones_apagones)
"""
from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime, Index
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime, timedelta
import random
import pandas as pd
import numpy as np
import joblib
from sqlalchemy.orm import Session
import psycopg2

# Configuración de la base de datos
engine = create_engine('postgresql://postgres:elvin123@localhost/apagones_db')
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine)

# Definición del modelo para la tabla de predicciones
class PrediccionesApagones(Base):
    __tablename__ = "predicciones_apagones"
    
    id = Column(Integer, primary_key=True, index=True)
    sector = Column(String(100), nullable=False)
    probabilidad_apagon = Column(Float, nullable=False)
    duracion_estimada = Column(Float, nullable=False)
    fecha = Column(DateTime, nullable=False)

    __table_args__ = (
        Index('idx_sector_fecha', 'sector', 'fecha', unique=True),
    )

# Crear las tablas en la base de datos
Base.metadata.create_all(bind=engine)

# Cargar modelos y preprocesadores
model_prob = joblib.load('modelo_probabilidad.joblib')
model_dur = joblib.load('modelo_duracion.joblib')
le_sector = joblib.load('le_sector.joblib')
le_estado = joblib.load('le_estado.joblib')
scaler = joblib.load('scaler.joblib')


# Función para conectar a la base de datos y obtener datos
def get_data_from_db(start_date, end_date):
    conn = psycopg2.connect(
        host="localhost",
        database="apagones_db",
        user="postgres",
        password="elvin123"
    )
    
    query = f"""
    SELECT *
    FROM mediciones_sector
    WHERE fecha BETWEEN '{start_date}' AND '{end_date}';
    """
    
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# Función para predecir e insertar en la base de datos
def predict_and_insert(start_date, end_date):
    # Obtener datos de la base de datos
    df = get_data_from_db(start_date, end_date)

    # Procesar datos
    df_processed = df.copy()
    df_processed['sector_encoded'] = le_sector.transform(df_processed['sector'])
    df_processed['estado_transformadores_encoded'] = le_estado.transform(df_processed['estado_transformadores'])

    # Convertir columnas booleanas
    bool_cols = ['sobrecarga_red', 'trabajos_planificados', 'alerta_climatica']
    for col in bool_cols:
        df_processed[col] = df_processed[col].astype(int)

    # Definir las características
    features = [
        'dia_semana', 'mes', 'hora', 'sector_encoded',
        'temperatura', 'humedad', 'precipitacion', 'velocidad_viento',
        'densidad_poblacional', 'edad_infraestructura', 'capacidad_transformadores',
        'demanda_actual', 'consumo_promedio', 'pico_demanda',
        'dias_ultimo_mantenimiento', 'estado_transformadores_encoded',
        'incidencias_recientes', 'sobrecarga_red', 'trabajos_planificados',
        'alerta_climatica'
    ]

    X = df_processed[features]
    
    # Escalar las características
    X_scaled = scaler.transform(X)

    # Realizar predicciones
    df_processed['probabilidad_apagon'] = model_prob.predict(X_scaled)
    df_processed['duracion_apagon'] = model_dur.predict(X_scaled)

    # Conectar a la base de datos
    db = SessionLocal()
    for index, row in df_processed.iterrows():
        # Verificar si ya existe una predicción con el mismo sector y fecha
        existe = db.query(PrediccionesApagones).filter(
            PrediccionesApagones.sector == row['sector'],
            PrediccionesApagones.fecha == row['fecha']
        ).first()
        
        if not existe:
            prediccion = PrediccionesApagones(
                sector=row['sector'],
                probabilidad_apagon=row['probabilidad_apagon'],
                duracion_estimada=row['duracion_apagon'],
                fecha=row['fecha']
            )
            db.add(prediccion)

    db.commit()
    db.close()

# Especificar el rango de fechas para las predicciones
start_date = '2018-01-01'  # Ajusta a la fecha de inicio deseada
end_date = '2024-11-3'     # Ajusta a la fecha de fin deseada

# Realizar predicciones y almacenar en la base de datos
predict_and_insert(start_date, end_date)

"""
SOLO SE DEBE EJECUTAR UNA SOLA VEZ
"""