import dash
from dash import html, dcc, dash_table
from datetime import datetime

def create_prediccion_layout():
    return html.Div([
        html.H1("Predicción de Apagones"),
        html.Div("Ingrese la fecha para predecir apagones:"),
        
        dcc.DatePickerSingle(
            id='input-fecha',
            date=datetime.now().date(),  # Valor por defecto de la fecha
            display_format='YYYY-MM-DD'  # Formato de visualización
        ),
        
        dash_table.DataTable(
            id='table-predicciones',
            columns=[
                {'name': 'Sector', 'id': 'sector'},
                {'name': 'Probabilidad de Apagón', 'id': 'probabilidad_apagon'},
                {'name': 'Duración Estimada', 'id': 'duracion_estimada'},
                {'name': 'Fecha', 'id': 'fecha'}
            ],
            data=[],
            style_table={'overflowX': 'auto'},
            style_cell={'textAlign': 'left'},
        )
    ])


