import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.analysis import (
    analizar_ventas_por_mes,
    analizar_top_productos_vendidos,
    analizar_ventas_por_categoria,
    analizar_evolucion_stock,
    analizar_distribucion_tipos_movimiento,
    analizar_top_productos_vendidos_en_rango,
    analizar_top_10_clientes,
    analizar_histograma_montos_venta,
    analizar_stock_promedio_por_categoria,
    analizar_productos_bajo_stock,
    analizar_boxplot_montos_venta,
    analizar_heatmap_ventas_mes_categoria,
    analizar_pie_ganancia_categoria
)
from src.config import check_db_config
from src.database import test_connection
from src.inserts import (AÑO_INICIO_SIM, AÑO_FIN_SIM)

def ejecutar_analisis_completo(year_analisis: int):
    print("============================================================")
    print(f"INICIANDO ANÁLISIS PARA EL AÑO: {year_analisis}")
    print("============================================================")

    analizar_ventas_por_mes(year_analisis)
    analizar_top_productos_vendidos(year_analisis)
    analizar_ventas_por_categoria(year_analisis)
    analizar_evolucion_stock(year_analisis)
    analizar_distribucion_tipos_movimiento(year_analisis)
    analizar_top_10_clientes()
    analizar_histograma_montos_venta()
    analizar_stock_promedio_por_categoria()
    analizar_productos_bajo_stock()
    analizar_boxplot_montos_venta()
    analizar_heatmap_ventas_mes_categoria(year_analisis)
    analizar_pie_ganancia_categoria(year_analisis)
    analizar_top_productos_vendidos_en_rango(year_analisis)

    print("\n============================================================")
    print(f"TODOS LOS ANÁLISIS PARA EL AÑO {year_analisis} HAN FINALIZADO.")
    print("Los gráficos se han guardado en la carpeta 'output'.")
    print("============================================================")

if __name__ == "__main__":
    import sys
    # Ahora check_db_config y test_connection validan solo la base estrella (dimensional)
    if not check_db_config():
        print("CRITICAL: La configuración de la base de datos dimensional (estrella) es inválida. Revisa tu archivo .env y los mensajes anteriores.")
        print("CRITICAL: El script de análisis no puede continuar.")
        sys.exit(1)
    if not test_connection():
        print("CRITICAL: No se pudo establecer conexión con la base de datos dimensional (estrella).")
        print("CRITICAL: El script de análisis no puede continuar.")
        sys.exit(1)

    if len(sys.argv) == 2:
        try:
            year_to_analyze = int(sys.argv[1])
            if not (AÑO_INICIO_SIM <= year_to_analyze <= AÑO_FIN_SIM):
                raise ValueError(f"El año debe estar entre {AÑO_INICIO_SIM} y {AÑO_FIN_SIM}.")
            ejecutar_analisis_completo(year_to_analyze)
        except ValueError as e:
            print(f"ERROR: El argumento '{sys.argv[1]}' no es un año válido o está fuera del rango permitido. {e}")
            print("Uso: python src/main.py <año>")
            sys.exit(1)
    else:
        print("ERROR: Debes proporcionar exactamente un argumento: el año para el análisis.")
        print("Uso: python src/main.py <año>")
        sys.exit(1)
