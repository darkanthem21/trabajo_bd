# Este módulo espera DataFrames con nombres de columnas alineados al modelo estrella puro:
# - producto_id, nombre_articulo, categoria_id, nombre_categoria, etc.
# - Las funciones de análisis deben entregar los datos ya preparados con estos nombres.

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
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

def graficar_top_productos(df_top_productos, filename, year):
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

def graficar_ventas_por_categoria(df_ventas_categoria, filename, year):
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

def graficar_evolucion_stock(df_stock_evolucion, filename, year):
    if df_stock_evolucion.empty:
        print(f"INFO: No hay datos de evolución de stock para el año {year} para graficar.")
        return

    plt.figure(figsize=(14, 7))
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

def graficar_distribucion_tipos_movimiento(df_movimientos, filename, year):
    if df_movimientos.empty:
        print(f"INFO: No hay datos de movimientos de stock para el año {year} para graficar.")
        return

    plt.figure(figsize=(14, 7))
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

def graficar_top_productos_rango(df_top_productos, filename, fecha_inicio, fecha_fin):
    if df_top_productos.empty:
        print(f"INFO: No hay datos de top productos para el rango {fecha_inicio} a {fecha_fin} para graficar.")
        return

    plt.figure(figsize=(10, 7))
    sns.barplot(x='cantidad_total_vendida', y='nombre_articulo', data=df_top_productos, palette="coolwarm", hue='nombre_articulo', dodge=False, legend=False)
    plt.title(f'Top {len(df_top_productos)} Productos Más Vendidos ({fecha_inicio} a {fecha_fin})', fontsize=16)
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

def graficar_top_10_clientes(df_top_clientes, filename):
    if df_top_clientes.empty:
        print("INFO: No hay datos de top 10 clientes para graficar.")
        return

    plt.figure(figsize=(10, 6))
    sns.barplot(x='total_ventas', y='nombre_cliente', data=df_top_clientes, palette='viridis')
    plt.title('Top 10 Clientes por Ventas', fontsize=16)
    plt.xlabel('Ventas Totales (CLP)', fontsize=12)
    plt.ylabel('Cliente', fontsize=12)
    plt.tight_layout()

    filepath = os.path.join(OUTPUT_DIR, filename)
    try:
        plt.savefig(filepath)
        print(f"INFO: Gráfico guardado en '{filepath}'")
    except Exception as e:
        print(f"ERROR: No se pudo guardar el gráfico en '{filepath}'. Razón: {e}")
    plt.close()

def graficar_histograma_montos_venta(df_montos, filename):
    if df_montos.empty:
        print("INFO: No hay datos de montos de venta para graficar.")
        return

    plt.figure(figsize=(10, 6))
    plt.hist(df_montos['total_venta'], bins=30, color='skyblue', edgecolor='black')
    plt.title('Distribución de Montos de Venta', fontsize=16)
    plt.xlabel('Monto de Venta (CLP)', fontsize=12)
    plt.ylabel('Cantidad de Ventas', fontsize=12)
    plt.tight_layout()

    filepath = os.path.join(OUTPUT_DIR, filename)
    try:
        plt.savefig(filepath)
        print(f"INFO: Gráfico guardado en '{filepath}'")
    except Exception as e:
        print(f"ERROR: No se pudo guardar el gráfico en '{filepath}'. Razón: {e}")
    plt.close()

def graficar_stock_promedio_por_categoria(df_stock_cat, filename):
    if df_stock_cat.empty:
        print("INFO: No hay datos de stock promedio por categoría para graficar.")
        return

    plt.figure(figsize=(10, 6))
    sns.barplot(x='stock_promedio', y='nombre_categoria', data=df_stock_cat, palette='magma')
    plt.title('Stock Promedio por Categoría', fontsize=16)
    plt.xlabel('Stock Promedio', fontsize=12)
    plt.ylabel('Categoría', fontsize=12)
    plt.tight_layout()

    filepath = os.path.join(OUTPUT_DIR, filename)
    try:
        plt.savefig(filepath)
        print(f"INFO: Gráfico guardado en '{filepath}'")
    except Exception as e:
        print(f"ERROR: No se pudo guardar el gráfico en '{filepath}'. Razón: {e}")
    plt.close()

