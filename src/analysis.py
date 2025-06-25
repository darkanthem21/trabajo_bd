import pandas as pd
from src.database import execute_query
from src.queries import (
    VENTAS_POR_MES_SQL,
    TOP_PRODUCTOS_CANTIDAD_SQL,
    VENTAS_POR_CATEGORIA_SQL,
    STOCK_EVOLUCION_SQL,
    DISTRIBUCION_TIPOS_MOVIMIENTO_SQL,
    MAS_VENDIDO_FECHA_SQL
)
from src.plotting import (
    graficar_ventas_por_mes,
    graficar_top_productos,
    graficar_ventas_por_categoria,
    graficar_evolucion_stock,
    graficar_distribucion_tipos_movimiento,
    graficar_top_productos_rango,
    graficar_top_10_clientes,
    graficar_histograma_montos_venta,
    graficar_stock_promedio_por_categoria,
    graficar_productos_bajo_stock,
    graficar_boxplot_montos_venta,
    graficar_heatmap_ventas_mes_categoria,
    graficar_pie_ganancia_categoria
)

def analizar_ventas_por_mes(year: int):
    """
    Obtiene los datos de ventas por mes para un año y genera el gráfico.
    """
    print(f"\n--- Iniciando análisis: Ventas por Mes para el año {year} ---")
    params = {'year': year}
    print(f"DEBUG: params type: {type(params)}, value: {params}")
    df = execute_query(VENTAS_POR_MES_SQL, params, tipo="estrella")

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
    df = execute_query(TOP_PRODUCTOS_CANTIDAD_SQL, params, tipo="estrella")

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
    df = execute_query(VENTAS_POR_CATEGORIA_SQL, params, tipo="estrella")

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
    df = execute_query(STOCK_EVOLUCION_SQL, params, tipo="estrella")

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
    df = execute_query(DISTRIBUCION_TIPOS_MOVIMIENTO_SQL, params, tipo="estrella")

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
    df = execute_query(MAS_VENDIDO_FECHA_SQL, params, tipo="estrella")

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

def analizar_top_10_clientes():
    """
    Obtiene el top 10 de clientes por ventas y genera el gráfico.
    """
    print(f"\n--- Iniciando análisis: Top 10 Clientes por Ventas ---")
    from src.queries import TOP_10_CLIENTES_SQL
    df = execute_query(TOP_10_CLIENTES_SQL, tipo="estrella")
    if df is not None and not df.empty:
        graficar_top_10_clientes(df, "top_10_clientes_ventas.png")
    else:
        print("INFO: No se encontraron datos para el Top 10 de clientes.")
    print("--- Análisis: Top 10 Clientes por Ventas finalizado ---")

def analizar_histograma_montos_venta():
    """
    Genera un histograma de los montos de venta.
    """
    print(f"\n--- Iniciando análisis: Histograma de Montos de Venta ---")
    from src.queries import HISTOGRAM_MONTOS_VENTA_SQL
    df = execute_query(HISTOGRAM_MONTOS_VENTA_SQL, tipo="estrella")
    if df is not None and not df.empty:
        graficar_histograma_montos_venta(df, "histograma_montos_venta.png")
    else:
        print("INFO: No se encontraron datos de montos de venta.")
    print("--- Análisis: Histograma de Montos de Venta finalizado ---")

def analizar_stock_promedio_por_categoria():
    """
    Genera un gráfico de stock promedio por categoría.
    """
    print(f"\n--- Iniciando análisis: Stock Promedio por Categoría ---")
    from src.queries import STOCK_PROMEDIO_POR_CATEGORIA_SQL
    df = execute_query(STOCK_PROMEDIO_POR_CATEGORIA_SQL, tipo="estrella")
    if df is not None and not df.empty:
        graficar_stock_promedio_por_categoria(df, "stock_promedio_por_categoria.png")
    else:
        print("INFO: No se encontraron datos de stock promedio por categoría.")
    print("--- Análisis: Stock Promedio por Categoría finalizado ---")

def analizar_productos_bajo_stock():
    """
    Genera un gráfico de productos con bajo stock (<5 unidades).
    """
    print(f"\n--- Iniciando análisis: Productos con Bajo Stock (<5 unidades) ---")
    from src.queries import PRODUCTOS_BAJO_STOCK_SQL
    df = execute_query(PRODUCTOS_BAJO_STOCK_SQL, tipo="estrella")
    if df is not None and not df.empty:
        graficar_productos_bajo_stock(df, "productos_bajo_stock.png")
    else:
        print("INFO: No se encontraron productos con bajo stock.")
    print("--- Análisis: Productos con Bajo Stock finalizado ---")

def analizar_boxplot_montos_venta():
    """
    Genera un boxplot de los montos de venta.
    """
    print(f"\n--- Iniciando análisis: Boxplot de Montos de Venta ---")
    from src.queries import HISTOGRAM_MONTOS_VENTA_SQL
    df = execute_query(HISTOGRAM_MONTOS_VENTA_SQL, tipo="estrella")
    if df is not None and not df.empty:
        graficar_boxplot_montos_venta(df, "boxplot_montos_venta.png")
    else:
        print("INFO: No se encontraron datos de montos de venta para boxplot.")
    print("--- Análisis: Boxplot de Montos de Venta finalizado ---")

def analizar_heatmap_ventas_mes_categoria(year: int):
    """
    Genera un heatmap de ventas por mes y categoría.
    """
    print(f"\n--- Iniciando análisis: Heatmap Ventas por Mes y Categoría ---")
    from src.queries import VENTAS_MES_CATEGORIA_SQL
    df = execute_query(VENTAS_MES_CATEGORIA_SQL, {'year': year}, tipo="estrella")
    if df is not None and not df.empty:
        graficar_heatmap_ventas_mes_categoria(df, f"heatmap_ventas_mes_categoria_{year}.png", year)
    else:
        print("INFO: No se encontraron datos para el heatmap de ventas por mes y categoría.")
    print("--- Análisis: Heatmap Ventas por Mes y Categoría finalizado ---")

def analizar_pie_ganancia_categoria(year: int):
    """
    Genera un pie chart de la ganancia total por categoría.
    """
    print(f"\n--- Iniciando análisis: Pie Chart de Ganancia por Categoría ---")
    from src.queries import PIE_GANANCIA_CATEGORIA_SQL
    df = execute_query(PIE_GANANCIA_CATEGORIA_SQL, {'year': year}, tipo="estrella")
    if df is not None and not df.empty:
        graficar_pie_ganancia_categoria(df, f"pie_ganancia_categoria_{year}.png")
    else:
        print("INFO: No se encontraron datos de ganancia por categoría.")
    print("--- Análisis: Pie Chart de Ganancia por Categoría finalizado ---")
