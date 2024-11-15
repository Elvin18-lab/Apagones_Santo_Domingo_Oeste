import geopandas as gpd
from sqlalchemy import create_engine
from geoalchemy2 import WKBElement
from sqlalchemy.orm import sessionmaker
from sectorDB import Sector  # Asegúrate de que esta clase está correctamente configurada

# Configura la conexión a la base de datos
db_url = "postgresql://postgres:EgRjEpfPLsdgCTCQRAgyfSaIdBatsHQI@postgres.railway.internal:5432/railway"
engine = create_engine(db_url)
Session = sessionmaker(bind=engine)
session = Session()

# Lee el archivo GeoJSON
gdf = gpd.read_file("C:/Users/elvin/Downloads/Practica/formulario_SDOeste/Proyecto_Final/geojson/sectores_unidos.geojson")

# Inserta cada sector en la base de datos
for _, row in gdf.iterrows():
    nombre = row["name"]  # Asegúrate de que el nombre del campo es correcto
    geom_wkb = WKBElement(row["geometry"].wkb, srid=4326)  # Convierte la geometría a WKB
    
    # Crea una instancia de Sector
    sector = Sector(nombre=nombre, geom=geom_wkb)
    
    # Agrega a la sesión
    session.add(sector)

# Confirma los cambios en la base de datos
try:
    session.commit()
    print("Sectores guardados exitosamente en la base de datos.")
except Exception as e:
    session.rollback()
    print(f"Ocurrió un error: {e}")
finally:
    session.close()


