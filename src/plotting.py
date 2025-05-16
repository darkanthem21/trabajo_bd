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

    # Asegurarse de que 'mes' esté ordenado y sea categórico para el gráfico
    df_ventas_mes = df_ventas_mes.sort_values('mes')
    # Mapear números de mes a nombres para mejor legibilidad
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

    plt.figure(figsize=(10, 7)) # Ajustar tamaño para barras horizontales
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

    plt.figure(figsize=(12, 7)) # Ancho mayor si hay varias categorías
    sns.barplot(x='nombre_categoria', y='ventas_totales_categoria', data=df_ventas_categoria, palette="magma", hue='nombre_categoria', dodge=False, legend=False)
    plt.title(f'Ventas Totales por Categoría de Producto - Año {year}', fontsize=16)
    plt.xlabel('Categoría', fontsize=12)
    plt.ylabel('Ventas Totales (CLP)', fontsize=12)
    plt.xticks(rotation=45, ha="right") # Rotar etiquetas si son largas
    plt.grid(axis='y', linestyle='--')
    plt.tight_layout()

    filepath = os.path.join(OUTPUT_DIR, filename)
    try:
        plt.savefig(filepath)
        print(f"INFO: Gráfico guardado en '{filepath}'")
    except Exception as e:
        print(f"ERROR: No se pudo guardar el gráfico en '{filepath}'. Razón: {e}")
    plt.close()
