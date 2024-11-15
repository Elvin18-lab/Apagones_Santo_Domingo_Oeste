from dash import dcc, html, Input, Output
from datetime import datetime
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from cachetools import cached, TTLCache
import re

# Importar las funciones necesarias
from fecha_futura import ensure_data_for_fecha, predict_and_insert

# Crear la caché para predicciones
cache = TTLCache(maxsize=100, ttl=600)  # Caché de 10 minutos
cache2 = TTLCache(maxsize=100, ttl=600)

# Configurar conexión a la base de datos
DATABASE_URL = "postgresql://postgres:elvin123@localhost/apagones_db"  # Reemplaza con tus credenciales
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def clean_probability(probabilidad):
    """Limpia y convierte el valor de probabilidad de apagón a un número entre 0 y 1."""
    if isinstance(probabilidad, str):
        probabilidad = re.sub(r'[^\d.]', '', probabilidad)
    try:
        probabilidad = float(probabilidad)
        if 0 <= probabilidad <= 100:
            return probabilidad / 100
    except (ValueError, TypeError):
        return None
    return None


def clean_duration(duracion):
    """Convierte la duración en formato de cadena o flotante a un valor en horas."""    
    if isinstance(duracion, str):
        # Si es una cadena con formato 'HH:MM'
        duracion = re.sub(r'[^\d:]', '', duracion)
        try:
            duracion_split = [int(x) for x in duracion.split(":")]
            if len(duracion_split) == 2:
                horas, minutos = duracion_split
                return horas + minutos / 60
        except (ValueError, TypeError):
            return None
    elif isinstance(duracion, (int, float)):
        # Si la duración es un número (flotante o entero)
        return float(duracion)
    return None

def normalize_probability(probabilidad):
    """Formatea la probabilidad en porcentaje con dos decimales."""
    if probabilidad is not None:
        return f"{probabilidad * 100:.2f}%"  # Ahora con dos decimales
    return "N/A"


def formatear_duracion_horas(duracion):
    """Formatea la duración en horas y minutos."""
    if duracion is not None:
        horas = int(duracion)
        minutos = int((duracion - horas) * 60)
        return f"{horas}h {minutos}m"
    return "N/A"


@cached(cache)  # Caché de 10 minutos
def fetch_predictions(fecha, force_refresh=False):
    """Obtiene los datos de predicciones de la base de datos para una fecha específica."""
    if force_refresh:
        cache.clear()
    with SessionLocal() as db:
        query = """
            SELECT sector, probabilidad_apagon, duracion_estimada, fecha 
            FROM predicciones_apagones 
            WHERE fecha::date = %(fecha)s
        """
        df = pd.read_sql_query(query, db.bind, params={"fecha": fecha})
        df['probabilidad_apagon'] = df['probabilidad_apagon'].apply(lambda x: clean_probability(x))
        df['duracion_estimada'] = df['duracion_estimada'].apply(lambda x: clean_duration(x))
        return df.dropna(subset=['probabilidad_apagon', 'duracion_estimada'])


@cached(cache2)
def obtener_prediciones(fecha, force_refresh=False):
    """Obtiene las predicciones futuras de la base de datos para una fecha específica."""
    if force_refresh:
        cache2.clear()
    with SessionLocal() as db:
        query = """
            SELECT sector, probabilidad_apagon, duracion_estimada, fecha 
            FROM predicciones_futuras 
            WHERE fecha::date = %(fecha)s
        """
        df = pd.read_sql_query(query, db.bind, params={"fecha": fecha})
        df['probabilidad_apagon'] = df['probabilidad_apagon'].apply(lambda x: clean_probability(x))
        df['duracion_estimada'] = df['duracion_estimada'].apply(lambda x: clean_duration(x))
        return df.dropna(subset=['probabilidad_apagon', 'duracion_estimada'])


def register_prediccion_callbacks(dash_app):
    """Registra los callbacks para la predicción de apagones."""
    @dash_app.callback(
        Output('table-predicciones', 'data'),
        [Input('input-fecha', 'date')]
    )
    def update_predictions(fecha):
        if fecha:
            try:
                fecha_dt = datetime.strptime(fecha, '%Y-%m-%d')
                with SessionLocal() as db:
                    # Primero intentamos obtener las predicciones actuales
                    df = fetch_predictions(fecha_dt, force_refresh=True)
                    if df.empty:
                        # Si no hay datos, generamos predicciones futuras
                        new_registro = ensure_data_for_fecha(fecha_dt, db)
                        predict_and_insert(new_registro, db)
                        df = obtener_prediciones(fecha_dt, force_refresh=True)

                    # Normalizar la probabilidad y la duración
                    df['probabilidad_apagon'] = df['probabilidad_apagon'].apply(normalize_probability)
                    df['duracion_estimada'] = df['duracion_estimada'].apply(formatear_duracion_horas)
                    return df.to_dict('records')
            except Exception as e:
                print(f"Error al obtener o procesar predicciones: {e}")
                return []
        return []  # Si no hay fecha, se devuelve un arreglo vacío























