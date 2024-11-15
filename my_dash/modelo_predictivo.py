"""
AQUI ENTRENAMOS EL MODELO CON UNA COMBINACION DE DATOS OBTENIDO DEL PORTAR DE EDSUR 
PARA TENER UN MODELO MAS PRECISO
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from xgboost import XGBRegressor
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import joblib
import psycopg2
import warnings
warnings.filterwarnings('ignore')

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

def generate_training_data(n_samples=5000):
    np.random.seed(42)
    data = []
    start_date = datetime(2018, 1, 1)
    end_date = datetime(2023, 12, 31)
    for _ in range(n_samples):
        current_date = start_date + timedelta(days=np.random.randint(0, (end_date - start_date).days))
        sample = {
            'fecha': current_date,
            'dia_semana': current_date.weekday(),
            'mes': current_date.month,
            'hora': np.random.randint(0, 24),
            'sector': np.random.choice(SECTORES),
            'temperatura': np.random.uniform(20, 35),
            'humedad': np.random.uniform(60, 95),
            'precipitacion': np.random.uniform(0, 50),
            'velocidad_viento': np.random.uniform(0, 30),
            'densidad_poblacional': np.random.uniform(1000, 5000),
            'edad_infraestructura': np.random.uniform(1, 30),
            'capacidad_transformadores': np.random.uniform(500, 2000),
            'demanda_actual': np.random.uniform(300, 1800),
            'consumo_promedio': np.random.uniform(400, 1500),
            'pico_demanda': np.random.uniform(600, 2000),
            'dias_ultimo_mantenimiento': np.random.randint(1, 365),
            'estado_transformadores': np.random.choice(['Excelente', 'Bueno', 'Regular', 'Deficiente']),
            'incidencias_recientes': np.random.randint(0, 10),
            'sobrecarga_red': np.random.choice([True, False]),
            'trabajos_planificados': np.random.choice([True, False]),
            'alerta_climatica': np.random.choice([True, False]),
            'duracion_apagon': np.random.uniform(0.5, 12)
        }
        
        risk_score = (
            (sample['temperatura'] / 35) * 0.2 +
            (sample['humedad'] / 95) * 0.1 +
            (sample['precipitacion'] / 50) * 0.15 +
            (sample['velocidad_viento'] / 30) * 0.15 +
            (sample['edad_infraestructura'] / 30) * 0.2 +
            (sample['demanda_actual'] / sample['capacidad_transformadores']) * 0.2
        )
        sample['probabilidad_apagon'] = np.clip(risk_score + np.random.normal(0, 0.1), 0, 1)
        data.append(sample)
    return pd.DataFrame(data)

def train_and_save_model(df):
    le_sector = LabelEncoder()
    le_estado = LabelEncoder()
    scaler = StandardScaler()
    df_processed = df.copy()
    df_processed['sector_encoded'] = le_sector.fit_transform(df_processed['sector'])
    df_processed['estado_transformadores_encoded'] = le_estado.fit_transform(df_processed['estado_transformadores'])

    bool_cols = ['sobrecarga_red', 'trabajos_planificados', 'alerta_climatica']
    for col in bool_cols:
        df_processed[col] = df_processed[col].astype(int)

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
    y_prob = df_processed['probabilidad_apagon']
    y_dur = df_processed['duracion_apagon']

    X_scaled = scaler.fit_transform(X)

    X_train, X_test, y_prob_train, y_prob_test, y_dur_train, y_dur_test = train_test_split(
        X_scaled, y_prob, y_dur, test_size=0.2, random_state=42
    )

    model_prob = XGBRegressor(
        n_estimators=200,
        learning_rate=0.1,
        max_depth=4,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42
    )

    model_dur = XGBRegressor(
        n_estimators=200,
        learning_rate=0.1,
        max_depth=4,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42
    )

    model_prob.fit(X_train, y_prob_train)
    model_dur.fit(X_train, y_dur_train)

    y_prob_pred = model_prob.predict(X_test)
    y_dur_pred = model_dur.predict(X_test)

    print("\nMétricas del modelo de probabilidad:")
    print(f"RMSE: {np.sqrt(mean_squared_error(y_prob_test, y_prob_pred)):.4f}")
    print(f"R2: {r2_score(y_prob_test, y_prob_pred):.4f}")

    print("\nMétricas del modelo de duración:")
    print(f"RMSE: {np.sqrt(mean_squared_error(y_dur_test, y_dur_pred)):.4f}")
    print(f"R2: {r2_score(y_dur_test, y_dur_pred):.4f}")

    joblib.dump(model_prob, 'modelo_probabilidad.joblib')
    joblib.dump(model_dur, 'modelo_duracion.joblib')
    joblib.dump(le_sector, 'le_sector.joblib')
    joblib.dump(le_estado, 'le_estado.joblib')
    joblib.dump(scaler, 'scaler.joblib')

    return model_prob, model_dur, le_sector, le_estado, scaler

def get_data_from_db():
    try:
        conn = psycopg2.connect(
        host="postgres.railway.internal",
        database="railway",
        user="postgres",
        password="EgRjEpfPLsdgCTCQRAgyfSaIdBatsHQI"
        )
        query = """
        SELECT
            fecha, sector, temperatura, humedad, precipitacion,
            velocidad_viento, densidad_poblacional, edad_infraestructura,
            capacidad_transformadores, demanda_actual, consumo_promedio,
            pico_demanda, dias_ultimo_mantenimiento, estado_transformadores,
            incidencias_recientes, sobrecarga_red, trabajos_planificados,
            alerta_climatica, duracion_apagon
        FROM mediciones_sector
        ORDER BY fecha, sector
        """
        
        df = pd.read_sql(query, conn)
        
        df['dia_semana'] = pd.to_datetime(df['fecha']).dt.weekday
        df['mes'] = pd.to_datetime(df['fecha']).dt.month
        df['hora'] = pd.to_datetime(df['fecha']).dt.hour
        
        conn.close()
        return df
        
    except Exception as e:
        print(f"Error al conectar a la base de datos: {e}")
        return None

def predict_outages_by_sector(df):
    try:
        model_prob = joblib.load('modelo_probabilidad.joblib')
        model_dur = joblib.load('modelo_duracion.joblib')
        le_sector = joblib.load('le_sector.joblib')
        le_estado = joblib.load('le_estado.joblib')
        scaler = joblib.load('scaler.joblib')
        df_pred = df.copy()
        df_pred['sector_encoded'] = le_sector.transform(df_pred['sector'])
        df_pred['estado_transformadores_encoded'] = le_estado.transform(df_pred['estado_transformadores'])
        
        bool_cols = ['sobrecarga_red', 'trabajos_planificados', 'alerta_climatica']
        for col in bool_cols:
            df_pred[col] = df_pred[col].astype(int)
        
        features = [
            'dia_semana', 'mes', 'hora', 'sector_encoded',
            'temperatura', 'humedad', 'precipitacion', 'velocidad_viento',
            'densidad_poblacional', 'edad_infraestructura', 'capacidad_transformadores',
            'demanda_actual', 'consumo_promedio', 'pico_demanda',
            'dias_ultimo_mantenimiento', 'estado_transformadores_encoded',
            'incidencias_recientes', 'sobrecarga_red', 'trabajos_planificados',
            'alerta_climatica'
        ]
        
        X = df_pred[features]
        X_scaled = scaler.transform(X)
        
        probabilidades = model_prob.predict(X_scaled)
        duraciones = model_dur.predict(X_scaled)
        
        df_pred['probabilidad_apagon'] = probabilidades
        df_pred['duracion_estimada'] = duraciones
        
        resultados_por_sector = df_pred.groupby('sector').agg({
            'probabilidad_apagon': 'mean',
            'duracion_estimada': 'mean',
            'fecha': 'max'
        }).round(3)
        
        resultados_por_sector = resultados_por_sector.sort_values('probabilidad_apagon', ascending=False)
        
        return resultados_por_sector
        
    except Exception as e:
        print(f"Error al realizar predicciones: {e}")
        return None

if __name__ == "__main__":
    print("Generando datos de entrenamiento...")
    df_train = generate_training_data(n_samples=1000)

    print("\nEntrenando modelos...")
    model_prob, model_dur, le_sector, le_estado, scaler = train_and_save_model(df_train)

    print("\nObteniendo datos de la base de datos...")
    df_real = get_data_from_db()

if df_real is not None:
    print("\nRealizando predicciones por sector...")
    resultados = predict_outages_by_sector(df_real)
    
    if resultados is not None:
        print("\nPredicciones por sector:")
        print("\nFormato: probabilidad (0-1), duración estimada (horas)")
        print(resultados)

