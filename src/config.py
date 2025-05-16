import os
from dotenv import load_dotenv
import sys

def find_project_root(marker_file='.env'):
    """busca la raiz del proyecto encontrando el .env"""
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
    if load_dotenv(dotenv_path=dotenv_path):
        pass
    else:
        print("no se pudo crear el .env")
else:
    if not load_dotenv():
        print("no existe el .env")
        pass


DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")

def check_db_config() -> bool:
    """
    revisa las variables del .env para asegurarse que no falte ninguna
    """
    essential_vars = {
        "DB_NAME": DB_NAME,
        "DB_USER": DB_USER,
        "DB_PASS": DB_PASS,
        "DB_HOST": DB_HOST,
        "DB_PORT": DB_PORT
    }
    missing_vars = [name for name, value in essential_vars.items() if value is None]

    if missing_vars:
        print("faltan variables para conectarse a la base de datos, revisar .env")
        return False
    return True
