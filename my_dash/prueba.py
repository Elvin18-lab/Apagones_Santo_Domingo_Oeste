import sqlite3
import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output
from sklearn.linear_model import LinearRegression

# Inicializar la aplicación Dash
app = Dash(__name__)

# Cargar datos y aplicar filtros iniciales
def cargar_datos():
    conexion = sqlite3.connect("C:/Users/elvin/Downloads/Practica/formulario_SDOeste/Proyecto_Final/my_dash/mi_base_de_datos.db")
    query = "SELECT * FROM encuestas"
    df = pd.read_sql(query, conexion)
    conexion.close()
    
    # Asegurarnos de que la columna `perdidas_economicas` es numérica, reemplazando errores por NaN
    df['perdidas_economicas'] = pd.to_numeric(df['perdidas_economicas'], errors='coerce')
    
    # Eliminar filas con valores NaN en `perdidas_economicas`
    df = df.dropna(subset=['perdidas_economicas'])

    # Filtrar datos por tipo de usuario y excluir sectores específicos
    sectores_excluir = [
        'Km. 12 Av. Independencia / Calle Isabel Aguiar',
        'Km. 13 Carretera Sánchez / Av. Independencia',
        'Km. 14'
    ]
    df = df[(df['tipo_usuario'].isin(['Residente', 'Comercial'])) & 
            (df['perdidas_economicas'] > 0) & 
            (~df['ubicacion'].isin(sectores_excluir))]
    return df

# Crear modelo de regresión lineal
def crear_modelo_regresion(df, tipo_usuario):
    df_usuario = df[df['tipo_usuario'] == tipo_usuario]
    modelo = LinearRegression()
    modelo.fit(df_usuario[['frecuencia_apagones']], df_usuario['perdidas_economicas'])
    return modelo

# Cargar los datos y crear modelos de regresión
df = cargar_datos()
modelo_residente = crear_modelo_regresion(df, 'Residente')
modelo_comercial = crear_modelo_regresion(df, 'Comercial')

# Crear el gráfico de barras apiladas inicial con Plotly
def crear_grafico_barras(df):
    # Agrupar y sumar pérdidas económicas por sector y tipo de usuario
    resultado_agrupado = df.groupby(['ubicacion', 'tipo_usuario'])['perdidas_economicas'].sum().reset_index()

    # Crear gráfico de barras apiladas
    fig = px.bar(
        resultado_agrupado,
        x='ubicacion',
        y='perdidas_economicas',
        color='tipo_usuario',
        barmode='stack',
        labels={'ubicacion': 'Ubicación (Sector)', 'perdidas_economicas': 'Pérdidas Económicas'},
        color_discrete_sequence=px.colors.sequential.Viridis
    )
    fig.update_layout(xaxis_tickangle=-45)
    return fig

# Crear el layout de la aplicación Dash
app.layout = html.Div([
    html.H1("Análisis de Pérdidas Económicas por Apagones", style={'text-align': 'center'}),
    
    # Gráfico de barras apiladas
    dcc.Graph(id='grafico-barras', figure=crear_grafico_barras(df)),
    
    # Input y output para el modelo de regresión lineal
    html.Label("Ingrese la frecuencia de apagones para estimar las pérdidas económicas", style={'font-size': '18px'}),
    dcc.Input(
        id='input-frecuencia', 
        type='number', 
        placeholder="Frecuencia de apagones", 
        min=0,
        style={'width': '60%', 'padding': '10px', 'font-size': '16px', 'margin-bottom': '15px'}
    ),
    html.Div(id='output-extrapolacion', style={'font-size': '16px', 'margin-top': '20px', 'line-height': '1.8'})
])

# Función para extrapolar pérdidas económicas
def extrapolar_perdidas(modelo, frecuencia):
    return modelo.predict(pd.DataFrame([[frecuencia]], columns=['frecuencia_apagones']))[0]

# Callback para actualizar la extrapolación de pérdidas al cambiar la frecuencia
@app.callback(
    Output('output-extrapolacion', 'children'),
    [Input('input-frecuencia', 'value')]
)
def actualizar_extrapolacion(frecuencia):
    if frecuencia is None:
        return "Ingrese una frecuencia de apagones para ver la extrapolación de pérdidas económicas."

    # Extrapolar pérdidas para los modelos de residente y comercial
    perdidas_residente = extrapolar_perdidas(modelo_residente, frecuencia)
    perdidas_comercial = extrapolar_perdidas(modelo_comercial, frecuencia)
    
    # Crear mensaje de resultados en líneas separadas usando múltiples elementos html.Div
    mensaje_extrapolacion = [
        html.Div(f"Pérdidas económicas extrapoladas para un residente con frecuencia de apagones {frecuencia}: {perdidas_residente:,.2f}"),
        html.Div(f"Pérdidas económicas extrapoladas para un comercial con frecuencia de apagones {frecuencia}: {perdidas_comercial:,.2f}")
    ]

    return mensaje_extrapolacion

# Ejecutar la aplicación
if __name__ == "__main__":
    app.run_server(debug=True)
