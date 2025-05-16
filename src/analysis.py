import pandas as pd
from src.database import execute_query
from src.queries import (
    VENTAS_POR_MES_SQL,
    TOP_PRODUCTOS_CANTIDAD_SQL,
    VENTAS_POR_CATEGORIA_SQL
)
from src.plotting import (
    graficar_ventas_por_mes,
    graficar_top_productos,
    graficar_ventas_por_categoria
)
import src.config

def analizar_ventas_por_mes(year: int):
    """
    Obtiene los datos de ventas por mes para un año y genera el gráfico.
    """
    print(f"\n--- Iniciando análisis: Ventas por Mes para el año {year} ---")
    params = {'year': year}
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
