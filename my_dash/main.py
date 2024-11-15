from fastapi import FastAPI, Request, HTTPException, Depends, Query
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from pydantic import BaseModel
from starlette.middleware.wsgi import WSGIMiddleware
from starlette.responses import RedirectResponse

# Configuración de la conexión a la base de datos
from clave import DATABASE

# importar el archivo app.py que maneja todo los graficos 
from app import create_dash_app

# Crear la conexión a PostgreSQL
engine = create_engine(DATABASE)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Inicializar la aplicación FastAPI
app = FastAPI(
    title="API Formulario Apagones",
    description="API para gestionar formularios de investigación sobre apagones eléctricos"
)
# Configura la aplicación Dash
dash_app = create_dash_app(requests_pathname_prefix="/dash/")
app.mount("/dash", WSGIMiddleware(dash_app.server))

# Montar el directorio de archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configuración de las plantillas Jinja2
templates = Jinja2Templates(directory="templates")

# Ruta de bienvenida
@app.get('/')
async def bienvenido(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Ruta del formulario
@app.get("/formulario")
async def mostrar_formulario(request: Request):
    return templates.TemplateResponse("formulario.html", {"request": request})


"""
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/enviar/")
async def procesar_formulario(
    datos: FormularioBase,
    request: Request,
    local_kw: str = Query(..., description="Parámetro requerido"),
    db: Session = Depends(get_db)
):
    try:
        # Crear nuevo registro directamente
        nuevo_formulario = Formulario(
        # Información personal y del encuestado
        nombre=datos.nombre.title(),
        fecha_nacimiento=datos.fecha_nacimiento,
        sexo=datos.sexo,
        fecha_encuesta=datos.fecha_encuesta,
        ubicacion=datos.ubicacion,
        tipo_usuario=datos.tipo_usuario,
        tiempo_residencia=datos.tiempo_residencia,
        consumo=datos.consumo,
        comentarios_adicionales=datos.comentarios_adicionales,

        # Frecuencia y duración de los apagones
        frecuencia_apagones=datos.frecuencia_apagones,
        duracion_apagones=datos.duracion_apagones,
        horario_apagones=datos.horario_apagones,
        comentarios_frecuencia=datos.comentarios_frecuencia,
        epoca_apagones=datos.epoca_apagones,
        condiciones_climaticas=datos.condiciones_climaticas,
        relacion_apagones=datos.relacion_apagones,

        # Facturación y consumo
        facturacion=datos.facturacion,
        cobro_apagones=datos.cobro_apagones,
        diferencias_facturacion=datos.diferencias_facturacion,
        compensaciones_apagones=datos.compensaciones_apagones,
        metodo_pago=datos.metodo_pago,
        registro_horas=datos.registro_horas,
        comentarios_facturacion=datos.comentarios_facturacion,

        # Impacto y consecuencias
        impacto_economico=datos.impacto_economico,
        perdidas_economicas=datos.perdidas_economicas,
        sistema_respaldo=datos.sistema_respaldo,
        comentarios_impacto=datos.comentarios_impacto,

        # Comunicación y respuesta
        notificaciones_apagones=datos.notificaciones_apagones,
        medio_notificaciones=datos.medio_notificaciones,
        tiempo_respuesta=datos.tiempo_respuesta,
        comentarios_comunicacion=datos.comentarios_comunicacion,

        # Datos técnicos
        num_transformador=datos.num_transformador,
        estado_infraestructura=datos.estado_infraestructura,
        observaciones_tecnicas=datos.observaciones_tecnicas,

        # Sistema predictivo de apagones
        utilidad_sistema=datos.utilidad_sistema,
        tiempo_alerta=datos.tiempo_alerta,
        acciones_alerta=datos.acciones_alerta,
        medio_alerta=datos.medio_alerta,
        info_alerta=datos.info_alerta,
        funcionalidades=datos.funcionalidades,
        compartir_datos=datos.compartir_datos,
        mejora_planificacion=datos.mejora_planificacion,
        beneficios=datos.beneficios,
        confiabilidad_sistema=datos.confiabilidad_sistema,
        participar_piloto=datos.participar_piloto,
        interes_reportar=datos.interes_reportar
    )
        
        # Guardar en la base de datos
        db.add(nuevo_formulario)
        db.commit()
        db.refresh(nuevo_formulario)

        return {
            "status": "success",
            "message": "Datos guardados correctamente",
            "data": datos.model_dump()
        }

    except Exception as e:
        db.rollback()  # Revertir cambios en caso de error

        return {
            "status": "error",
            "message": str(e)
        }

# Ruta para la página de validación
@app.get("/validacion")
async def validacion(request: Request):
    return templates.TemplateResponse("validacion.html", {"request": request})
"""

# ruta para ir al dashboard 
@app.get("/dashboard")
async def dashboard():
    return RedirectResponse(url="/dash/")






""" Ruta para recibir los datos del formulario
@app.post("/enviar/")
async def enviar_formulario(formulario: FormularioBase, request: Request, db: Session = Depends(SessionLocal)):
    # Aquí puedes agregar la lógica para insertar los datos en la base de datos
    new_formulario = Formulario(
        # Asigna los valores del formulario a los campos de la tabla
        nombre_completo=formulario.nombre,
        fecha_nacimiento=formulario.fecha_nacimiento,
        sexo=formulario.sexo,
        fecha_encuesta=formulario.fecha_encuesta,
        ubicacion=formulario.ubicacion,
        tipo_usuario=formulario.tipo_usuario,
        tiempo_residencia=formulario.tiempo_residencia,
        consumo=formulario.consumo,
        comentarios_adicionales=formulario.comentarios_adicionales,
        frecuencia_apagones=formulario.frecuencia_apagones,
        duracion_apagones=formulario.duracion_apagones,
        horario_apagones=formulario.horario_apagones,
        comentarios_frecuencia=formulario.comentarios_facturacion,
        epoca_apagones=formulario.epoca_apagones, 
        condiciones_climaticas=formulario.condiciones_climaticas,
        relacion_apagones=formulario.relacion_apagones, 
        otro_factor=formulario.otro_factor,
        facturacion=formulario.facturacion, 
        cobro_apagones=formulario.cobro_apagones, 
        diferencias_facturacion=formulario.diferencias_facturacion, 
        compensaciones_apagones=formulario. compensaciones_apagones, 
        metodo_pago=formulario.metodo_pago, 
        metodo_pago_otro=formulario.metodo_pago_otro, 
        registros=formulario.registros, 
        comentarios_facturacion=formulario.comentarios_facturacion,
        impacto_economico=formulario.impacto_economico, 
        perdidas_economicas=formulario.perdidas_economicas,
        sistema_respaldo=formulario.sistema_respaldo, 
        sistema_respaldo_otro=formulario.sistema_respaldo_otro,
        comentarios_impacto=formulario.comentarios_impacto,   
        notificaciones_apagones=formulario.notificaciones_apagones,
        medio_notificaciones=formulario.medio_notificaciones, 
        tiempo_respuesta=formulario.tiempo_respuesta, 
        comentarios_comunicacion=formulario.comentarios_comunicacion,
        num_transformador=formulario.num_transformador, 
        estado_infraestructura=formulario.estado_infraestructura,
        observaciones_tecnicas=formulario.observaciones_tecnicas,
        utilidad_sistema=formulario.utilidad_sistema, 
        tiempo_alerta=formulario.tiempo_alerta, 
        acciones_alerta=formulario.acciones_alerta, 
        medio_alerta=formulario.medio_alerta, 
        info_alerta=formulario.info_alerta,
        funcionalidades=formulario.funcionalidades, 
        compartir_datos=formulario.compartir_datos, 
        mejora_planificacion=formulario.mejora_planificacion,
        beneficios=formulario.beneficios, 
        confiabilidad_sistema=formulario.confiabilidad_sistema,
        participar_piloto=formulario.participar_piloto,
        interes_reportar=formulario.interes_reportar, 
    )
    
    try:
        db.add(new_formulario)
        db.commit()
        db.refresh(new_formulario)  # Esto actualiza el objeto con la información del DB (como el ID)
        return templates.TemplateResponse("validacion.html", {"request": request})
    except Exception as e:
        db.rollback()  # Deshacer los cambios en caso de error
        raise HTTPException(status_code=500, detail=str(e))"""






