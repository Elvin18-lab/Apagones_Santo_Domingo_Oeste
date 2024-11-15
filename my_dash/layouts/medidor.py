from dash import dcc, html
import dash_bootstrap_components as dbc

def create_medidor_layout():
    return dbc.Container([
        dbc.Row([dbc.Col(html.H1("Análisis del Rendimiento: Transformadores por Sector y Año"), className="mb-4")]),
        dbc.Row([
            dbc.Col(dcc.Dropdown(
                id='year-dropdown-medidor',
                options=[], 
                value=2023,  # Asegúrate de que este año existe en tu base de datos
                placeholder="Selecciona un año"
            ), width=6),
            dbc.Col(dcc.Dropdown(
                id='sector-dropdown-medidor',
                options=[], 
                value='La Venta',  # Asegúrate de que este sector existe en tu base de datos
                placeholder="Selecciona un sector"
            ), width=6)
        ]),
        dbc.Row([dbc.Col(dcc.Graph(id='gauge-chart-medidor'), width=12)]),
    ], fluid=True)

