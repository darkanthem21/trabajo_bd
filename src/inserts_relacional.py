# src/inserts_relacional.py

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import psycopg2
import random
import datetime
from dateutil.relativedelta import relativedelta
from src.database import get_db_connection

def limpiar_tablas(conn):
    with conn.cursor() as cursor:
        print("Limpiando tablas existentes...")
        cursor.execute("TRUNCATE TABLE \"DetallesVenta\", \"Ventas\", \"MovimientosInventario\", \"Productos\", \"Clientes\", \"Categorias\", \"Fabricantes\", \"Ubicaciones\" RESTART IDENTITY CASCADE;")
    conn.commit()
    print("Tablas limpiadas y secuencias reiniciadas.")

def insertar_catalogos(conn):
    with conn.cursor() as cursor:
        print("Insertando datos en catálogos...")
        categorias = [('Aceites',), ('Filtros',), ('Baterías',), ('Amortiguadores',), ('Frenos',), ('Correas',), ('Aditivos',)]
        cursor.executemany("INSERT INTO \"Categorias\" (nombre) VALUES (%s) ON CONFLICT (nombre) DO NOTHING;", categorias)
        fabricantes = [('Mobil',), ('Bosch',), ('ACDelco',), ('Castrol',), ('Fram',), ('Liqui Moly',), ('Monroe',)]
        cursor.executemany("INSERT INTO \"Fabricantes\" (nombre) VALUES (%s) ON CONFLICT (nombre) DO NOTHING;", fabricantes)
        ubicaciones = [('Bodega Central',), ('Estantería A-1',), ('Estantería B-2',), ('Mostrador',), ('Taller',)]
        cursor.executemany("INSERT INTO \"Ubicaciones\" (descripcion) VALUES (%s);", ubicaciones)
    conn.commit()
    print("Catálogos insertados.")

def insertar_clientes(conn, cantidad):
    with conn.cursor() as cursor:
        print(f"Insertando {cantidad} clientes...")
        nombres = ["Ana", "Juan", "Maria", "Pedro", "Luisa", "Carlos", "Sofia", "Miguel", "Laura", "Diego"]
        apellidos = ["Gonzalez", "Rodriguez", "Gomez", "Fernandez", "Lopez", "Martinez", "Perez", "Sanchez"]
        for i in range(cantidad):
            rut = f"{random.randint(10000000, 25000000)}-{random.randint(0,9)}"
            nombre = f"{random.choice(nombres)} {random.choice(apellidos)}"
            cursor.execute("INSERT INTO \"Clientes\" (rut, nombre_completo) VALUES (%s, %s) ON CONFLICT (rut) DO NOTHING;", (rut, nombre))
    conn.commit()
    print("Clientes insertados.")


def insertar_productos(conn, cantidad):
    """Inserta productos con nombres genéricos y SKUs estructurados."""
    with conn.cursor() as cursor:
        print(f"Insertando {cantidad} productos con SKUs consistentes...")
        cursor.execute("SELECT categoria_id, nombre FROM \"Categorias\";")
        categorias = {row[0]: row[1] for row in cursor.fetchall()}
        cursor.execute("SELECT fabricante_id, nombre FROM \"Fabricantes\";")
        fabricantes = {row[0]: row[1] for row in cursor.fetchall()}
        cursor.execute("SELECT ubicacion_id FROM \"Ubicaciones\";")
        ubi_ids = [row[0] for row in cursor.fetchall()]
        nombres_base = ["Kit de Mantenimiento", "Componente de Motor", "Sistema de Frenado", "Filtro de Alto Flujo", "Aceite Sintético Avanzado", "Batería de Larga Duración", "Amortiguador de Gas"]
        modelos = ["Serie 100", "Pro-V", "XLT", "Gold Standard", "Eco-Max", "Ultra-Duty"]

        sku_counters = {}

        for i in range(cantidad):
            cat_id = random.choice(list(categorias.keys()))
            fab_id = random.choice(list(fabricantes.keys()))

            fab_prefix = fabricantes[fab_id][:3].upper()
            cat_prefix = categorias[cat_id][:3].upper()
            combo_key = f"{fab_prefix}-{cat_prefix}"
            current_seq = sku_counters.get(combo_key, 0) + 1
            sku_counters[combo_key] = current_seq
            sku = f"{combo_key}-{current_seq:04d}"

            nombre = f"{random.choice(nombres_base)} {random.choice(modelos)} {random.randint(100, 999)}"

            precio_venta = random.randint(150, 800) * 100
            costo_unitario = precio_venta * round(random.uniform(0.6, 0.8), 2)
            stock = 0

            params = (nombre, sku, costo_unitario, precio_venta, stock, cat_id, fab_id, random.choice(ubi_ids))
            cursor.execute("""
                INSERT INTO "Productos" (nombre, sku, costo_unitario, precio_venta, stock, categoria_id, fabricante_id, ubicacion_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
            """, params)
    conn.commit()
    print("Productos insertados.")

