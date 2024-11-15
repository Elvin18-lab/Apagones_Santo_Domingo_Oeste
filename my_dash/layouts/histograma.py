from dash import dcc, html
import dash_bootstrap_components as dbc

def create_histograma_layout():
    return html.Div([
        dbc.Row([
            dbc.Col(html.H1("Patrones de Consumo Promedio por Sector a lo Largo del Tiempo", className="text-center"), className="mb-4")
        ]),
        dbc.Row([
            dbc.Col(dcc.Dropdown(id='histograma-sector-dropdown', options=[], value=None, placeholder="Selecciona un sector"), width=12)
        ]),
        dbc.Row([
            dbc.Col(dcc.Graph(id='histograma-consumo-grafico'), width=12)  # ID actualizado para el gráfico
        ])
    ])

