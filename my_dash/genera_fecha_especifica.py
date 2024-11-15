import random
from datetime import datetime
from sqlalchemy.orm import Session
from Proyecto_Final.my_dash.esquemaDB import MedicionesSector, SessionLocal  # Ajusta según tu configuración de modelo y sesión
import names  # Asegúrate de tener el paquete `names` instalado
import numpy as np

# Lista de sectores
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

# Estados posibles de transformadores
ESTADOS_TRANSFORMADORES = ['Excelente', 'Bueno', 'Regular', 'Deficiente']

def generar_datos_fecha_especifica(fecha: str):
    """
    Genera y guarda datos de mediciones para cada sector en una fecha específica.

    Args:
        fecha (str): Fecha en formato 'YYYY-MM-DD' para la cual se generarán los datos.
    """
    # Convertir la fecha en objeto datetime
    fecha_actual = datetime.strptime(fecha, "%Y-%m-%d").date()
    
    # Crear una sesión de la base de datos
    session = SessionLocal()

    try:
        # Crear registros para cada sector
        for sector in SECTORES:
            # Generar datos aleatorios para el registro
            nombre_completo = f"{names.get_first_name()} {names.get_last_name()}"
            correo_electronico = f"{nombre_completo.lower().replace(' ', '.')}@ejemplo.com"
            
            # Crear un nuevo registro de MedicionesSector con datos simulados
            nuevo_registro = MedicionesSector(
                nombre_completo=nombre_completo,
                correo_electronico=correo_electronico,
                fecha=fecha_actual,
                dia_semana=fecha_actual.weekday(),
                mes=fecha_actual.month,
                hora=random.randint(0, 23),
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
            
            # Agregar el registro a la sesión
            session.add(nuevo_registro)
        
        # Confirmar todos los registros en la base de datos
        session.commit()
        print(f"Datos generados y guardados para la fecha {fecha}.")

    except Exception as e:
        # Revertir en caso de error
        session.rollback()
        print(f"Error al guardar los datos: {e}")
    
    finally:
        # Cerrar la sesión
        session.close()

# Ejemplo de uso
generar_datos_fecha_especifica("2024-11-04")
