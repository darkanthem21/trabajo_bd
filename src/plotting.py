import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import os

OUTPUT_DIR = "output"

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def graficar_ventas_por_mes(df_ventas_mes: pd.DataFrame, filename: str, year: int):
    """
    Grafica las ventas totales por mes y guarda el gráfico.
    """
    if df_ventas_mes.empty:
        print(f"INFO: No hay datos de ventas por mes para el año {year} para graficar.")
        return

    df_ventas_mes = df_ventas_mes.sort_values('mes')
    meses_nombres = {
        1: 'Ene', 2: 'Feb', 3: 'Mar', 4: 'Abr', 5: 'May', 6: 'Jun',
        7: 'Jul', 8: 'Ago', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dic'
    }
    df_ventas_mes['mes_nombre'] = df_ventas_mes['mes'].map(meses_nombres)

    plt.figure(figsize=(10, 6))
    sns.barplot(x='mes_nombre', y='ventas_totales', data=df_ventas_mes, palette="viridis", hue='mes_nombre', dodge=False, legend=False)
    plt.title(f'Ventas Totales por Mes - Año {year}', fontsize=16)
    plt.xlabel('Mes', fontsize=12)
    plt.ylabel('Ventas Totales (CLP)', fontsize=12)
    plt.xticks(rotation=45)
    plt.grid(axis='y', linestyle='--')
    plt.tight_layout()

    filepath = os.path.join(OUTPUT_DIR, filename)
    try:
        plt.savefig(filepath)
        print(f"INFO: Gráfico guardado en '{filepath}'")
    except Exception as e:
        print(f"ERROR: No se pudo guardar el gráfico en '{filepath}'. Razón: {e}")
    plt.close()

def graficar_top_productos(df_top_productos: pd.DataFrame, filename: str, year: int):
    """
    Grafica el top 5 de productos más vendidos y guarda el gráfico.
    """
    if df_top_productos.empty:
        print(f"INFO: No hay datos de top productos para el año {year} para graficar.")
        return

    plt.figure(figsize=(10, 7))
    sns.barplot(x='cantidad_total_vendida', y='nombre_articulo', data=df_top_productos, palette="coolwarm", hue='nombre_articulo', dodge=False, legend=False)
    plt.title(f'Top 5 Productos Más Vendidos (por Cantidad) - Año {year}', fontsize=16)
    plt.xlabel('Cantidad Total Vendida', fontsize=12)
    plt.ylabel('Producto', fontsize=12)
    plt.tight_layout()

    filepath = os.path.join(OUTPUT_DIR, filename)
    try:
        plt.savefig(filepath)
        print(f"INFO: Gráfico guardado en '{filepath}'")
    except Exception as e:
        print(f"ERROR: No se pudo guardar el gráfico en '{filepath}'. Razón: {e}")
    plt.close()

def graficar_ventas_por_categoria(df_ventas_categoria: pd.DataFrame, filename: str, year: int):
    """
    Grafica las ventas totales por categoría de producto y guarda el gráfico.
    """
    if df_ventas_categoria.empty:
        print(f"INFO: No hay datos de ventas por categoría para el año {year} para graficar.")
        return

    plt.figure(figsize=(12, 7))
    sns.barplot(x='nombre_categoria', y='ventas_totales_categoria', data=df_ventas_categoria, palette="magma", hue='nombre_categoria', dodge=False, legend=False)
    plt.title(f'Ventas Totales por Categoría de Producto - Año {year}', fontsize=16)
    plt.xlabel('Categoría', fontsize=12)
    plt.ylabel('Ventas Totales (CLP)', fontsize=12)
    plt.xticks(rotation=45, ha="right")
    plt.grid(axis='y', linestyle='--')
    plt.tight_layout()

    filepath = os.path.join(OUTPUT_DIR, filename)
    try:
        plt.savefig(filepath)
        print(f"INFO: Gráfico guardado en '{filepath}'")
    except Exception as e:
        print(f"ERROR: No se pudo guardar el gráfico en '{filepath}'. Razón: {e}")
    plt.close()

