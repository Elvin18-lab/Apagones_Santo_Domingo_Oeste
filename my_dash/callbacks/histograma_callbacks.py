from dash import Input, Output
import pandas as pd
import plotly.graph_objects as go
from data.database import get_connection
from cachetools import TTLCache, cached

# Configurar caché para los sectores
sector_cache = TTLCache(maxsize=100, ttl=3600)  # 3600 segundos = 1 hora

@cached(sector_cache)
def obtener_sectores():
    engine = get_connection()
    query = "SELECT DISTINCT sector FROM mediciones_sector;"
    df = pd.read_sql(query, engine)
    return [{'label': sector, 'value': sector} for sector in df['sector']]

def obtener_datos_consumo_promedio():
    engine = get_connection()
    query = """
        SELECT 
            EXTRACT(YEAR FROM fecha) AS año,
            sector,
            AVG(consumo_promedio) AS consumo_promedio
        FROM 
            mediciones_sector
        GROUP BY 
            año, sector
        ORDER BY 
            año, sector;
    """
    df = pd.read_sql(query, engine)
    return df

def register_histograma_callbacks(dash_app):
    @dash_app.callback(
        Output('histograma-sector-dropdown', 'options'),
        Input('histograma-sector-dropdown', 'value')
    )
    def actualizar_dropdown(_):
        opciones = obtener_sectores()
        return opciones

    @dash_app.callback(
        Output('histograma-consumo-grafico', 'figure'),
        Input('histograma-sector-dropdown', 'value')
    )
    def actualizar_histograma(sector_seleccionado):
        df = obtener_datos_consumo_promedio()

        if sector_seleccionado:
            df = df[df['sector'] == sector_seleccionado]

        # Calcular la línea de tendencia
        trend = df.groupby('año')['consumo_promedio'].mean().reset_index()

        # Crear el gráfico
        fig = go.Figure()

        # Añadir las barras del histograma
        fig.add_trace(go.Bar(
            x=df['año'],
            y=df['consumo_promedio'],
            name='Consumo Promedio',
            marker_color='rgba(153, 102, 255, 0.7)',
            opacity=0.75
        ))

        # Añadir la línea de tendencia
        fig.add_trace(go.Scatter(
            x=trend['año'],
            y=trend['consumo_promedio'],
            mode='lines+markers',
            name='Tendencia',
            line=dict(color='red', width=2),
            marker=dict(size=8)
        ))

        # Actualizar el layout
        fig.update_layout(
            xaxis_title='Año',
            yaxis_title='Consumo Promedio (kWh)',
            barmode='overlay',
            template='plotly_white'
        )

        return fig






