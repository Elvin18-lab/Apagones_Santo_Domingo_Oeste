import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sectorDB import Sector


def cargar_geojson_a_bd(ruta_geojson, database_url):
    try:
        engine = create_engine(database_url)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Cargar el archivo GeoJSON
        with open(ruta_geojson, 'r', encoding='utf-8') as f:
            geojson_data = json.load(f)

        for feature in geojson_data['features']:
            if feature['geometry']['type'] == 'Polygon':
                coords = feature['geometry']['coordinates'][0]  # Obtener las coordenadas del polígono
                nombre = feature['properties'].get('name', 'Sector sin nombre')

                nuevo_sector = Sector(nombre=nombre, coordenadas=coords)
                session.add(nuevo_sector)

        session.commit()  # Guardar cambios en la base de datos
        session.close()
        print(f"Se han cargado {len(geojson_data['features'])} sectores en la base de datos.")
    except Exception as e:
        print(f"Ocurrió un error: {e}")


# Ejemplo de uso
DATABASE_URL = 'postgresql://postgres:EgRjEpfPLsdgCTCQRAgyfSaIdBatsHQI@postgres.railway.internal:5432/railway'
ruta_geojson = 'C:/Users/elvin/Downloads/Practica/formulario_SDOeste/Proyecto_Final/geojson/sectores_unidos.geojson'

cargar_geojson_a_bd(ruta_geojson, DATABASE_URL)
