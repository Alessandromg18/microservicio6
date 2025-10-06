# Modelos para las consultas
from pydantic import BaseModel, Field
from typing import Optional

class EchoRequest(BaseModel):
    """Modelo para el endpoint de prueba echo"""
    message: str = Field(
        ...,
        description="Mensaje que será devuelto por el endpoint",
        example="Hello World",
        min_length=1,
        max_length=500
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "¡Hola desde ScrapeTok!"
            }
        }

class SQLQueryRequest(BaseModel):
    """Modelo para consultas SQL personalizadas (si se implementa en el futuro)"""
    query: str = Field(
        ...,
        description="Consulta SQL a ejecutar en Athena",
        example="SELECT * FROM users LIMIT 10"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "SELECT userId, COUNT(*) as total FROM scraped_acount GROUP BY userId"
            }
        }

class QueryParams(BaseModel):
    """Parámetros comunes para consultas"""
    limit: Optional[int] = Field(
        default=10,
        ge=1,
        le=1000,
        description="Número máximo de resultados a retornar"
    )
    offset: Optional[int] = Field(
        default=0,
        ge=0,
        description="Número de resultados a saltar (para paginación)"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "limit": 20,
                "offset": 0
            }
        }