def registrar_movimientos_stock_inicial(conn):
    with conn.cursor() as cursor:
        print("Registrando stock inicial...")
        cursor.execute("SELECT producto_id, ubicacion_id FROM \"Productos\";")
        productos = cursor.fetchall()
        for prod_id, ubi_id in productos:
            cantidad_inicial = random.randint(20, 100)
            cursor.execute("INSERT INTO \"MovimientosInventario\" (tipo, cantidad, producto_id, ubicacion_id) VALUES ('compra_inicial', %s, %s, %s);", (cantidad_inicial, prod_id, ubi_id))
            cursor.execute("UPDATE \"Productos\" SET stock = stock + %s WHERE producto_id = %s;", (cantidad_inicial, prod_id))
    conn.commit()
    print("Stock inicial registrado y actualizado.")

def registrar_ventas_periodo(conn):
    with conn.cursor() as cursor:
        print("Registrando ventas para el período de 3 años...")
        cursor.execute("SELECT rut FROM \"Clientes\";")
        cliente_ruts = [row[0] for row in cursor.fetchall()]
        cursor.execute("SELECT producto_id, precio_venta FROM \"Productos\" WHERE stock > 0;")
        productos_disponibles = cursor.fetchall()
        if not productos_disponibles:
            print("No hay productos con stock para vender.")
            return
        end_date = datetime.date.today()
        start_date = end_date - relativedelta(years=3)
        total_ventas = 0
        current_month_start = datetime.date(start_date.year, start_date.month, 1)
        while current_month_start < end_date:
            num_ventas_mes = random.randint(480, 520)
            for _ in range(num_ventas_mes):
                cliente_rut = random.choice(cliente_ruts)
                boleta = f"BOL-{random.randint(10000, 99999)}"
                days_in_month = (current_month_start + relativedelta(months=1) - datetime.timedelta(days=1)).day
                random_day = random.randint(1, days_in_month)
                fecha = datetime.datetime(current_month_start.year, current_month_start.month, random_day, random.randint(9, 18), random.randint(0, 59))
                cursor.execute("INSERT INTO \"Ventas\" (boleta_numero, fecha, cliente_rut) VALUES (%s, %s, %s) RETURNING venta_id;", (boleta, fecha, cliente_rut))
                venta_id = cursor.fetchone()[0]
                num_productos_en_venta = random.randint(1, 4)
                for _ in range(num_productos_en_venta):
                    prod_id, precio = random.choice(productos_disponibles)
                    cantidad = random.randint(1, 5)
                    cursor.execute("SELECT stock FROM \"Productos\" WHERE producto_id = %s;", (prod_id,))
                    stock_actual = cursor.fetchone()[0]
                    if stock_actual < cantidad:
                        continue
                    subtotal = cantidad * precio
                    cursor.execute("INSERT INTO \"DetallesVenta\" (venta_id, producto_id, cantidad, precio_unitario, subtotal) VALUES (%s, %s, %s, %s, %s);", (venta_id, prod_id, cantidad, precio, subtotal))
                    cursor.execute("UPDATE \"Productos\" SET stock = stock - %s WHERE producto_id = %s;", (cantidad, prod_id))
                    cursor.execute("INSERT INTO \"MovimientosInventario\" (tipo, cantidad, producto_id) VALUES ('venta_cliente', %s, %s);", (cantidad, prod_id))
            total_ventas += num_ventas_mes
            print(f"  - Mes {current_month_start.strftime('%Y-%m')}: {num_ventas_mes} ventas registradas.")
            current_month_start += relativedelta(months=1)
    conn.commit()
    print(f"Ventas registradas. Total aproximado: {total_ventas}")


if __name__ == "__main__":
    conn = get_db_connection()
    if conn:
        try:
            limpiar_tablas(conn)
            insertar_catalogos(conn)
            insertar_clientes(conn, 150)
            insertar_productos(conn, 200)
            registrar_movimientos_stock_inicial(conn)
            registrar_ventas_periodo(conn)
        except psycopg2.Error as e:
            print(f"Ocurrió un error de base de datos: {e}")
        finally:
            conn.close()
            print("Proceso finalizado. Conexión cerrada.")
