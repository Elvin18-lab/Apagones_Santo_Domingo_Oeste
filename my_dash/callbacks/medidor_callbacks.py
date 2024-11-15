from dash import Input, Output
import pandas as pd
import plotly.graph_objects as go
from data.database import get_connection
from cachetools import TTLCache, cached

# Configurar caché para años y sectores
year_cache = TTLCache(maxsize=100, ttl=3600)  # 1 hora
sector_cache = TTLCache(maxsize=100, ttl=3600)  # 1 hora

@cached(year_cache)
def obtener_anios():
    engine = get_connection()
    query_years = "SELECT DISTINCT EXTRACT(YEAR FROM fecha) AS year FROM mediciones_sector ORDER BY year;"
    years_df = pd.read_sql(query_years, engine)
    return [{'label': int(year), 'value': int(year)} for year in years_df['year'].tolist()]

@cached(sector_cache)
def obtener_sectores(selected_year):
    engine = get_connection()
    query_sectors = f"""
        SELECT DISTINCT ms.sector 
        FROM mediciones_sector ms 
        WHERE EXTRACT(YEAR FROM ms.fecha) = {selected_year};
    """
    sectors_df = pd.read_sql(query_sectors, engine)
    return [{'label': sector, 'value': sector} for sector in sectors_df['sector'].tolist()]

def register_medidor_callbacks(dash_app):
    @dash_app.callback(
        [Output('year-dropdown-medidor', 'options'),  # ID actualizado
         Output('sector-dropdown-medidor', 'options')],  # ID actualizado
        Input('year-dropdown-medidor', 'value')  # ID actualizado
    )
    def update_year_options(selected_year):
        year_options = obtener_anios()
        
        # Cargar sectores solo si hay un año seleccionado
        if selected_year:
            sector_options = obtener_sectores(selected_year)
        else:
            sector_options = []  # Si no hay año seleccionado, opciones de sectores vacías

        return year_options, sector_options

    @dash_app.callback(
        Output('gauge-chart-medidor', 'figure'),  # ID actualizado
        Input('year-dropdown-medidor', 'value'),  # ID actualizado
        Input('sector-dropdown-medidor', 'value')  # ID actualizado
    )
    def update_gauge_chart(selected_year, selected_sector):
        if selected_year and selected_sector:
            engine = get_connection()
            query = f"""
                SELECT 
                    ms.estado_transformadores,
                    COUNT(*) AS cantidad
                FROM 
                    mediciones_sector ms
                WHERE 
                    EXTRACT(YEAR FROM ms.fecha) = {selected_year} AND ms.sector = '{selected_sector}'
                GROUP BY 
                    ms.estado_transformadores;
            """
            
            df = pd.read_sql(query, engine)

            if df.empty:
                return go.Figure()

            estado_mapping = {
                'Excelente': 100,
                'Bueno': 75,
                'Regular': 50,
                'Deficiente': 25
            }

            estado_max = df.loc[df['cantidad'].idxmax()]
            estado = estado_max['estado_transformadores']
            cantidad = estado_max['cantidad']
            valor = estado_mapping.get(estado, 0)

            fig = go.Figure()
            fig.add_trace(go.Indicator(
                mode="gauge",
                value=valor,
                title={'text': f"<b>Estado de Transformadores:</b> {estado} en {selected_sector} ({selected_year})", 'font': {'size': 20}},
                gauge={
                    'axis': {'range': [0, 100], 'tickvals': [25, 50, 75, 100]},
                    'bar': {'color': "orange"},
                    'steps': [
                        {'range': [0, 25], 'color': "red"},
                        {'range': [25, 50], 'color': "yellow"},
                        {'range': [50, 75], 'color': "lightgreen"},
                        {'range': [75, 100], 'color': "green"},
                    ],
                    'threshold': {
                        'line': {'color': "black", 'width': 4},
                        'thickness': 0.75,
                        'value': valor
                    }
                }
            ))

            fig.update_layout(paper_bgcolor="white", font=dict(color="black"))

            return fig

        return go.Figure()
