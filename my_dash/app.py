import dash_bootstrap_components as dbc
from dash import Dash, dcc, html

from layouts.barra import crear_grafico_barras_layout
from layouts.mapa import create_map_layout
from layouts.medidor import create_medidor_layout
from layouts.histograma import create_histograma_layout

from callbacks.barra_callbacks import register_graficos_callbacks
from callbacks.mapa_callbacks import register_map_callbacks
from callbacks.medidor_callbacks import register_medidor_callbacks
from callbacks.histograma_callbacks import register_histograma_callbacks

def create_dash_app(requests_pathname_prefix="/dash/"):
    dash_app = Dash(
        __name__, 
        requests_pathname_prefix=requests_pathname_prefix, 
        external_stylesheets=[dbc.themes.BOOTSTRAP]
    )

    # Definir el layout principal con las tabs
    dash_app.layout = html.Div([
        dbc.Container([
            html.H1("Dashboard de Análisis de Apagones en Santo Domingo Oeste",
                   className="text-center my-4"),
            
            dcc.Tabs(
                id='tabs',
                value='tab-mapa',  # Tab inicial
                children=[
                    dcc.Tab(
                        label='Mapa',
                        value='tab-mapa',
                        children=[create_map_layout()]
                    ),
                    dcc.Tab(
                        label='Medidor',
                        value='tab-medidor',
                        children=[create_medidor_layout()]
                    ),
                    dcc.Tab(
                        label='Histograma',
                        value='tab-histograma',
                        children=[create_histograma_layout()]
                    ),
                    dcc.Tab(
                        label='Gráfico de Barras',
                        value='tab-barras',
                        children=[crear_grafico_barras_layout()]
                    ),
                ],
                className="mb-4"
            )
        ], fluid=True)
    ])

    # Registrar todos los callbacks
    register_graficos_callbacks(dash_app)
    register_map_callbacks(dash_app)
    register_medidor_callbacks(dash_app)
    register_histograma_callbacks(dash_app)
    
    return dash_app

if __name__ == '__main__':
    app = create_dash_app()
    app.run_server(debug=True)