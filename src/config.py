# ADVERTENCIA:
# Este archivo espera que el .env contenga SOLO dos configuraciones de base de datos:
# - DB_TRANS_*  (para la base transaccional/relacional)
# - DB_STAR_*   (para la base dimensional/estrella)
# No uses variables antiguas como DB_NAME, DB_USER, DB_ORIGEN_*, DB_DESTINO_*, etc.

import os
from dotenv import load_dotenv

def find_project_root(marker_file='.env'):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    while True:
        if os.path.exists(os.path.join(current_dir, marker_file)):
            return current_dir
        parent_dir = os.path.dirname(current_dir)
        if parent_dir == current_dir:
            return None
        current_dir = parent_dir

project_root = find_project_root('.env')
if project_root:
    dotenv_path = os.path.join(project_root, '.env')
    load_dotenv(dotenv_path=dotenv_path)
else:
    load_dotenv()

# Base de datos transaccional (relacional)
DB_TRANS_NAME = os.getenv("DB_TRANS_NAME")
DB_TRANS_USER = os.getenv("DB_TRANS_USER")
DB_TRANS_PASS = os.getenv("DB_TRANS_PASS")
DB_TRANS_HOST = os.getenv("DB_TRANS_HOST")
DB_TRANS_PORT = os.getenv("DB_TRANS_PORT")

# Base de datos dimensional (estrella)
DB_STAR_NAME = os.getenv("DB_STAR_NAME")
DB_STAR_USER = os.getenv("DB_STAR_USER")
DB_STAR_PASS = os.getenv("DB_STAR_PASS")
DB_STAR_HOST = os.getenv("DB_STAR_HOST")
DB_STAR_PORT = os.getenv("DB_STAR_PORT")

def check_db_config(tipo="estrella"):
    """
    Verifica que la configuración de la base de datos esté completa.
    Por defecto revisa la base dimensional (estrella).
    """
    if tipo == "transaccional":
        required = [DB_TRANS_NAME, DB_TRANS_USER, DB_TRANS_PASS, DB_TRANS_HOST, DB_TRANS_PORT]
    else:
        required = [DB_STAR_NAME, DB_STAR_USER, DB_STAR_PASS, DB_STAR_HOST, DB_STAR_PORT]
    return all(required)

def get_db_config(tipo="estrella"):
    """
    Devuelve la configuración de conexión para la base solicitada.
    tipo: 'transaccional' o 'estrella'
    """
    if tipo == "transaccional":
        return {
            'host': DB_TRANS_HOST,
            'port': DB_TRANS_PORT,
            'user': DB_TRANS_USER,
            'password': DB_TRANS_PASS,
            'database': DB_TRANS_NAME
        }
    elif tipo == "estrella":
        return {
            'host': DB_STAR_HOST,
            'port': DB_STAR_PORT,
            'user': DB_STAR_USER,
            'password': DB_STAR_PASS,
            'database': DB_STAR_NAME
        }
    else:
        raise ValueError(f"Tipo de configuración inválido: {tipo}")
