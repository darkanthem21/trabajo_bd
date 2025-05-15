import psycopg2
import random
import os
from datetime import datetime, timedelta
import logging

import src.config as config
from src.database import get_db_connection # Usaremos la conexión centralizada

N_FABRICANTES = 3
N_CATEGORIAS = 4
N_UBICACIONES = 5
N_CLIENTES = 10
N_PRODUCTOS = 20
N_VENTAS = 50
N_MOV_STOCK_OTROS = 30
AÑO_INICIO_SIM = 2023
AÑO_FIN_SIM = 2025
CODIGOS_MOVIMIENTO_ESPERADOS = [
    'ENTRADA_INI', 'SALIDA_VTA', 'ENTRADA_COMPRA',
    'AJUSTE_INV_POS', 'AJUSTE_INV_NEG'
]


def generar_fecha_aleatoria(año_inicio=AÑO_INICIO_SIM, año_fin=AÑO_FIN_SIM):
    start_date = datetime(año_inicio, 1, 1)
    end_date = datetime(año_fin, 12, 31)

    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days

    if days_between_dates < 0:
        logging.warning(f"El año de inicio ({año_inicio}) es posterior al año de fin ({año_fin}). Usando fecha de inicio.")
        return start_date
    if days_between_dates == 0:
        random_number_of_days = 0
    else:
        random_number_of_days = random.randrange(days_between_dates + 1)

    random_date = start_date + timedelta(
        days=random_number_of_days,
        hours=random.randint(0, 23),
        minutes=random.randint(0, 59),
        seconds=random.randint(0, 59)
    )
    return random_date

