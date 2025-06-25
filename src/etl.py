import psycopg2
from src import config
from src.queries_etl import *
from src.config import get_db_config
from src.queries_etl import TIPO_MOVIMIENTO_MAP

def get_connection(tipo):
    db_conf = config.get_db_config(tipo)
    try:
        return psycopg2.connect(
            dbname=db_conf['database'],
            user=db_conf['user'],
            password=db_conf['password'],
            host=db_conf['host'],
            port=db_conf['port']
        )
    except Exception as e:
        print(f"Error conectando a BD {tipo}: {e}")
        return None

def limpiar_tablas_destino(conn_dest):
    with conn_dest.cursor() as cur:
        for query in [
            TRUNCATE_HECHOS_STOCK,
            TRUNCATE_HECHOS_VENTAS,
            TRUNCATE_PRODUCTOS,
            TRUNCATE_CLIENTE,
            TRUNCATE_UBICACIONES,
            TRUNCATE_CATEGORIAS,
            TRUNCATE_FABRICANTES
        ]:
            cur.execute(query)
        conn_dest.commit()

def extraer_datos_origen(conn_origen):
    datos = {}
    with conn_origen.cursor() as cur:
        cur.execute(GET_FABRICANTES_ORIGEN_SQL)
        datos['fabricantes'] = cur.fetchall()
        cur.execute(GET_CATEGORIAS_ORIGEN_SQL)
        datos['categorias'] = cur.fetchall()
        cur.execute(GET_UBICACIONES_ORIGEN_SQL)
        datos['ubicaciones'] = cur.fetchall()
        cur.execute(GET_CLIENTES_ORIGEN_SQL)
        datos['clientes'] = cur.fetchall()
        cur.execute(GET_PRODUCTOS_ACTIVOS_ORIGEN_SQL)
        datos['productos'] = cur.fetchall()
        cur.execute(GET_VENTAS_DETALLE_ORIGEN_SQL)
        datos['ventas'] = cur.fetchall()
        cur.execute(GET_MOVIMIENTOS_STOCK_ORIGEN_SQL)
        datos['movimientos'] = cur.fetchall()
    return datos

def obtener_tipo_movimiento_ids(conn_dest):
    with conn_dest.cursor() as cur:
        cur.execute("SELECT id, tipo_movimiento FROM dim_movimiento;")
        rows = cur.fetchall()
        return {tipo: id_ for id_, tipo in rows}

def cargar_dimensiones(conn_dest, datos):
    fab_map = {}
    cat_map = {}
    ubi_map = {}
    cli_map = {}

    with conn_dest.cursor() as cur:
        for fab_id, nombre in datos['fabricantes']:
            cur.execute(INSERT_FABRICANTE_DESTINO_SQL, (nombre,))
            new_id = cur.fetchone()[0]
            fab_map[fab_id] = new_id

        for cat_id, nombre in datos['categorias']:
            cur.execute(INSERT_CATEGORIA_DESTINO_SQL, (nombre,))
            new_id = cur.fetchone()[0]
            cat_map[cat_id] = new_id

        for ubi_id, descripcion in datos['ubicaciones']:
            codigo = f"UB{ubi_id:03d}"
            cur.execute(INSERT_UBICACION_DESTINO_SQL, (codigo, descripcion))
            new_id = cur.fetchone()[0]
            ubi_map[ubi_id] = new_id

        for idx, (rut, nombre) in enumerate(datos['clientes'], 1):
            cur.execute(INSERT_CLIENTE_DESTINO_SQL, (idx, rut, nombre))
            cli_map[rut] = idx

        for prod in datos['productos']:
            (producto_id, nombre, fabricante_id, categoria_id, sku, costo_unitario, precio_venta, stock, ubicacion_id) = prod
            cur.execute(
                INSERT_PRODUCTO_DESTINO_SQL,
                (
                    producto_id,
                    nombre,
                    fab_map.get(fabricante_id),
                    cat_map.get(categoria_id),
                    sku,
                    costo_unitario,
                    precio_venta,
                    stock,
                    ubi_map.get(ubicacion_id)
                )
            )
        conn_dest.commit()
    return fab_map, cat_map, ubi_map, cli_map

def cargar_hechos(conn_dest, datos, cli_map, ubi_map, tipo_movimiento_ids):
    with conn_dest.cursor() as cur:
        for venta in datos['ventas']:
            (venta_id, boleta_numero, fecha, cliente_rut, prod_id, cantidad, precio_unitario, subtotal) = venta
            nro_boleta = int(''.join(filter(str.isdigit, str(boleta_numero))) or '0')
            cliente_id = cli_map.get(cliente_rut)
            total_venta = int(float(subtotal))
            cur.execute("SELECT costo FROM productos WHERE producto_id = %s;", (prod_id,))
            costo_unitario = cur.fetchone()[0]
            cur.execute(
                INSERT_VENTA_DESTINO_SQL,
                (
                    nro_boleta,
                    prod_id,
                    fecha,
                    cliente_id,
                    cantidad,
                    costo_unitario,
                    total_venta
                )
            )
        for mov in datos['movimientos']:
            (movimiento_id, fecha_movimiento, tipo, cantidad, producto_id, ubicacion_id) = mov
            tipo_dim = TIPO_MOVIMIENTO_MAP.get(tipo)
            tipo_movimiento_fk = tipo_movimiento_ids.get(tipo_dim)
            if tipo_movimiento_fk is None:
                print(f"ADVERTENCIA: Tipo de movimiento '{tipo}' no mapeado, se omite movimiento_id={movimiento_id}")
                continue
            cur.execute(
                INSERT_MOVIMIENTO_STOCK_DESTINO_SQL,
                (
                    producto_id,
                    fecha_movimiento,
                    ubi_map.get(ubicacion_id),
                    tipo_movimiento_fk,
                    cantidad
                )
            )
        conn_dest.commit()

def main():
    # No se requiere check_etl_config, solo se usan las dos bases del .env
    conn_origen = get_connection('transaccional')
    conn_dest = get_connection('estrella')
    if not conn_origen or not conn_dest:
        print("No se pudo conectar a una o ambas bases de datos.")
        import sys
        sys.exit(1)
    limpiar_tablas_destino(conn_dest)
    datos = extraer_datos_origen(conn_origen)
    fab_map, cat_map, ubi_map, cli_map = cargar_dimensiones(conn_dest, datos)
    tipo_movimiento_ids = obtener_tipo_movimiento_ids(conn_dest)
    cargar_hechos(conn_dest, datos, cli_map, ubi_map, tipo_movimiento_ids)
    conn_origen.close()
    conn_dest.close()
    print("ETL completado exitosamente.")

if __name__ == "__main__":
    main()
