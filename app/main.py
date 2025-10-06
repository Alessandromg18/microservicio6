from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from app.athena_client import run_athena_query
from app.models import SQLQueryRequest, EchoRequest, QueryParams
from typing import Dict, Any

# Metadata para la documentación de la API
tags_metadata = [
    {
        "name": "Health",
        "description": "Endpoints para verificar el estado del servicio",
    },
    {
        "name": "Analytics",
        "description": "Endpoints de análisis y métricas de usuarios y administradores. Ejecuta consultas sobre AWS Athena.",
    },
]

app = FastAPI(
    title="ScrapeTok Analytics API - Microservicio 6",
    description="""
    ## API de Analytics para ScrapeTok
    
    Esta API proporciona endpoints de análisis avanzado sobre datos almacenados en AWS Athena.
    
    ### Características principales:
    * 🔍 **Análisis de usuarios**: Obtén estadísticas sobre usuarios con más cuentas scrapeadas
    * 👨‍💼 **Métricas de admins**: Consulta información sobre administradores, preguntas respondidas y vistas
    * 🧪 **Health check**: Verifica el estado del servicio
    
    ### Tecnologías:
    * FastAPI
    * AWS Athena
    * Boto3
    
    ---
    **Documentación automática generada por FastAPI**
    """,
    version="1.0.0",
    openapi_tags=tags_metadata,
    contact={
        "name": "ScrapeTok Team",
        "email": "support@scrapetok.com",
    },
    license_info={
        "name": "MIT",
    },
)

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",  # React default
        "http://localhost:8080",  # Vue default
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos los métodos (GET, POST, etc.)
    allow_headers=["*"],  # Permite todos los headers
)

# 🧪 Endpoint Echo Test
@app.post(
    "/echo",
    tags=["Health"],
    summary="Test de eco",
    description="Endpoint simple para verificar que el servicio está funcionando correctamente",
    response_description="Devuelve el mensaje enviado",
    responses={
        200: {
            "description": "Mensaje de eco exitoso",
            "content": {
                "application/json": {
                    "example": {"echo": "Hello World"}
                }
            }
        }
    }
)
async def echo_test(request: EchoRequest) -> Dict[str, str]:
    """
    Endpoint de prueba que devuelve el mismo mensaje que recibe.
    
    - **message**: El mensaje que deseas que se devuelva
    """
    return {"echo": request.message}

# 🧑‍💻 Endpoint para "Usuarios con más cuentas scrapeadas y cantidad de filtros activos"
@app.get(
    "/users/most_scraped",
    tags=["Analytics"],
    summary="Usuarios con más cuentas scrapeadas",
    description="Obtiene los usuarios con mayor cantidad de cuentas scrapeadas y sus filtros activos",
    response_description="Lista de usuarios ordenados por cantidad de cuentas scrapeadas",
    responses={
        200: {
            "description": "Consulta exitosa",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "data": [
                            {
                                "userId": "user123",
                                "accounts_scraped": 45,
                                "active_filters": 12
                            },
                            {
                                "userId": "user456",
                                "accounts_scraped": 38,
                                "active_filters": 8
                            }
                        ]
                    }
                }
            }
        },
        500: {
            "description": "Error en la consulta a Athena",
            "content": {
                "application/json": {
                    "example": {"detail": "Error al ejecutar la consulta"}
                }
            }
        }
    }
)
async def get_users_most_scraped(
    limit: int = Query(
        default=10,
        ge=1,
        le=1000,
        description="Número máximo de usuarios a retornar",
        example=10
    )
) -> Dict[str, Any]:
    """
    Consulta los usuarios con más cuentas scrapeadas en la plataforma.
    
    Esta consulta ejecuta una query en AWS Athena que:
    - Cuenta las cuentas scrapeadas por usuario
    - Ordena los resultados por cantidad de cuentas scrapeadas (descendente)
    
    **Parámetros:**
    - **limit**: Cantidad máxima de resultados (1-1000, default: 10)
    
    **Retorna:**
    - Lista de usuarios con sus métricas de scraping
    """
    query = f"""
    SELECT
      user_id,
      username,
      COUNT(accountName) AS accounts_scraped
    FROM usuarios_cuentas_raspadas
    GROUP BY user_id, username
    ORDER BY accounts_scraped DESC
    LIMIT {limit}
    """
    try:
        result = run_athena_query(query)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 🧑‍💻 Endpoint para "Admins con más interacciones en publicaciones"
