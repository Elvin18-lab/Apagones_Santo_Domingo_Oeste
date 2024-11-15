# mapa_layout.py

from dash import dcc, html
import dash_bootstrap_components as dbc
from datetime import datetime, timedelta

def create_map_layout():
    # Establecer la fecha predeterminada como '2024-11-06'
    fecha_predeterminada = '2024-11-06'

    return dbc.Container([
        dbc.Row([
            dbc.Col(html.H1("Alertas de Apagón: Mapa de Calor por Sector"), className="mb-4")
        ]),
        dbc.Row([
            dbc.Col(dcc.Dropdown(
                id="dropdown-sector-map", 
                placeholder="Selecciona un sector", 
                options=[], 
                clearable=True, 
                style={'width': '100%'}
            ), width=4),
            dbc.Col(dcc.DatePickerSingle(
                id='date-picker-map',
                placeholder="Fecha",
                date=fecha_predeterminada,  # Establecer fecha fija como predeterminada
                display_format='YYYY-MM-DD',
                style={'width': '100%', 'height': '40px', 'lineHeight': '40px', 'fontSize': '12px'}
            ), width=4)
        ]),
        dbc.Row([
            dbc.Col(html.Div(id="duracion-estimada-map", className="mb-2"), width=12),
            dbc.Col(dcc.Graph(id="mapa-sectores"), width=12)
        ]),
    ], fluid=True)



