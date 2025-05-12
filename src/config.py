import os
from dotenv import load_dotenv
import sys

def find_project_root(marker_file='.env'):
    """Busca la raíz del proyecto subiendo directorios hasta encontrar un archivo marcador."""
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
    try:
        load_dotenv(dotenv_path=dotenv_path)
        print(f"Archivo .env cargado desde: {dotenv_path}")
    except Exception as e:
        print(f"Error al cargar el archivo .env desde {dotenv_path}: {e}")
else:
    load_dotenv()

DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")

def check_db_config() -> bool:
    """
    Verifica que las variables de entorno esenciales para la BD estén definidas.
    Devuelve True si la configuración es válida, False en caso contrario.
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
        print("\n--- ERROR CRÍTICO DE CONFIGURACIÓN ---")
        print("Faltan las siguientes variables de entorno esenciales para la base de datos:")
        for var_name in missing_vars:
            print(f"  - {var_name}")
        print("\nAsegúrate de que estén definidas en el archivo .env en la raíz del proyecto")
        print(f"(Se buscó .env en: {project_root or 'No encontrado'})")
        print("o que estén definidas como variables de entorno del sistema.")
        print("----------------------------------------")
        return False
    else:
        print("\nConfiguración de base de datos cargada y validada correctamente.")
        return True

if __name__ == "__main__":
    print("\n--- Probando la carga de configuración (config.py) ---")
    is_valid = check_db_config()
    if not is_valid:
        print("\nLa validación de la configuración falló. Revisa los mensajes anteriores.")
        sys.exit(1)
    else:
         print("\nPrueba de carga de configuración finalizada exitosamente.")
