import pandas as pd
from src.database import execute_query
from src.queries import (
    VENTAS_POR_MES_SQL,
    TOP_PRODUCTOS_CANTIDAD_SQL,
    VENTAS_POR_CATEGORIA_SQL,
    STOCK_EVOLUCION_SQL,
    DISTRIBUCION_TIPOS_MOVIMIENTO_SQL
)
from src.plotting import (
    graficar_ventas_por_mes,
    graficar_top_productos,
    graficar_ventas_por_categoria,
    graficar_evolucion_stock,
    graficar_distribucion_tipos_movimiento
)
import src.config

def analizar_ventas_por_mes(year: int):
    """
    Obtiene los datos de ventas por mes para un año y genera el gráfico.
    """
    print(f"\n--- Iniciando análisis: Ventas por Mes para el año {year} ---")
    params = {'year': year}
    print(f"DEBUG: params type: {type(params)}, value: {params}")
    df = execute_query(VENTAS_POR_MES_SQL, params)

    if df is not None:
        if not df.empty:
            df['mes'] = df['mes'].astype(int)
            df['ventas_totales'] = pd.to_numeric(df['ventas_totales'])
            filename = f"analisis_ventas_por_mes_{year}.png"
            graficar_ventas_por_mes(df, filename, year)
        else:
            print(f"INFO: No se encontraron datos de ventas por mes para el año {year}.")
    else:
        print(f"ERROR: No se pudieron obtener los datos de ventas por mes para el año {year}.")
    print("--- Análisis: Ventas por Mes finalizado ---")

def analizar_top_productos_vendidos(year: int):
    """
    Obtiene los datos del top 5 de productos más vendidos para un año y genera el gráfico.
    """
    print(f"\n--- Iniciando análisis: Top 5 Productos Vendidos para el año {year} ---")
    params = {'year': year}
    print(f"DEBUG: params type: {type(params)}, value: {params}")
    df = execute_query(TOP_PRODUCTOS_CANTIDAD_SQL, params)

    if df is not None:
        if not df.empty:
            df['cantidad_total_vendida'] = pd.to_numeric(df['cantidad_total_vendida'])
            filename = f"analisis_top_5_productos_vendidos_{year}.png"
            graficar_top_productos(df, filename, year)
        else:
            print(f"INFO: No se encontraron datos del top 5 de productos para el año {year}.")
    else:
        print(f"ERROR: No se pudieron obtener los datos del top 5 de productos para el año {year}.")
    print("--- Análisis: Top 5 Productos Vendidos finalizado ---")

def analizar_ventas_por_categoria(year: int):
    """
    Obtiene los datos de ventas por categoría de producto para un año y genera el gráfico.
    """
    print(f"\n--- Iniciando análisis: Ventas por Categoría para el año {year} ---")
    params = {'year': year}
    print(f"DEBUG: params type: {type(params)}, value: {params}")
    df = execute_query(VENTAS_POR_CATEGORIA_SQL, params)

    if df is not None:
        if not df.empty:
            df['ventas_totales_categoria'] = pd.to_numeric(df['ventas_totales_categoria'])
            filename = f"analisis_ventas_por_categoria_{year}.png"
            graficar_ventas_por_categoria(df, filename, year)
        else:
            print(f"INFO: No se encontraron datos de ventas por categoría para el año {year}.")
    else:
        print(f"ERROR: No se pudieron obtener los datos de ventas por categoría para el año {year}.")
    print("--- Análisis: Ventas por Categoría finalizado ---")

def analizar_evolucion_stock(year: int):
    """
    Obtiene los datos de evolución de stock por producto para un año y genera el gráfico.
    """
    print(f"\n--- Iniciando análisis: Evolución de Stock por Producto para el año {year} ---")
    params = {'year': year}
    print(f"DEBUG: params type: {type(params)}, value: {params}")
    df = execute_query(STOCK_EVOLUCION_SQL, params)

    if df is not None:
        if not df.empty:
            df['variacion_stock'] = pd.to_numeric(df['variacion_stock'])
            df['fecha'] = pd.to_datetime(df['fecha'])
            filename = f"analisis_evolucion_stock_{year}.png"
            graficar_evolucion_stock(df, filename, year)
        else:
            print(f"INFO: No se encontraron datos de evolución de stock para el año {year}.")
    else:
        print(f"ERROR: No se pudieron obtener los datos de evolución de stock para el año {year}.")
    print("--- Análisis: Evolución de Stock por Producto finalizado ---")

def analizar_distribucion_tipos_movimiento(year: int):
    """
    Obtiene los datos de distribución de tipos de movimiento de stock por mes para un año y genera el gráfico.
    """
    print(f"\n--- Iniciando análisis: Distribución de Tipos de Movimiento de Stock para el año {year} ---")
    params = {'year': year}
    print(f"DEBUG: params type: {type(params)}, value: {params}")
    df = execute_query(DISTRIBUCION_TIPOS_MOVIMIENTO_SQL, params)

    if df is not None:
        if not df.empty:
            df['total_movimiento'] = pd.to_numeric(df['total_movimiento'])
            df['mes'] = pd.to_datetime(df['mes'])
            filename = f"analisis_distribucion_tipos_movimiento_{year}.png"
            graficar_distribucion_tipos_movimiento(df, filename, year)
        else:
            print(f"INFO: No se encontraron datos de distribución de tipos de movimiento para el año {year}.")
    else:
        print(f"ERROR: No se pudieron obtener los datos de distribución de tipos de movimiento para el año {year}.")
    print("--- Análisis: Distribución de Tipos de Movimiento de Stock finalizado ---")