def graficar_productos_bajo_stock(df_bajo_stock, filename):
    if df_bajo_stock.empty:
        print("INFO: No hay productos con bajo stock para graficar.")
        return

    plt.figure(figsize=(12, 6))
    sns.barplot(x='stock_actual', y='nombre_articulo', data=df_bajo_stock, palette='rocket')
    plt.title('Productos con Bajo Stock (<5 unidades)', fontsize=16)
    plt.xlabel('Stock Actual', fontsize=12)
    plt.ylabel('Producto', fontsize=12)
    plt.tight_layout()

    filepath = os.path.join(OUTPUT_DIR, filename)
    try:
        plt.savefig(filepath)
        print(f"INFO: Gráfico guardado en '{filepath}'")
    except Exception as e:
        print(f"ERROR: No se pudo guardar el gráfico en '{filepath}'. Razón: {e}")
    plt.close()

def graficar_boxplot_montos_venta(df_montos, filename):
    if df_montos.empty:
        print("INFO: No hay datos de montos de venta para boxplot.")
        return

    plt.figure(figsize=(8, 6))
    sns.boxplot(x=df_montos['total_venta'], color='lightblue')
    plt.title('Boxplot de Montos de Venta', fontsize=16)
    plt.xlabel('Monto de Venta (CLP)', fontsize=12)
    plt.tight_layout()

    filepath = os.path.join(OUTPUT_DIR, filename)
    try:
        plt.savefig(filepath)
        print(f"INFO: Gráfico guardado en '{filepath}'")
    except Exception as e:
        print(f"ERROR: No se pudo guardar el gráfico en '{filepath}'. Razón: {e}")
    plt.close()

def graficar_heatmap_ventas_mes_categoria(df, filename, year):
    if df.empty:
        print("INFO: No hay datos para el heatmap de ventas por mes y categoría.")
        return
    tabla = df.pivot(index='nombre_categoria', columns='mes', values='ventas_totales').fillna(0)
    tabla = tabla.reindex(sorted(tabla.columns), axis=1)
    tabla = tabla.astype(float)
    plt.figure(figsize=(12, 7))
    sns.heatmap(tabla, annot=True, fmt=".0f", cmap="YlGnBu")
    plt.title(f"Heatmap de Ventas por Mes y Categoría - Año {year}", fontsize=16)
    plt.xlabel("Mes")
    plt.ylabel("Categoría")
    plt.tight_layout()
    filepath = os.path.join(OUTPUT_DIR, filename)
    try:
        plt.savefig(filepath)
        print(f"INFO: Gráfico guardado en '{filepath}'")
    except Exception as e:
        print(f"ERROR: No se pudo guardar el gráfico en '{filepath}'. Razón: {e}")
    plt.close()

def graficar_pie_ganancia_categoria(df, filename):
    # Elimina NaN, None y ganancias <= 0
    df = df.dropna(subset=['ganancia_total'])
    df = df[df['ganancia_total'] > 0]
    if df.empty:
        print("INFO: No hay categorías con ganancia para graficar el pie chart.")
        return

    plt.figure(figsize=(8, 8))
    plt.pie(df['ganancia_total'], labels=df['nombre_categoria'], autopct='%1.1f%%', startangle=140, colors=sns.color_palette('pastel'))
    plt.title('Participación en Ganancia por Categoría', fontsize=16)
    plt.tight_layout()
    filepath = os.path.join(OUTPUT_DIR, filename)
    try:
        plt.savefig(filepath)
        print(f"INFO: Gráfico guardado en '{filepath}'")
    except Exception as e:
        print(f"ERROR: No se pudo guardar el gráfico en '{filepath}'. Razón: {e}")
    plt.close()
