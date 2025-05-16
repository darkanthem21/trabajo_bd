# src/main.py
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.analysis import (
    analizar_ventas_por_mes,
    analizar_top_productos_vendidos,
    analizar_ventas_por_categoria
)
from src.config import check_db_config
from src.database import test_connection
from src.inserts import (AÑO_INICIO_SIM, AÑO_FIN_SIM)

def ejecutar_analisis_completo(year_analisis: int):
    """
    Ejecuta todos los análisis definidos para el año especificado.
    """
    print(f"============================================================")
    print(f"INICIANDO ANÁLISIS PARA EL AÑO: {year_analisis}")
    print(f"============================================================")

    analizar_ventas_por_mes(year_analisis)
    analizar_top_productos_vendidos(year_analisis)
    analizar_ventas_por_categoria(year_analisis)

    print(f"\n============================================================")
    print(f"TODOS LOS ANÁLISIS PARA EL AÑO {year_analisis} HAN FINALIZADO.")
    print(f"Los gráficos se han guardado en la carpeta '{os.path.join(os.getcwd(), 'output')}'.")
    print(f"============================================================")

if __name__ == "__main__":
    print("INFO: Verificando configuración de la base de datos...")
    if not check_db_config():
        print("CRITICAL: La configuración de la base de datos es inválida. Revisa tu archivo .env y los mensajes anteriores.")
        print("CRITICAL: El script de análisis no puede continuar.")
        sys.exit(1)
    print("INFO: Configuración de base de datos verificada.")
    print("INFO: Probando conexión a la base de datos...")
    if not test_connection():
        print("CRITICAL: No se pudo establecer conexión con la base de datos.")
        print("CRITICAL: El script de análisis no puede continuar.")
        sys.exit(1)
    print("INFO: Conexión a la base de datos exitosa.")

    if len(sys.argv) < 2:
        print("ERROR: Debes proporcionar el año como argumento.")
        print("Uso: python src/main.py <año>")
        sys.exit(1)

    try:
        year_to_analyze = int(sys.argv[1])
        if not (AÑO_INICIO_SIM <= year_to_analyze <= AÑO_FIN_SIM):
            raise ValueError("Año fuera de rango razonable.")
    except ValueError as e:
        print(f"ERROR: El año '{sys.argv[1]}' no es un número válido o está fuera de rango. {e}")
        sys.exit(1)

    ejecutar_analisis_completo(year_to_analyze)