@app.get(
    "/admins/questions_and_views",
    tags=["Analytics"],
    summary="Métricas de administradores en TikTok",
    description="Obtiene estadísticas de administradores incluyendo publicaciones y métricas de engagement",
    response_description="Lista de administradores con sus métricas",
    responses={
        200: {
            "description": "Consulta exitosa",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "data": [
                            {
                                "usernameTiktokAccount": "admin_user1",
                                "total_posts": 45,
                                "total_views": 125000,
                                "total_likes": 12500,
                                "avg_views": 2777
                            }
                        ]
                    }
                }
            }
        },
        500: {
            "description": "Error en la consulta a Athena",
            "content": {
                "application/json": {
                    "example": {"detail": "Error al ejecutar la consulta"}
                }
            }
        }
    }
)
async def get_admins_with_questions_and_views(
    limit: int = Query(
        default=10,
        ge=1,
        le=1000,
        description="Número máximo de administradores a retornar",
        example=10
    )
) -> Dict[str, Any]:
    """
    Consulta métricas de administradores basadas en sus publicaciones en TikTok.
    
    Esta consulta ejecuta una query en AWS Athena que:
    - Agrupa publicaciones por cuenta de administrador
    - Calcula total de vistas, likes y comentarios
    - Calcula promedio de vistas por publicación
    - Ordena por total de vistas (descendente)
    
    **Parámetros:**
    - **limit**: Cantidad máxima de resultados (1-1000, default: 10)
    
    **Retorna:**
    - Lista de administradores con sus métricas de engagement
    """
    query = f"""
    SELECT
      usernameTiktokAccount,
      COUNT(postid) AS total_posts,
      SUM(views) AS total_views,
      SUM(likes) AS total_likes,
      SUM(comments) AS total_comments,
      AVG(views) AS avg_views
    FROM publicaciones_admin_interacciones
    GROUP BY usernameTiktokAccount
    ORDER BY total_views DESC
    LIMIT {limit}
    """
    try:
        result = run_athena_query(query)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# � Endpoint adicional: Listar usuarios básicos
@app.get(
    "/users/list",
    tags=["Analytics"],
    summary="Listar usuarios registrados",
    description="Obtiene la lista de usuarios registrados en el sistema",
    response_description="Lista de usuarios"
)
async def get_users_list(
    limit: int = Query(
        default=10,
        ge=1,
        le=1000,
        description="Número máximo de usuarios a retornar",
        example=10
    )
) -> Dict[str, Any]:
    """
    Consulta los usuarios registrados en el sistema.
    
    **Parámetros:**
    - **limit**: Cantidad máxima de resultados (1-1000, default: 10)
    
    **Retorna:**
    - Lista de usuarios con su información básica
    """
    query = f"""
    SELECT
      id,
      firstname,
      lastname,
      username,
      creation_date
    FROM usuarios_basicos
    ORDER BY creation_date DESC
    LIMIT {limit}
    """
    try:
        result = run_athena_query(query)
        return {"success": True, "data": result, "count": len(result)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 📊 Endpoint adicional: Top publicaciones
@app.get(
    "/posts/top",
    tags=["Analytics"],
    summary="Top publicaciones por vistas",
    description="Obtiene las publicaciones con más vistas",
    response_description="Lista de publicaciones ordenadas por vistas"
)
async def get_top_posts(
    limit: int = Query(
        default=10,
        ge=1,
        le=100,
        description="Número máximo de publicaciones a retornar",
        example=10
    )
) -> Dict[str, Any]:
    """
    Consulta las publicaciones con más vistas.
    
    **Parámetros:**
    - **limit**: Cantidad máxima de resultados (1-100, default: 10)
    
    **Retorna:**
    - Lista de publicaciones ordenadas por número de vistas
    """
    query = f"""
    SELECT
      postid,
      usernameTiktokAccount,
      views,
      likes,
      comments
    FROM publicaciones_admin_interacciones
    ORDER BY views DESC
    LIMIT {limit}
    """
    try:
        result = run_athena_query(query)
        return {"success": True, "data": result, "count": len(result)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# �🔍 Endpoints de Exploración (para debugging)
@app.get(
    "/debug/tables",
    tags=["Analytics"],
    summary="Listar todas las tablas en la base de datos",
    description="Obtiene la lista de todas las tablas disponibles en Athena",
)
async def list_tables() -> Dict[str, Any]:
    """
    Lista todas las tablas en la base de datos scrapetok.
    Útil para verificar qué tablas están disponibles.
    """
    query = "SHOW TABLES IN scrapetok"
    try:
        result = run_athena_query(query)
        # Intentar diferentes claves posibles que Athena podría usar
        tables = []
        for row in result:
            # Probar diferentes claves
            table_name = (row.get('tab_name') or 
                         row.get('tablename') or 
                         row.get('table_name') or
                         row.get('name') or
                         list(row.values())[0] if row.values() else '')
            if table_name:
                tables.append(table_name)
        
        return {
            "success": True, 
            "tables": tables, 
            "count": len(tables),
            "raw_data": result  # Para debugging
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get(
    "/debug/describe/{table_name}",
    tags=["Analytics"],
    summary="Describir la estructura de una tabla",
    description="Obtiene las columnas y tipos de datos de una tabla específica",
)
async def describe_table(table_name: str) -> Dict[str, Any]:
    """
    Describe la estructura de una tabla específica.
    
    **Parámetros:**
    - **table_name**: Nombre de la tabla a describir
    """
    query = f"DESCRIBE scrapetok.{table_name}"
    try:
        result = run_athena_query(query)
        return {"success": True, "table": table_name, "columns": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post(
    "/debug/query",
    tags=["Analytics"],
    summary="Ejecutar consulta SQL personalizada",
    description="Ejecuta una consulta SQL personalizada en Athena (¡úsalo con cuidado!)",
)
async def execute_custom_query(request: SQLQueryRequest) -> Dict[str, Any]:
    """
    Ejecuta una consulta SQL personalizada en Athena.
    
    **¡ADVERTENCIA!** Este endpoint es para debugging. En producción debería estar protegido.
    
    **Parámetros:**
    - **query**: Consulta SQL a ejecutar
    """
    try:
        result = run_athena_query(request.query)
        return {"success": True, "data": result, "row_count": len(result)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))