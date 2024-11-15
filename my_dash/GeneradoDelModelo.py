from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import random
import names
from esquemaDB import MedicionesSector

# Configuración de la conexión a la base de datos
engine = create_engine('postgresql://postgres:elvin123@localhost/apagones_db')
SessionLocal = sessionmaker(bind=engine)

# Lista de sectores y estados de transformadores
SECTORES = [
    "Zona Industrial de Herrera", "Ensanche Altagracia", "Hato Nuevo", 
    "Bayona", "El Abanico", "El Libertador", "Buenos Aires", 
    "Las Palmas", "Enriquillo", "Manoguayabo", "La Venta", "Las Caobas"
]
ESTADOS_TRANSFORMADORES = ['Excelente', 'Bueno', 'Regular', 'Deficiente']

# Función para guardar registros solo para la fecha actual
def guardar_registros_fecha_actual():
    # Obtener la fecha de hoy
    fecha_actual = date.today()

    # Crear una sesión de base de datos
    session = SessionLocal()

    # Recorremos cada sector para agregar registros si no existen para la fecha actual
    for sector in SECTORES:
        try:
            # Verificar si ya existe un registro para la fecha y sector actual
            existe = session.query(MedicionesSector).filter(
                MedicionesSector.fecha == fecha_actual,
                MedicionesSector.sector == sector
            ).first()

            if not existe:
                # Generar nombre y correo electrónico
                nombre_completo = f"{names.get_first_name()} {names.get_last_name()}"
                correo_electronico = f"{nombre_completo.lower().replace(' ', '.')}@ejemplo.com"

                # Crear nuevo registro con valores aleatorios
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

                # Agregar el nuevo registro a la sesión
                session.add(nuevo_registro)
                session.commit()  # Confirmar la inserción de cada registro
            else:
                print(f"Registro ya existente para {fecha_actual} en {sector}.")

        except Exception as e:
            print("Error al guardar los datos:", e)
            session.rollback()

    # Cerrar la sesión al finalizar
    session.close()

# Llamar a la función para guardar los registros
guardar_registros_fecha_actual()