def graficar_evolucion_stock(df_stock_evolucion: pd.DataFrame, filename: str, year: int):
    """
    Grafica la evolución diaria del stock por producto y guarda el gráfico.
    """
    if df_stock_evolucion.empty:
        print(f"INFO: No hay datos de evolución de stock para el año {year} para graficar.")
        return

    plt.figure(figsize=(14, 7))
    # Graficar una línea por producto
    for producto, datos in df_stock_evolucion.groupby('nombre_articulo'):
        datos_ordenados = datos.sort_values('fecha')
        plt.plot(datos_ordenados['fecha'], datos_ordenados['variacion_stock'].cumsum(), marker='o', label=producto)

    plt.title(f'Evolución del Stock por Producto - Año {year}', fontsize=16)
    plt.xlabel('Fecha', fontsize=12)
    plt.ylabel('Stock Acumulado', fontsize=12)
    plt.legend(title="Producto", bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()

    filepath = os.path.join(OUTPUT_DIR, filename)
    try:
        plt.savefig(filepath)
        print(f"INFO: Gráfico guardado en '{filepath}'")
    except Exception as e:
        print(f"ERROR: No se pudo guardar el gráfico en '{filepath}'. Razón: {e}")
    plt.close()

def graficar_distribucion_tipos_movimiento(df_movimientos: pd.DataFrame, filename: str, year: int):
    """
    Grafica la distribución de tipos de movimiento de stock por mes en un gráfico de líneas y guarda el gráfico.
    """
    if df_movimientos.empty:
        print(f"INFO: No hay datos de movimientos de stock para el año {year} para graficar.")
        return

    plt.figure(figsize=(14, 7))
    # Pivot para tener los tipos de movimiento como columnas
    df_pivot = df_movimientos.pivot(index='mes', columns='tipo_movimiento', values='total_movimiento').fillna(0)
    df_pivot.index = pd.to_datetime(df_pivot.index)

    df_pivot.plot(ax=plt.gca(), marker='o')
    plt.title(f'Distribución de Tipos de Movimiento de Stock por Mes - Año {year}', fontsize=16)
    plt.xlabel('Mes', fontsize=12)
    plt.ylabel('Total Movimiento', fontsize=12)
    plt.legend(title="Tipo de Movimiento", bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()

    filepath = os.path.join(OUTPUT_DIR, filename)
    try:
        plt.savefig(filepath)
        print(f"INFO: Gráfico guardado en '{filepath}'")
    except Exception as e:
        print(f"ERROR: No se pudo guardar el gráfico en '{filepath}'. Razón: {e}")
    plt.close()

def graficar_top_productos_rango(df_top_productos: pd.DataFrame, filename: str, fecha_inicio: str, fecha_fin: str):
    """
    Grafica el top N de productos más vendidos en un rango de fechas y guarda el gráfico.

    Args:
        df_top_productos:  DataFrame con los datos de los productos más vendidos.
        filename: Nombre del archivo para guardar el gráfico.
        fecha_inicio: Fecha de inicio del rango para el título.
        fecha_fin: Fecha de fin del rango para el título.
    """
    if df_top_productos.empty:
        print(f"INFO: No hay datos de top productos para el rango {fecha_inicio} a {fecha_fin} para graficar.")
        return

    plt.figure(figsize=(10, 7))
    sns.barplot(x='cantidad_total_vendida', y='nombre_articulo', data=df_top_productos, palette="coolwarm", hue='nombre_articulo', dodge=False, legend=False)
    plt.title(f'Top {len(df_top_productos)} Productos Más Vendidos ({fecha_inicio} a {fecha_fin})', fontsize=16)  # Título dinámico
    plt.xlabel('Cantidad Total Vendida', fontsize=12)
    plt.ylabel('Producto', fontsize=12)
    plt.tight_layout()

    filepath = os.path.join(OUTPUT_DIR, filename)
    try:
        plt.savefig(filepath)
        print(f"INFO: Gráfico guardado en '{filepath}'")
    except Exception as e:
        print(f"ERROR: No se pudo guardar el gráfico en '{filepath}'. Razón: {e}")
    plt.close()

def graficar_ventas_por_cliente(df_ventas_cliente: pd.DataFrame, filename: str, year: int):
    """
    Grafica el total de ventas por cliente.
    """
    if df_ventas_cliente.empty:
        print(f"INFO: No hay datos de ventas por cliente para el año {year} para graficar.")
        return

    plt.figure(figsize=(12, 7))
    sns.barplot(x='nombre_cliente', y='total_ventas', data=df_ventas_cliente, palette='viridis')
    plt.title(f'Ventas Totales por Cliente - Año {year}', fontsize=16)
    plt.xlabel('Cliente', fontsize=12)
    plt.ylabel('Ventas Totales', fontsize=12)
    plt.xticks(rotation=45, ha="right")  # Rotar las etiquetas para mejor legibilidad
    plt.tight_layout()

    filepath = os.path.join(OUTPUT_DIR, filename)
    try:
        plt.savefig(filepath)
        print(f"INFO: Gráfico guardado en '{filepath}'")
    except Exception as e:
        print(f"ERROR: No se pudo guardar el gráfico en '{filepath}'. Razón: {e}")
    plt.close()
