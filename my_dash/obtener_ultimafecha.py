from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime, Index
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from datetime import datetime
import pandas as pd
import joblib
import psycopg2
from esquemaDB import MedicionesSector

# Configuración de la base de datos
engine = create_engine('postgresql://postgres:EgRjEpfPLsdgCTCQRAgyfSaIdBatsHQI@postgres.railway.internal:5432/railway')
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
def get_data_from_db(date):
    conn = psycopg2.connect(
        host="localhost",
        database="apagones_db",
        user="postgres",
        password="elvin123"
    )
    
    query = f"""
    SELECT *
    FROM mediciones_sector
    WHERE fecha = '{date}';
    """
    
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# Función para obtener la última fecha registrada en MedicionesSector
def get_last_date():
    session = SessionLocal()
    last_record = session.query(MedicionesSector).order_by(MedicionesSector.fecha.desc()).first()
    session.close()
    return last_record.fecha if last_record else None

# Función para verificar si ya existe una predicción para la fecha y sector dados
def prediction_exists(sector, fecha):
    session = SessionLocal()
    existe = session.query(PrediccionesApagones).filter(
        PrediccionesApagones.sector == sector,
        PrediccionesApagones.fecha == fecha
    ).first()
    session.close()
    return existe is not None

# Función para predecir e insertar en la base de datos
def predict_and_insert(date=None):
    """
    Realiza predicciones para una fecha específica o la última registrada en la base de datos
    y las guarda en la tabla de predicciones si aún no existen.

    Args:
        date (str): Fecha en formato 'YYYY-MM-DD'. Si es None, usará la última fecha registrada.
    """
    # Si no se especifica la fecha, usar la última fecha registrada
    if date is None:
        date = get_last_date()
    else:
        date = datetime.strptime(date, "%Y-%m-%d").date()

    if not date:
        print("No se encontró ninguna fecha registrada.")
        return

    # Verificar si ya existen predicciones para la fecha
    session = SessionLocal()
    existing_predictions = session.query(PrediccionesApagones).filter(
        PrediccionesApagones.fecha == date
    ).all()
    session.close()

    if existing_predictions:
        print(f"Ya existen predicciones para la fecha {date}. No se realizarán nuevas predicciones.")
        return

    # Obtener datos de la fecha especificada
    df = get_data_from_db(date)

    if df.empty:
        print("No hay datos disponibles para la fecha especificada.")
        return

    # Procesar datos
    df['sector_encoded'] = le_sector.transform(df['sector'])
    df['estado_transformadores_encoded'] = le_estado.transform(df['estado_transformadores'])
    
    # Convertir booleanos a enteros
    bool_cols = ['sobrecarga_red', 'trabajos_planificados', 'alerta_climatica']
    df[bool_cols] = df[bool_cols].astype(int)

    # Definir características y escalar
    features = [
        'dia_semana', 'mes', 'hora', 'sector_encoded',
        'temperatura', 'humedad', 'precipitacion', 'velocidad_viento',
        'densidad_poblacional', 'edad_infraestructura', 'capacidad_transformadores',
        'demanda_actual', 'consumo_promedio', 'pico_demanda',
        'dias_ultimo_mantenimiento', 'estado_transformadores_encoded',
        'incidencias_recientes', 'sobrecarga_red', 'trabajos_planificados',
        'alerta_climatica'
    ]
    
    X = df[features]
    X_scaled = scaler.transform(X)

    # Realizar predicciones
    df['probabilidad_apagon'] = model_prob.predict(X_scaled)
    df['duracion_apagon'] = model_dur.predict(X_scaled)

    # Insertar predicciones en la base de datos
    session = SessionLocal()
    for _, row in df.iterrows():
        # Verificar si ya existe una predicción con el mismo sector y fecha
        if not prediction_exists(row['sector'], date):
            prediccion = PrediccionesApagones(
                sector=row['sector'],
                probabilidad_apagon=row['probabilidad_apagon'],
                duracion_estimada=row['duracion_apagon'],
                fecha=date
            )
            session.add(prediccion)

    session.commit()
    session.close()
    print(f"Predicciones para la fecha {date} guardadas exitosamente.")

# Realizar predicciones y almacenar en la base de datos
predict_and_insert()  # Llamada a la función para ejecutar la predicción e inserción

