import psycopg2
import random
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dotenv_path = os.path.join(project_root, '.env')
if os.path.exists(dotenv_path): load_dotenv(dotenv_path=dotenv_path)
else: print(f"Advertencia: Archivo .env no encontrado en {dotenv_path}.")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
if not all([DB_NAME, DB_USER, DB_PASS]): exit("Error Crítico: Faltan variables de entorno esenciales.")
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

def get_db_connection():
    conn = None
    try:
        conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST, port=DB_PORT)
        return conn
    except Exception as e:
        print(f"Error Crítico al conectar a la BD con psycopg2: {e}")
        return None

def generar_fecha_aleatoria(año_inicio=AÑO_INICIO_SIM, año_fin=AÑO_FIN_SIM):
    start_date = datetime(año_inicio, 1, 1)
    end_date = datetime(año_fin, 12, 31)
    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days
    if days_between_dates <= 0: random_number_of_days = 0
    else: random_number_of_days = random.randrange(days_between_dates)
    random_date = start_date + timedelta(days=random_number_of_days, hours=random.randint(0, 23), minutes=random.randint(0, 59), seconds=random.randint(0, 59))
    return random_date

def generar_rut_chileno():
    """Genera un RUT chileno válido (formato XXXXXXXX-Y) de forma aleatoria."""
    rut_base = random.randint(5000000, 25000000)
    reversed_digits = [int(d) for d in reversed(str(rut_base))]
    factors = [2, 3, 4, 5, 6, 7] * (len(reversed_digits) // 6 + 1)
    s = sum(d * factors[i] for i, d in enumerate(reversed_digits))
    remainder = s % 11
    dv = 11 - remainder
    if dv == 11:
        dv_char = '0'
    elif dv == 10:
        dv_char = 'K'
    else:
        dv_char = str(dv)
    return f"{rut_base}-{dv_char}"

def obtener_ids_tipos_movimiento(cursor) -> dict:
    """Consulta dim_movimiento y devuelve dict {tipo_movimiento: id}."""
    print("Consultando IDs de tipos de movimiento desde dim_movimiento...")
    mov_type_ids = {}
    try:
        cursor.execute("SELECT id, tipo_movimiento FROM dim_movimiento;")
        results = cursor.fetchall()
        for row_id, tipo_mov in results: mov_type_ids[tipo_mov] = row_id
        print("IDs de tipos de movimiento obtenidos:", mov_type_ids)
        missing = [c for c in CODIGOS_MOVIMIENTO_ESPERADOS if c not in mov_type_ids]
        if missing: print(f"Advertencia: Faltan IDs para: {missing}")
    except psycopg2.Error as e:
        print(f"Error al consultar dim_movimiento: {e}"); raise
    return mov_type_ids

def insertar_dimensiones_principales(cursor):
    """Inserta fabricantes, categorías, ubicaciones, clientes (CON RUT). Devuelve IDs."""
    fabricantes_ids = []
    categorias_ids = []
    ubicaciones_ids = []
    cliente_ids = list(range(1, N_CLIENTES + 1))
    producto_ids = list(range(1, N_PRODUCTOS + 1))

    print("Insertando fabricantes..."); fab_sql = "INSERT INTO fabricantes (nombre_fabricante) VALUES (%s) RETURNING fabricante_id;"
    for i in range(1, N_FABRICANTES + 1): cursor.execute(fab_sql, (f'Fabricante_{i}',)); fabricantes_ids.append(cursor.fetchone()[0])
    print("Insertando categorías..."); cat_sql = "INSERT INTO categorias (nombre_categoria) VALUES (%s) RETURNING categoria_id;"
    for i in range(1, N_CATEGORIAS + 1): cursor.execute(cat_sql, (f'Categoría_{i}',)); categorias_ids.append(cursor.fetchone()[0])
    print("Insertando ubicaciones..."); ubi_sql = "INSERT INTO ubicaciones (codigo_ubicacion, descripcion_ubicacion) VALUES (%s, %s) RETURNING ubicacion_id;"
    for i in range(1, N_UBICACIONES + 1): cursor.execute(ubi_sql, (f'UB{i:03}', f'Bodega {i}')); ubicaciones_ids.append(cursor.fetchone()[0])

    print("Insertando clientes (con RUT)...")
    cli_sql = "INSERT INTO cliente (cliente_id, rut, nombre_cliente) VALUES (%s, %s, %s);"
    clientes_data = []
    ruts_generados = set()
    for i in cliente_ids:
        rut = generar_rut_chileno()
        while rut in ruts_generados:
            rut = generar_rut_chileno()
        ruts_generados.add(rut)
        clientes_data.append((i, rut, f'Cliente Nombre{i} Apellido{i}'))
    cursor.executemany(cli_sql, clientes_data)

    print("Dimensiones principales insertadas.")
    return fabricantes_ids, categorias_ids, ubicaciones_ids, cliente_ids, producto_ids

def insertar_productos(cursor, fabricantes_ids, categorias_ids, ubicaciones_ids, producto_ids):
    """Inserta productos con precios/costos como enteros (CLP)."""
    print("Insertando productos (precios/costos en CLP)...")
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
    print(f"{len(productos_data)} productos insertados.")

def insertar_hechos(cursor, producto_ids, cliente_ids, ubicaciones_ids, mov_type_ids: dict):
    """Inserta ventas y stock (costos/totales en CLP)."""
    ventas_data = []
    stock_data = []
    productos_info = {}

    cursor.execute("SELECT producto_id, costo, precio FROM productos;")
    for prod_id, costo, precio in cursor.fetchall():
        productos_info[prod_id] = {'costo': int(costo) if costo is not None else 0,
                                   'precio': int(precio) if precio is not None else 0}

    print("Generando stock inicial...")
    tipo_mov_id_ini = mov_type_ids.get('ENTRADA_INI')
    if tipo_mov_id_ini is None: raise ValueError("ID 'ENTRADA_INI' no encontrado.")
    fecha_inicial = datetime(AÑO_INICIO_SIM, 1, 1, 10, 0, 0)
    for prod_id in producto_ids:
        if random.random() < 0.8:
            cantidad_inicial = random.randint(20, 150)
            ubi_id = random.choice(ubicaciones_ids) if random.random() > 0.1 else None
            stock_data.append((prod_id, fecha_inicial, ubi_id, tipo_mov_id_ini, cantidad_inicial))

    print("Simulando ventas y salidas de stock (CLP)...")
    tipo_mov_id_vta = mov_type_ids.get('SALIDA_VTA')
    if tipo_mov_id_vta is None: raise ValueError("ID 'SALIDA_VTA' no encontrado.")
    for i in range(1, N_VENTAS + 1):
        nro_boleta = random.randint(10000, 99999)
        prod_id = random.choice(producto_ids)
        fecha_venta = generar_fecha_aleatoria()
        cli_id = random.choice(cliente_ids) if random.random() > 0.05 else None
        cantidad_venta = random.randint(1, 5)
        if prod_id not in productos_info: continue

        costo_unitario = productos_info[prod_id]['costo']
        precio_unitario = productos_info[prod_id]['precio']
        total_venta = int(precio_unitario * cantidad_venta)

        ventas_data.append((nro_boleta, prod_id, fecha_venta, cli_id, cantidad_venta, costo_unitario, total_venta))
        ubi_id_venta = random.choice(ubicaciones_ids) if random.random() > 0.2 else None
        stock_data.append((prod_id, fecha_venta, ubi_id_venta, tipo_mov_id_vta, -cantidad_venta))

    print("Simulando otras entradas y ajustes de stock...")
    tipo_mov_compra_id = mov_type_ids.get('ENTRADA_COMPRA')
    tipo_mov_aj_pos_id = mov_type_ids.get('AJUSTE_INV_POS')
    tipo_mov_aj_neg_id = mov_type_ids.get('AJUSTE_INV_NEG')
    otros_tipos_ids = [id for id in [tipo_mov_compra_id, tipo_mov_aj_pos_id, tipo_mov_aj_neg_id] if id is not None]
    if not otros_tipos_ids: print("Advertencia: No se encontraron IDs para otros tipos de movimiento.")

    for i in range(1, N_MOV_STOCK_OTROS + 1):
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

    print("Insertando hechos de ventas...")
    sql_ventas = """
    INSERT INTO hechos_ventas (nro_boleta, producto_fk, fecha, cliente_fk, cantidad, costo_unitario, total_venta)
    VALUES (%s, %s, %s, %s, %s, %s, %s);
    """
    cursor.executemany(sql_ventas, ventas_data)
    print(f"{len(ventas_data)} hechos de ventas insertados.")

    print("Insertando hechos de stock...")
    sql_stock = """
    INSERT INTO hechos_stock (producto_fk, fecha, ubicacion_fk, tipo_movimiento_fk, cantidad)
    VALUES (%s, %s, %s, %s, %s);
    """
    cursor.executemany(sql_stock, stock_data)
    print(f"{len(stock_data)} hechos de stock insertados.")

def actualizar_stock_productos(cursor):
    """
    Calcula el stock actual para cada producto sumando los movimientos
    en hechos_stock y actualiza la columna productos.stock_actual.
    """
    print("Calculando y actualizando stock_actual en productos...")

    sql_update_stock = """
    WITH StockCalculado AS (
        SELECT
            producto_fk,
            SUM(cantidad) AS stock_calculado
        FROM
            hechos_stock
        GROUP BY
            producto_fk
    )
    UPDATE productos p
    SET stock_actual = GREATEST(COALESCE(sc.stock_calculado, 0), 0) -- Asegura que sea 0 o más
    FROM StockCalculado sc
    WHERE p.producto_id = sc.producto_fk;
    """
    sql_update_cero = """
    UPDATE productos
    SET stock_actual = 0
    WHERE producto_id NOT IN (SELECT DISTINCT producto_fk FROM hechos_stock);
    """

    try:
        print("  - Actualizando stock para productos con movimientos...")
        cursor.execute(sql_update_stock)
        rows_updated_with_moves = cursor.rowcount
        print(f"    {rows_updated_with_moves} filas actualizadas (con movimientos).")

        print("  - Estableciendo en 0 stock para productos sin movimientos...")
        cursor.execute(sql_update_cero)
        rows_updated_to_zero = cursor.rowcount
        print(f"    {rows_updated_to_zero} filas actualizadas a 0 (sin movimientos).")

        print("Stock actual en tabla productos actualizado coherentemente.")

    except psycopg2.Error as e:
        print(f"ERROR al actualizar stock_actual en productos: {e}")
        raise

def main():
    print("--- Iniciando Script de Inserción de Datos de Prueba (v3 - con RUT y CLP) ---")
    conn = get_db_connection()
    if not conn: print("Finalizando script: error de conexión."); return

    try:
        with conn: # Transacción automática (commit al final, rollback en error)
            with conn.cursor() as cursor:

                print("\nPASO 1: Obteniendo IDs de Tipos de Movimiento...")
                mov_type_ids = obtener_ids_tipos_movimiento(cursor)
                if not all(c in mov_type_ids for c in CODIGOS_MOVIMIENTO_ESPERADOS):
                     raise ValueError("No se encontraron todos los IDs de tipos de movimiento necesarios en 'dim_movimiento'.")

                print("\nPASO 2: Insertando Dimensiones Principales...")
                f_ids, c_ids, u_ids, cli_ids, p_ids = insertar_dimensiones_principales(cursor)

                print("\nPASO 3: Insertando Productos...")
                insertar_productos(cursor, f_ids, c_ids, u_ids, p_ids)

                print("\nPASO 4: Insertando Hechos (Ventas y Stock)...")
                insertar_hechos(cursor, p_ids, cli_ids, u_ids, mov_type_ids)

                print("\nPASO 5: Actualizando stock_actual en productos...")
                actualizar_stock_productos(cursor)

        print("\n--- ¡Inserción y actualización de stock completadas exitosamente! Transacción confirmada. ---")

    except (Exception, psycopg2.DatabaseError) as error:
        print(f"\n--- ERROR DURANTE LA INSERCIÓN O ACTUALIZACIÓN: {error} ---")
        print("--- La transacción fue revertida automáticamente (rollback). ---")
    finally:
        if conn:
            conn.close()
            print("--- Conexión a la base de datos cerrada. ---")

if __name__ == "__main__":
    main()
