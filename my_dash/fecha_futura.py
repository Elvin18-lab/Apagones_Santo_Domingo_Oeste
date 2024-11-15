from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import pandas as pd
import psycopg2
import joblib
from datetime import datetime
from sqlalchemy.orm import Session
from cachetools import cached, LRUCache
from sqlalchemy.exc import NoResultFound
import random
# Configuración de la base de datos
engine = create_engine('postgresql://postgres:elvin123@localhost/apagones_db')
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine)

# Definir la clase MedicionesSector
class MedicionesFuturas(Base):
    __tablename__ = "mediciones_futuras"
    
    id = Column(Integer, primary_key=True, index=True)
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

        # Cambiar el nombre del índice para evitar conflictos
    __table_args__ = (
        Index('idx_mediciones_fecha_sector_hora', 'fecha', 'sector', 'hora', unique=True),
    )

# Definir la clase PrediccionesApagones
class PrediccionesFuturas(Base): 
    __tablename__ = "predicciones_futuras"
    
    id = Column(Integer, primary_key=True, index=True)
    sector = Column(String(100), nullable=False)
    probabilidad_apagon = Column(Float, nullable=False)
    duracion_estimada = Column(Float, nullable=False)
    fecha = Column(DateTime, nullable=False)

    __table_args__ = (
        Index('idx_predicciones_sector_fecha', 'sector', 'fecha', unique=True),
    )

# Crear las tablas en la base de datos
Base.metadata.create_all(bind=engine)

# Cargar modelos y preprocesadores
model_prob = joblib.load('modelo_probabilidad.joblib')
model_dur = joblib.load('modelo_duracion.joblib')
le_sector = joblib.load('le_sector.joblib')
le_estado = joblib.load('le_estado.joblib')
scaler = joblib.load('scaler.joblib')

SECTORES = [
    "Zona Industrial de Herrera", "Ensanche Altagracia", "Hato Nuevo", 
    "Bayona", "El Abanico", "El Libertador", "Buenos Aires", 
    "Las Palmas", "Enriquillo", "Manoguayabo", "La Venta", "Las Caobas"
]
ESTADOS_TRANSFORMADORES = ['Excelente', 'Bueno', 'Regular', 'Deficiente']

def ensure_data_for_fecha(fecha, db_session: Session):
    """Asegura que existan datos para una fecha dada, creando un registro para cada sector si es necesario."""
    registros_existentes = db_session.query(MedicionesFuturas).filter(
        MedicionesFuturas.fecha == fecha
    ).all()

    # Crear un conjunto de sectores existentes para verificar
    sectores_existentes = {registro.sector for registro in registros_existentes}

    # Iterar sobre todos los sectores y agregar registros si no existen
    for sector in SECTORES:
        if sector in sectores_existentes:
            continue  # Si el registro ya existe, continuar al siguiente sector

        # Crear un nuevo registro con datos ficticios o predeterminados
        new_registro = MedicionesFuturas(
            fecha=fecha,  # Solo guardamos la fecha sin hora
            dia_semana=fecha.weekday(),
            mes=fecha.month,
            hora=random.randint(0, 23),  # Generar una hora aleatoria para el registro
            sector=sector,  # Usamos el sector de la iteración
            temperatura=25.0,
            humedad=60.0,
            precipitacion=0.0,
            velocidad_viento=5.0,
            densidad_poblacional=1000.0,
            edad_infraestructura=10.0,
            capacidad_transformadores=100.0,
            demanda_actual=80.0,
            consumo_promedio=75.0,
            pico_demanda=90.0,
            dias_ultimo_mantenimiento=30,
            estado_transformadores=random.choice(ESTADOS_TRANSFORMADORES),
            incidencias_recientes=1,
            sobrecarga_red=False,
            trabajos_planificados=False,
            alerta_climatica=False,
            duracion_apagon=0.0
        )

        # Agregar el nuevo registro a la sesión
        db_session.add(new_registro)

    # Hacer commit solo una vez después de agregar todos los nuevos registros
    db_session.commit()

def predict_and_insert(new_registro, db_session: Session):
    """Realiza predicciones para los registros de la tabla MedicionesFuturas e inserta las predicciones en la base de datos si no existen."""
    # Obtener todos los registros de la tabla MedicionesFuturas
    registros = db_session.query(MedicionesFuturas).all()

    # Procesar cada registro para hacer predicciones
    for registro in registros:
        df_processed = pd.DataFrame([{
            'fecha': registro.fecha,
            'sector': registro.sector,
            'dia_semana': registro.dia_semana,
            'mes': registro.mes,
            'hora': registro.hora,
            'temperatura': registro.temperatura,
            'humedad': registro.humedad,
            'precipitacion': registro.precipitacion,
            'velocidad_viento': registro.velocidad_viento,
            'densidad_poblacional': registro.densidad_poblacional,
            'edad_infraestructura': registro.edad_infraestructura,
            'capacidad_transformadores': registro.capacidad_transformadores,
            'demanda_actual': registro.demanda_actual,
            'consumo_promedio': registro.consumo_promedio,
            'pico_demanda': registro.pico_demanda,
            'dias_ultimo_mantenimiento': registro.dias_ultimo_mantenimiento,
            'estado_transformadores': registro.estado_transformadores,
            'incidencias_recientes': registro.incidencias_recientes,
            'sobrecarga_red': registro.sobrecarga_red,
            'trabajos_planificados': registro.trabajos_planificados,
            'alerta_climatica': registro.alerta_climatica
        }])

        # Procesar datos
        df_processed['sector_encoded'] = le_sector.transform(df_processed['sector'])
        df_processed['estado_transformadores_encoded'] = le_estado.transform(df_processed['estado_transformadores'])

        # Convertir columnas booleanas a enteros
        bool_cols = ['sobrecarga_red', 'trabajos_planificados', 'alerta_climatica']
        df_processed[bool_cols] = df_processed[bool_cols].astype(int)

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

        # Verificar e insertar las predicciones
        for index, row in df_processed.iterrows():
            existe = db_session.query(PrediccionesFuturas).filter(
                PrediccionesFuturas.sector == row['sector'],
                PrediccionesFuturas.fecha == row['fecha']
            ).first()

            if not existe:
                prediccion = PrediccionesFuturas(
                    sector=row['sector'],
                    probabilidad_apagon=row['probabilidad_apagon'],
                    duracion_estimada=row['duracion_apagon'],
                    fecha=row['fecha']
                )
                db_session.add(prediccion)

    # Guardar cambios en la base de datos
    db_session.commit()
