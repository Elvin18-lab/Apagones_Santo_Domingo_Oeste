import dash_bootstrap_components as dbc
from dash import dcc, html

def crear_grafico_barras_layout():
    return dbc.Container([
        # Título principal
        dbc.Row([
            dbc.Col([
                html.H1("Análisis de Pérdidas Económicas por Apagones",
                        className="text-center mb-4")
            ])
        ]),
        
        # Bloque del estimador de pérdidas
        dbc.Row([
            dbc.Col([
                html.H2("Estimador de Pérdidas", className="mt-4 mb-3"),  # Margen superior
                
                # Formulario de entrada
                dbc.Form([
                    dbc.Label("Frecuencia de apagones mensual:",
                              className="mb-2", style={'font-weight': 'bold'}),
                    dbc.Input(
                        id='input-frecuencia',
                        type='number',
                        placeholder="Ingrese un número",
                        min=0,
                        step=1,
                        className="mb-3",
                        style={'max-width': '300px'}
                    ),
                ], style={'margin-bottom': '30px'}),  # Espacio debajo del formulario
                
                # Contenedor para los resultados
                html.Div(
                    id='output-extrapolacion',
                    className="mt-3"
                )
            ], 
            md=6,  # Usar la mitad del ancho en pantallas medianas
            className="mx-auto"  # Centrar el contenedor
            )
        ], className="mt-4"),
        
        # Gráfico de barras apiladas
        dbc.Row([
            dbc.Col([
                dcc.Graph(
                    id='grafico-barras',
                    style={'height': '390px', 'margin-bottom': '20px'}  # Altura fija y margen inferior
                )
            ])
        ])
    ], fluid=True)
