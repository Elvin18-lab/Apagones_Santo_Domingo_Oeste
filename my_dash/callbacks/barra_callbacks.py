import sqlite3
import pandas as pd
import plotly.express as px
from dash import Input, Output, State, html
from sklearn.linear_model import LinearRegression
from dash.dependencies import Input, Output, State

def cargar_datos():
    try:
        conexion = sqlite3.connect("C:/Users/elvin/Downloads/Practica/formulario_SDOeste/Proyecto_Final/my_dash/mi_base_de_datos.db")
        query = "SELECT * FROM encuestas"
        df = pd.read_sql(query, conexion)
        conexion.close()
        
        df['perdidas_economicas'] = pd.to_numeric(df['perdidas_economicas'], errors='coerce')
        df = df.dropna(subset=['perdidas_economicas'])

        sectores_excluir = [
            'Km. 12 Av. Independencia / Calle Isabel Aguiar',
            'Km. 13 Carretera Sánchez / Av. Independencia',
            'Km. 14'
        ]
        df = df[
            (df['tipo_usuario'].isin(['Residente', 'Comercial'])) & 
            (df['perdidas_economicas'] > 0) & 
            (~df['ubicacion'].isin(sectores_excluir))
        ]
        return df
    except Exception as e:
        print(f"Error al cargar datos: {str(e)}")
        return pd.DataFrame()

def crear_modelo_regresion(df, tipo_usuario):
    try:
        df_usuario = df[df['tipo_usuario'] == tipo_usuario]
        X = df_usuario[['frecuencia_apagones']].values
        y = df_usuario['perdidas_economicas'].values
        modelo = LinearRegression()
        modelo.fit(X, y)
        return modelo
    except Exception as e:
        print(f"Error al crear modelo de regresión: {str(e)}")
        return None

def crear_grafico_barras(df):
    try:
        resultado_agrupado = df.groupby(['ubicacion', 'tipo_usuario'])['perdidas_economicas'].sum().reset_index()
        fig = px.bar(
            resultado_agrupado,
            x='ubicacion',
            y='perdidas_economicas',
            color='tipo_usuario',
            barmode='stack',
            labels={
                'ubicacion': 'Ubicación (Sector)', 
                'perdidas_economicas': 'Pérdidas Económicas'
            },
            color_discrete_sequence=px.colors.sequential.Viridis,
        )
        fig.update_layout(
            xaxis_tickangle=-45,
            height=600,
            margin=dict(l=50, r=50, t=50, b=100)
        )
        return fig
    except Exception as e:
        print(f"Error al crear gráfico: {str(e)}")
        return {}

def extrapolar_perdidas(modelo, frecuencia):
    try:
        if modelo is None:
            return 0
        return modelo.predict([[frecuencia]])[0]
    except Exception as e:
        print(f"Error al extrapolar pérdidas: {str(e)}")
        return 0

def register_graficos_callbacks(app):
    # Cargar datos una sola vez al iniciar
    df = cargar_datos()
    
    # Crear modelos una sola vez
    modelo_residente = crear_modelo_regresion(df, 'Residente')
    modelo_comercial = crear_modelo_regresion(df, 'Comercial')
    
    # Callback para inicializar el gráfico
    @app.callback(
        Output('grafico-barras', 'figure'),
        Input('tabs', 'value')  # Asumiendo que tienes un componente tabs
    )
    def inicializar_grafico(tab_value):
        return crear_grafico_barras(df)

    # Callback para la extrapolación
    @app.callback(
        Output('output-extrapolacion', 'children'),
        Input('input-frecuencia', 'value')
    )
    def actualizar_extrapolacion(frecuencia):
        if frecuencia is None or frecuencia < 0:
            return html.Div("Por favor, ingrese una frecuencia de apagones válida (mayor o igual a 0).",
                          style={'color': 'red'})

        try:
            perdidas_residente = extrapolar_perdidas(modelo_residente, frecuencia)
            perdidas_comercial = extrapolar_perdidas(modelo_comercial, frecuencia)
            
            return [
                html.Div([
                    html.H4("Resultados de la Extrapolación:", 
                           style={'margin-top': '20px', 'margin-bottom': '15px'}),
                    html.Div([
                        html.Strong("Residencial: "),
                        f"RD$ {perdidas_residente:,.2f}"
                    ], style={'margin-bottom': '10px'}),
                    html.Div([
                        html.Strong("Comercial: "),
                        f"RD$ {perdidas_comercial:,.2f}"
                    ]),
                ], style={'background-color': '#f8f9fa', 
                         'padding': '20px', 
                         'border-radius': '5px',
                         'box-shadow': '0 2px 4px rgba(0,0,0,0.1)'})
            ]
        except Exception as e:
            return html.Div(f"Error en el cálculo: {str(e)}", 
                          style={'color': 'red'})


