import os
from functools import lru_cache
from pydantic import BaseConfig, Field, ValidationError

# Asegurar que la variable de entorno esté configurada
if os.getenv("CQLENG_ALLOW_SCHEMA_MANAGEMENT") is None:
    os.environ["CQLENG_ALLOW_SCHEMA_MANAGEMENT"] = "1"

class Settings(BaseConfig):
    """
    Clase de configuración para almacenar las variables de entorno
    """
    name: str = os.getenv("PROJ_NAME")
    db_client_id: str = os.getenv("ASTRA_DB_CLIENT_ID")
    db_client_secret: str = os.getenv("ASTRA_DB_CLIENT_SECRET")
    redis_url: str = os.getenv("REDIS_URL")
    class Config:
        env_file = ".env"

@lru_cache
def get_setting(): 
    """
    Obtiene y devuelve las configuraciones almacenadas en caché.
    """
    try:
        return Settings()
    except ValidationError as e:
        print(f"Error al validar las variables de entorno: {e}")
        return None

def clear_setting_cache():
    """
    Limpia la caché para forzar la recarga de la configuración.
    """
    get_setting.cache_clear()
