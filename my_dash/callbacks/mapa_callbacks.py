import dash
from dash import Input, Output
from layouts.mapa import create_map_layout
from cachetools import TTLCache, cached
import pandas as pd
import geopandas as gpd
from sqlalchemy import create_engine
from shapely import wkt
import plotly.express as px
from datetime import timedelta

# Configurar caché con un tiempo de vida de 2 horas
cache = TTLCache(maxsize=100, ttl=7200)  # 7200 segundos = 2 horas

# Conectar a la base de datos PostgreSQL
engine = create_engine('postgresql://postgres:elvin123@localhost:5432/apagones_db')

@cached(cache)
def cargar_datos(fecha=None):
    query = """
        SELECT 
            pa.id AS id_apagon,
            s.nombre AS nombre_sector,
            pa.probabilidad_apagon,
            pa.duracion_estimada,
            ST_AsText(s.geom) AS geom,
            pa.fecha
        FROM 
            predicciones_apagones pa
        INNER JOIN 
            sectores s ON pa.sector = s.nombre
    """
    if fecha:
        query += f" WHERE pa.fecha = '{fecha}'"

    df = pd.read_sql(query, engine)
    df = df[df['geom'].notnull()]
    df['geometry'] = df['geom'].apply(lambda x: wkt.loads(x) if x else None)

    gdf = gpd.GeoDataFrame(df, geometry='geometry', crs="EPSG:4326")
    return gdf

# Función para formatear horas en un formato legible
def formatear_duracion_horas(duracion):
    duracion_timedelta = timedelta(hours=duracion)
    total_horas, remainder = divmod(duracion_timedelta.total_seconds(), 3600)
    minutos = remainder // 60
    return f"{int(total_horas)} horas y {int(minutos)} minutos"

def register_map_callbacks(dash_app):
    @dash_app.callback(
        [Output("mapa-sectores", "figure"),
         Output("dropdown-sector-map", "options"),
         Output("duracion-estimada-map", "children")],
        [Input("dropdown-sector-map", "value"),
         Input("date-picker-map", "date")]
    )
    def actualizar_mapa(sector_seleccionado, fecha_seleccionada):
        gdf = cargar_datos(fecha=fecha_seleccionada)

        duracion_estimada_texto = "Selecciona un sector para ver la duración estimada."

        if sector_seleccionado:
            gdf = gdf[gdf["nombre_sector"] == sector_seleccionado]
            
            if not gdf.empty:
                duracion_estimada = gdf['duracion_estimada'].iloc[0]
                duracion_estimada_texto = f"Duración Estimada: {formatear_duracion_horas(duracion_estimada)}"

        gdf['probabilidad_apagon'] = gdf['probabilidad_apagon'] * 100

        min_prob = gdf['probabilidad_apagon'].min() if not gdf.empty else 0
        max_prob = gdf['probabilidad_apagon'].max() if not gdf.empty else 0

        fig = px.choropleth_mapbox(
            gdf,
            geojson=gdf.geometry.__geo_interface__,
            locations=gdf.index,
            color="probabilidad_apagon",
            mapbox_style="carto-positron",
            center={"lat": 18.5, "lon": -70},
            zoom=11,
            opacity=0.6,
            color_continuous_scale=px.colors.sequential.Viridis,
            range_color=[min_prob, max_prob]
        )
        
        fig.update_layout(coloraxis_colorbar=dict(
            title="Probabilidad de Apagón (%)",
            tickvals=[min_prob, (min_prob + max_prob) / 2, max_prob],
            ticktext=[f"{min_prob:.1f}%", f"{((min_prob + max_prob) / 2):.1f}%", f"{max_prob:.1f}%"],
        ))

        fig.update_traces(marker=dict(line=dict(width=0.5, color='black')))
        fig.update_traces(hovertemplate='<br>'.join([
            'Sector: %{customdata[0]}',
            'Duración Estimada: %{customdata[1]}',
            'Fecha: %{customdata[2]}',
            'Probabilidad de Apagón: %{z:.2f}%'
        ]), customdata=gdf[['nombre_sector', 'duracion_estimada', 'fecha']].values)

        fig.update_layout(
            margin={"r": 0, "t": 30, "l": 0, "b": 0},
            title_x=0.5,
        )

        opciones_dropdown = [{"label": nombre, "value": nombre} for nombre in gdf["nombre_sector"].unique()]

        return fig, opciones_dropdown, duracion_estimada_texto