def generar_rut_chileno():
    rut_base = random.randint(5000000, 25000000)
    reversed_digits = [int(d) for d in reversed(str(rut_base))]
    factors = [2, 3, 4, 5, 6, 7] * (len(reversed_digits) // 6 + 1)
    s = sum(d * factors[i] for i, d in enumerate(reversed_digits))
    remainder = s % 11
    dv = 11 - remainder
    if dv == 11: dv_char = '0'
    elif dv == 10: dv_char = 'K'
    else: dv_char = str(dv)
    return f"{rut_base}-{dv_char}"

def obtener_ids_tipos_movimiento(cursor) -> dict:
    logging.info("Consultando IDs de tipos de movimiento desde dim_movimiento...")
    mov_type_ids = {}
    try:
        cursor.execute("SELECT id, tipo_movimiento FROM dim_movimiento;")
        results = cursor.fetchall()
        for row_id, tipo_mov in results: mov_type_ids[tipo_mov] = row_id
        missing = [c for c in CODIGOS_MOVIMIENTO_ESPERADOS if c not in mov_type_ids]
        if missing:
            logging.warning(f"Faltan IDs para los siguientes tipos de movimiento esperados: {missing}")
    except psycopg2.Error as e:
        logging.error(f"Error al consultar dim_movimiento: {e}")
        raise
    return mov_type_ids

def insertar_dimensiones_principales(cursor):
    fabricantes_ids, categorias_ids, ubicaciones_ids = [], [], []
    cliente_ids = list(range(1, N_CLIENTES + 1))

    logging.info("Insertando fabricantes...")
    fab_sql = "INSERT INTO fabricantes (nombre_fabricante) VALUES (%s) RETURNING fabricante_id;"
    for i in range(1, N_FABRICANTES + 1):
        cursor.execute(fab_sql, (f'Fabricante_{i}',)); fabricantes_ids.append(cursor.fetchone()[0])

    logging.info("Insertando categorías...")
    cat_sql = "INSERT INTO categorias (nombre_categoria) VALUES (%s) RETURNING categoria_id;"
    for i in range(1, N_CATEGORIAS + 1):
        cursor.execute(cat_sql, (f'Categoría_{i}',)); categorias_ids.append(cursor.fetchone()[0])

    logging.info("Insertando ubicaciones...")
    ubi_sql = "INSERT INTO ubicaciones (codigo_ubicacion, descripcion_ubicacion) VALUES (%s, %s) RETURNING ubicacion_id;"
    for i in range(1, N_UBICACIONES + 1):
        cursor.execute(ubi_sql, (f'UB{i:03}', f'Bodega {i}')); ubicaciones_ids.append(cursor.fetchone()[0])

    logging.info("Insertando clientes (con RUT)...")
    cli_sql = "INSERT INTO cliente (cliente_id, rut, nombre_cliente) VALUES (%s, %s, %s);"
    clientes_data = []
    ruts_generados = set()
    for i in cliente_ids:
        rut = generar_rut_chileno()
        while rut in ruts_generados: rut = generar_rut_chileno()
        ruts_generados.add(rut)
        clientes_data.append((i, rut, f'Cliente Nombre{i} Apellido{i}'))
    cursor.executemany(cli_sql, clientes_data)

    logging.info("Dimensiones principales insertadas.")
    return fabricantes_ids, categorias_ids, ubicaciones_ids, cliente_ids

def insertar_productos(cursor, fabricantes_ids, categorias_ids, ubicaciones_ids):
    producto_ids = list(range(1, N_PRODUCTOS + 1)) # Definir IDs de producto aquí
    logging.info("Insertando productos (precios/costos en CLP)...")
    productos_data = []
    for i in producto_ids:
        nombre = f'Aceite Sintético {i}W{random.choice([30, 40])}' if i % 2 == 0 else f'Filtro Aire Mod {i}'
        fab_id = random.choice(fabricantes_ids)
        cat_id = random.choice(categorias_ids)
        sku = f'SKU{i:05}'
        costo = random.randint(4000, 60000)
        precio = int(costo * random.uniform(1.25, 1.9))
        ubi_id = random.choice(ubicaciones_ids)
        productos_data.append((i, nombre, fab_id, cat_id, sku, costo, precio, ubi_id))

    prod_sql = """
    INSERT INTO productos (producto_id, nombre_articulo, fabricante_fk, categoria_fk, sku, costo, precio, ubicacion_fk)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
    """
    cursor.executemany(prod_sql, productos_data)
    logging.info(f"{len(productos_data)} productos insertados.")
    return producto_ids

def insertar_hechos(cursor, producto_ids, cliente_ids, ubicaciones_ids, mov_type_ids: dict):
    ventas_data, stock_data = [], []
    productos_info = {}

    cursor.execute("SELECT producto_id, costo, precio FROM productos;")
    for prod_id, costo, precio in cursor.fetchall():
        productos_info[prod_id] = {'costo': int(costo or 0), 'precio': int(precio or 0)}

    logging.info("Generando stock inicial...")
    tipo_mov_id_ini = mov_type_ids.get('ENTRADA_INI')
    if tipo_mov_id_ini is None:
        logging.error("ID de tipo de movimiento 'ENTRADA_INI' no encontrado en dim_movimiento.")
        raise ValueError("ID 'ENTRADA_INI' no encontrado.")
    fecha_inicial = datetime(AÑO_INICIO_SIM, 1, 1, 10, 0, 0)
    for prod_id in producto_ids:
        if random.random() < 0.8:
            cantidad_inicial = random.randint(20, 150)
            ubi_id = random.choice(ubicaciones_ids) if random.random() > 0.1 else None
            stock_data.append((prod_id, fecha_inicial, ubi_id, tipo_mov_id_ini, cantidad_inicial))

    logging.info("Simulando ventas y salidas de stock (CLP)...")
    tipo_mov_id_vta = mov_type_ids.get('SALIDA_VTA')
    if tipo_mov_id_vta is None:
        logging.error("ID de tipo de movimiento 'SALIDA_VTA' no encontrado.")
        raise ValueError("ID 'SALIDA_VTA' no encontrado.")

    for _ in range(1, N_VENTAS + 1):
        nro_boleta = random.randint(10000, 99999)
        prod_id = random.choice(producto_ids)
        fecha_venta = generar_fecha_aleatoria()
        cli_id = random.choice(cliente_ids) if random.random() > 0.05 else None
        cantidad_venta = random.randint(1, 5)
        if prod_id not in productos_info:
            logging.warning(f"Producto ID {prod_id} no encontrado en productos_info durante la simulación de ventas. Saltando esta venta.")
            continue

        costo_unitario = productos_info[prod_id]['costo']
        precio_unitario = productos_info[prod_id]['precio']
        total_venta = int(precio_unitario * cantidad_venta)

        ventas_data.append((nro_boleta, prod_id, fecha_venta, cli_id, cantidad_venta, costo_unitario, total_venta))
        ubi_id_venta = random.choice(ubicaciones_ids) if random.random() > 0.2 else None
        stock_data.append((prod_id, fecha_venta, ubi_id_venta, tipo_mov_id_vta, -cantidad_venta))

    logging.info("Simulando otras entradas y ajustes de stock...")
    tipo_mov_compra_id = mov_type_ids.get('ENTRADA_COMPRA')
    tipo_mov_aj_pos_id = mov_type_ids.get('AJUSTE_INV_POS')
    tipo_mov_aj_neg_id = mov_type_ids.get('AJUSTE_INV_NEG')

    otros_tipos_ids = [id_mov for id_mov in [tipo_mov_compra_id, tipo_mov_aj_pos_id, tipo_mov_aj_neg_id] if id_mov is not None]
    if not otros_tipos_ids:
        logging.warning("No se encontraron IDs para tipos de movimiento 'ENTRADA_COMPRA', 'AJUSTE_INV_POS', 'AJUSTE_INV_NEG'. No se simularán estos movimientos.")

    for _ in range(1, N_MOV_STOCK_OTROS + 1):
         if not otros_tipos_ids: break
         prod_id = random.choice(producto_ids)
         fecha_mov = generar_fecha_aleatoria()
         ubi_id = random.choice(ubicaciones_ids) if random.random() > 0.1 else None
         tipo_mov_id = random.choice(otros_tipos_ids)
         cantidad_mov = 0
         if tipo_mov_id == tipo_mov_compra_id: cantidad_mov = random.randint(10, 60)
         elif tipo_mov_id == tipo_mov_aj_pos_id: cantidad_mov = random.randint(1, 5)
         elif tipo_mov_id == tipo_mov_aj_neg_id: cantidad_mov = -random.randint(1, 5)
         stock_data.append((prod_id, fecha_mov, ubi_id, tipo_mov_id, cantidad_mov))

    sql_ventas = "INSERT INTO hechos_ventas (nro_boleta, producto_fk, fecha, cliente_fk, cantidad, costo_unitario, total_venta) VALUES (%s, %s, %s, %s, %s, %s, %s);"
    cursor.executemany(sql_ventas, ventas_data)

    sql_stock = "INSERT INTO hechos_stock (producto_fk, fecha, ubicacion_fk, tipo_movimiento_fk, cantidad) VALUES (%s, %s, %s, %s, %s);"
    cursor.executemany(sql_stock, stock_data)

def actualizar_stock_productos(cursor):
    logging.info("Calculando y actualizando stock_actual en productos...")
    sql_update_stock = """
    WITH StockCalculado AS (
        SELECT producto_fk, SUM(cantidad) AS stock_calculado
        FROM hechos_stock GROUP BY producto_fk
    )
    UPDATE productos p SET stock_actual = GREATEST(COALESCE(sc.stock_calculado, 0), 0)
    FROM StockCalculado sc WHERE p.producto_id = sc.producto_fk;
    """
    sql_update_cero = """
    UPDATE productos SET stock_actual = 0
    WHERE producto_id NOT IN (SELECT DISTINCT producto_fk FROM hechos_stock);
    """
    try:
        cursor.execute(sql_update_stock)
        logging.info(f"  {cursor.rowcount} filas de productos actualizadas con stock calculado.")
        cursor.execute(sql_update_cero)
        logging.info(f"  {cursor.rowcount} filas de productos actualizadas a stock 0 (sin movimientos).")
        logging.info("Stock actual en tabla productos actualizado.")
    except psycopg2.Error as e:
        logging.error(f"ERROR al actualizar stock_actual en productos: {e}")
        raise

def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    if not config.check_db_config():
        logger.critical("Configuración de base de datos invalida. Revisa los logs")
        return

    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            logger.critical("No se pudo establecer conexión con la base de datos. Finalizando script.")
            return

        with conn:
            with conn.cursor() as cursor:
                logger.info("PASO 1: Obteniendo IDs de Tipos de Movimiento...")
                mov_type_ids = obtener_ids_tipos_movimiento(cursor)
                if not all(c in mov_type_ids for c in ['ENTRADA_INI', 'SALIDA_VTA']): # Chequeo mínimo
                     logger.error("No se encontraron todos los IDs de tipos de movimiento necesarios en 'dim_movimiento'.")
                     raise ValueError("Faltan IDs de tipos de movimiento esenciales.")

                logger.info("PASO 2: Insertando Dimensiones Principales...")
                f_ids, c_ids, u_ids, cli_ids = insertar_dimensiones_principales(cursor)

                logger.info("PASO 3: Insertando Productos...")
                p_ids = insertar_productos(cursor, f_ids, c_ids, u_ids)

                logger.info("PASO 4: Insertando Hechos (Ventas y Stock)...")
                insertar_hechos(cursor, p_ids, cli_ids, u_ids, mov_type_ids)

                logger.info("PASO 5: Actualizando stock_actual en productos...")
                actualizar_stock_productos(cursor)

    except Exception as error: # Otros errores inesperados
        logger.error(f"Error Inesperado durante la inserción o actualización: {error}")
    finally:
        if conn:
            conn.close()
            logger.info("--- Conexión a la base de datos cerrada. ---")

if __name__ == "__main__":
    main()
