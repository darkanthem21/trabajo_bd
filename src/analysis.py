import pandas as pd
from src.database import execute_query
from src.queries import (
    VENTAS_POR_MES_SQL,
    TOP_PRODUCTOS_CANTIDAD_SQL,
    VENTAS_POR_CATEGORIA_SQL,
    STOCK_EVOLUCION_SQL,
    DISTRIBUCION_TIPOS_MOVIMIENTO_SQL,
    MAS_VENDIDO_FECHA_SQL,
    VENTAS_POR_CLIENTE_SQL
)
from src.plotting import (
    graficar_ventas_por_mes,
    graficar_top_productos,
    graficar_ventas_por_categoria,
    graficar_evolucion_stock,
    graficar_distribucion_tipos_movimiento,
    graficar_top_productos_rango,
    graficar_ventas_por_cliente
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

def analizar_top_productos_vendidos_en_rango(year: int):
    from datetime import datetime
    """
    Obtiene los top 10 productos más vendidos en un rango de fechas dentro del año especificado.
    El mes y día para el inicio y fin del rango se solicitan por terminal.
    """
    print(f"\n--- Iniciando análisis interactivo: Top 10 Productos Vendidos en Rango para el año {year} ---")
    print(f"Se le solicitará el mes y día para definir el rango dentro del año {year}.")

    fecha_inicio_dt = None
    fecha_fin_dt = None

    while True:
        try:
            mes_inicio_str = input(f"  Ingrese el MES de INICIO del rango (1-12) para {year}: ")
            mes_inicio = int(mes_inicio_str)
            dia_inicio_str = input(f"  Ingrese el DÍA de INICIO del rango para el mes {mes_inicio}/{year}: ")
            dia_inicio = int(dia_inicio_str)

            fecha_inicio_dt = datetime(year, mes_inicio, dia_inicio)
            fecha_inicio_str = fecha_inicio_dt.strftime('%Y-%m-%d')
            break
        except ValueError:
            print("  Valor inválido para mes o día. Asegúrese de que el mes esté entre 1-12 y el día sea válido para ese mes y año.")
        except Exception as e:
            print(f"  Error inesperado al procesar la fecha de inicio: {e}")

    while True:
        try:
            mes_fin_str = input(f"  Ingrese el MES de FIN del rango (1-12) para {year}: ")
            mes_fin = int(mes_fin_str)
            dia_fin_str = input(f"  Ingrese el DÍA de FIN del rango para el mes {mes_fin}/{year}: ")
            dia_fin = int(dia_fin_str)

            fecha_fin_dt = datetime(year, mes_fin, dia_fin)
            if fecha_inicio_dt and fecha_fin_dt < fecha_inicio_dt:
                print("  La fecha de fin no puede ser anterior a la fecha de inicio. Inténtelo de nuevo.")
                continue
            fecha_fin_str = fecha_fin_dt.strftime('%Y-%m-%d')
            break
        except ValueError:
            print("  Valor inválido para mes o día. Asegúrese de que el mes esté entre 1-12 y el día sea válido para ese mes y año.")
        except Exception as e:
            print(f"  Error inesperado al procesar la fecha de fin: {e}")

    print(f"Analizando productos más vendidos desde {fecha_inicio_str} hasta {fecha_fin_str}.")

    params = {'fecha_inicio': fecha_inicio_str, 'fecha_fin': fecha_fin_str}
    df = execute_query(MAS_VENDIDO_FECHA_SQL, params)

    if df is not None:
        if not df.empty:
            df['total_vendido'] = pd.to_numeric(df['total_vendido'])
            if 'total_vendido' in df.columns and 'cantidad_total_vendida' not in df.columns:
                 df.rename(columns={'total_vendido': 'cantidad_total_vendida'}, inplace=True)

            filename = f"analisis_top_10_productos_rango_{year}-{mes_inicio:02d}{dia_inicio:02d}_a_{year}-{mes_fin:02d}{dia_fin:02d}.png"
            graficar_top_productos_rango(df, filename, fecha_inicio_str, fecha_fin_str)
        else:
            print(f"INFO: No se encontraron datos de ventas en el rango {fecha_inicio_str} a {fecha_fin_str}.")
    else:
        print(f"ERROR: No se pudieron obtener los datos de ventas en el rango {fecha_inicio_str} a {fecha_fin_str}.")
    print(f"--- Análisis: Top 10 Productos Vendidos en Rango ({fecha_inicio_str} a {fecha_fin_str}) finalizado ---")

def analizar_ventas_por_cliente(year: int):
    """
    Obtiene el total de ventas por cliente para un año dado y genera el gráfico.
    """
    print(f"\n--- Iniciando análisis: Ventas por Cliente para el año {year} ---")
    params = {'year': year}
    print(f"DEBUG: params type: {type(params)}, value: {params}")
    df = execute_query(VENTAS_POR_CLIENTE_SQL, params)

    if df is not None:
        if not df.empty:
            df['total_ventas'] = pd.to_numeric(df['total_ventas'])
            filename = f"analisis_ventas_por_cliente_{year}.png"
            graficar_ventas_por_cliente(df, filename, year)
        else:
            print(f"INFO: No se encontraron datos de ventas por cliente para el año {year}.")
    else:
        print(f"ERROR: No se pudieron obtener los datos de ventas por cliente para el año {year}.")
    print("--- Análisis: Ventas por Cliente finalizado ---")
