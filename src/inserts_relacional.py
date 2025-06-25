# src/inserts_relacional.py - VERSIÓN CORREGIDA
"""
Script para poblar la base de datos relacional con datos de prueba
Versión corregida que asegura compatibilidad con el ETL
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import psycopg2
import random
import datetime
from dateutil.relativedelta import relativedelta
from src.database import get_db_connection  # Siempre conecta a la base transaccional

# Tipos de movimiento que deben coincidir con el mapeo del ETL
TIPOS_MOVIMIENTO_VALIDOS = [
    'compra_inicial',
    'venta_cliente',
    'compra_proveedor',
    'ajuste_positivo',
    'ajuste_negativo'
]

def limpiar_tablas(conn):
    """Limpia todas las tablas y reinicia las secuencias"""
    with conn.cursor() as cursor:
        print("🧹 Limpiando tablas existentes...")
        cursor.execute("""
            TRUNCATE TABLE "DetallesVenta", "Ventas", "MovimientosInventario",
                          "Productos", "Clientes", "Categorias", "Fabricantes", "Ubicaciones"
            RESTART IDENTITY CASCADE;
        """)
    conn.commit()
    print("✅ Tablas limpiadas y secuencias reiniciadas.")

def insertar_catalogos(conn):
    """Inserta datos en las tablas de catálogos"""
    with conn.cursor() as cursor:
        print("📚 Insertando datos en catálogos...")

        # Categorías más realistas para lubricentro
        categorias = [
            ('Aceites',),
            ('Filtros',),
            ('Baterías',),
            ('Amortiguadores',),
            ('Frenos',),
            ('Correas',),
            ('Aditivos',),
            ('Lubricantes',),
            ('Repuestos Motor',)
        ]
        cursor.executemany(
            'INSERT INTO "Categorias" (nombre) VALUES (%s) ON CONFLICT (nombre) DO NOTHING;',
            categorias
        )

        # Fabricantes conocidos
        fabricantes = [
            ('Mobil',),
            ('Bosch',),
            ('ACDelco',),
            ('Castrol',),
            ('Fram',),
            ('Liqui Moly',),
            ('Monroe',),
            ('Shell',),
            ('Valvoline',),
            ('Mann Filter',)
        ]
        cursor.executemany(
            'INSERT INTO "Fabricantes" (nombre) VALUES (%s) ON CONFLICT (nombre) DO NOTHING;',
            fabricantes
        )

        # Ubicaciones del almacén
        ubicaciones = [
            ('Bodega Central',),
            ('Estantería A-1',),
            ('Estantería A-2',),
            ('Estantería B-1',),
            ('Estantería B-2',),
            ('Estantería C-1',),
            ('Mostrador',),
            ('Taller Mecánico',),
            ('Área de Batería',),
            ('Depósito Aceites',)
        ]
        cursor.executemany('INSERT INTO "Ubicaciones" (descripcion) VALUES (%s);', ubicaciones)

    conn.commit()
    print("✅ Catálogos insertados correctamente.")

def generar_rut_chileno():
    """Genera un RUT chileno válido"""
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

def insertar_clientes(conn, cantidad):
    """Inserta clientes con RUTs válidos"""
    with conn.cursor() as cursor:
        print(f"👥 Insertando {cantidad} clientes...")

        nombres = ["Ana", "Juan", "María", "Pedro", "Luisa", "Carlos", "Sofía", "Miguel", "Laura", "Diego",
                  "Carmen", "Francisco", "Isabel", "Manuel", "Rosa", "Antonio", "Pilar", "José", "Elena", "Ramón"]
        apellidos = ["González", "Rodríguez", "Gómez", "Fernández", "López", "Martínez", "Pérez", "Sánchez",
                    "Romero", "Soto", "Contreras", "Silva", "Sepúlveda", "Morales", "Ortega", "Castillo"]

        ruts_generados = set()
        clientes_insertados = 0

        for i in range(cantidad):
            # Generar RUT único
            rut = generar_rut_chileno()
            while rut in ruts_generados:
                rut = generar_rut_chileno()
            ruts_generados.add(rut)

            nombre = f"{random.choice(nombres)} {random.choice(apellidos)} {random.choice(apellidos)}"

            try:
                cursor.execute(
                    'INSERT INTO "Clientes" (rut, nombre_completo) VALUES (%s, %s);',
                    (rut, nombre)
                )
                clientes_insertados += 1
            except psycopg2.IntegrityError:
                # RUT duplicado, continuar
                continue

    conn.commit()
    print(f"✅ {clientes_insertados} clientes insertados.")

def insertar_productos(conn, cantidad):
    """Inserta productos con nombres realistas y SKUs estructurados"""
    with conn.cursor() as cursor:
        print(f"🛠️  Insertando {cantidad} productos...")

        # Obtener IDs de catálogos
        cursor.execute('SELECT categoria_id, nombre FROM "Categorias";')
        categorias = {row[0]: row[1] for row in cursor.fetchall()}

        cursor.execute('SELECT fabricante_id, nombre FROM "Fabricantes";')
        fabricantes = {row[0]: row[1] for row in cursor.fetchall()}

        cursor.execute('SELECT ubicacion_id FROM "Ubicaciones";')
        ubi_ids = [row[0] for row in cursor.fetchall()]

        # Plantillas de productos por categoría
        productos_por_categoria = {
            "Aceites": [
                ("Aceite Motor 5W-30", 15000, 25000),
                ("Aceite Motor 10W-40", 12000, 20000),
                ("Aceite Sintético 0W-20", 18000, 30000),
                ("Aceite Transmisión ATF", 8000, 15000),
                ("Aceite Hidráulico", 10000, 18000)
            ],
            "Filtros": [
                ("Filtro de Aceite", 3000, 8000),
                ("Filtro de Aire", 4000, 10000),
                ("Filtro de Combustible", 5000, 12000),
                ("Filtro de Cabina", 6000, 14000),
                ("Filtro Hidráulico", 7000, 16000)
            ],
            "Baterías": [
                ("Batería 45Ah", 35000, 60000),
                ("Batería 65Ah", 45000, 80000),
                ("Batería 75Ah", 55000, 95000),
                ("Batería AGM 90Ah", 70000, 120000),
                ("Batería Gel 100Ah", 80000, 140000)
            ],
            "Amortiguadores": [
                ("Amortiguador Delantero", 25000, 45000),
                ("Amortiguador Trasero", 20000, 38000),
                ("Amortiguador Gas", 30000, 55000),
                ("Kit Amortiguador", 40000, 70000),
                ("Amortiguador Reforzado", 35000, 65000)
            ],
            "Frenos": [
                ("Pastillas de Freno", 15000, 28000),
                ("Disco de Freno", 20000, 40000),
                ("Líquido de Frenos DOT-4", 3000, 8000),
                ("Kit de Frenos", 35000, 65000),
                ("Zapatas de Freno", 12000, 25000)
            ],
            "Correas": [
                ("Correa de Distribución", 8000, 18000),
                ("Correa Alternador", 5000, 12000),
                ("Correa Poly-V", 4000, 10000),
                ("Kit de Correas", 15000, 30000),
                ("Correa Accesorios", 6000, 14000)
            ],
            "Aditivos": [
                ("Aditivo Motor", 4000, 10000),
                ("Limpiador Inyectores", 5000, 12000),
                ("Aditivo Radiador", 3000, 8000),
                ("Aditivo Combustible", 3500, 9000),
                ("Tratamiento Motor", 6000, 15000)
            ]
        }

        # Contador para SKUs por combinación fabricante-categoría
        sku_counters = {}
        productos_insertados = 0

        for i in range(cantidad):
            # Seleccionar categoría y fabricante
            cat_id = random.choice(list(categorias.keys()))
            fab_id = random.choice(list(fabricantes.keys()))

            categoria_nombre = categorias[cat_id]
            fabricante_nombre = fabricantes[fab_id]

            # Generar SKU estructurado
            fab_prefix = fabricante_nombre[:3].upper()
            cat_prefix = categoria_nombre[:3].upper()
            combo_key = f"{fab_prefix}-{cat_prefix}"

            current_seq = sku_counters.get(combo_key, 0) + 1
            sku_counters[combo_key] = current_seq
            sku = f"{combo_key}-{current_seq:04d}"

            # Seleccionar producto base según categoría
            if categoria_nombre in productos_por_categoria:
                producto_base = random.choice(productos_por_categoria[categoria_nombre])
                nombre_base, costo_base, precio_base = producto_base

                # Añadir variabilidad
                variacion = random.uniform(0.8, 1.2)
                costo_unitario = int(costo_base * variacion)
                precio_venta = int(precio_base * variacion)

                # Generar nombre con especificaciones
                specs = ["Pro", "Premium", "Standard", "HD", "Performance"]
                nombre = f"{nombre_base} {fabricante_nombre} {random.choice(specs)}"

            else:
                # Para categorías sin plantilla, generar genérico
                nombre = f"Producto {categoria_nombre} {fabricante_nombre} {i+1:03d}"
                costo_unitario = random.randint(5000, 50000)
                precio_venta = int(costo_unitario * random.uniform(1.3, 2.0))

            stock_inicial = 0  # Se llenará después
            ubicacion_id = random.choice(ubi_ids)

            try:
                cursor.execute("""
                    INSERT INTO "Productos"
                    (nombre, sku, costo_unitario, precio_venta, stock, categoria_id, fabricante_id, ubicacion_id, eliminado)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
                """, (nombre, sku, costo_unitario, precio_venta, stock_inicial, cat_id, fab_id, ubicacion_id, False))
                productos_insertados += 1

            except psycopg2.IntegrityError as e:
                print(f"⚠️  Error insertando producto {sku}: {e}")
                continue

    conn.commit()
    print(f"✅ {productos_insertados} productos insertados.")

def registrar_movimientos_stock_inicial(conn):
    """Registra el stock inicial de todos los productos"""
    with conn.cursor() as cursor:
        print("📦 Registrando stock inicial...")

        cursor.execute('SELECT producto_id, ubicacion_id FROM "Productos" WHERE eliminado = FALSE;')
        productos = cursor.fetchall()

        movimientos_insertados = 0

        for prod_id, ubi_id in productos:
            cantidad_inicial = random.randint(10, 150)

            try:
                # Insertar movimiento de stock
                cursor.execute("""
                    INSERT INTO "MovimientosInventario"
                    (tipo, cantidad, producto_id, ubicacion_id)
                    VALUES ('compra_inicial', %s, %s, %s);
                """, (cantidad_inicial, prod_id, ubi_id))

                # Actualizar stock del producto
                cursor.execute(
                    'UPDATE "Productos" SET stock = stock + %s WHERE producto_id = %s;',
                    (cantidad_inicial, prod_id)
                )

                movimientos_insertados += 1

            except psycopg2.Error as e:
                print(f"⚠️  Error registrando stock inicial para producto {prod_id}: {e}")
                continue

    conn.commit()
    print(f"✅ Stock inicial registrado para {movimientos_insertados} productos.")

def registrar_ventas_periodo(conn):
    """Registra ventas realistas para un período de 3 años"""
    with conn.cursor() as cursor:
        print("💰 Registrando ventas para período de 3 años...")

        # Obtener datos necesarios
        cursor.execute('SELECT rut FROM "Clientes";')
        cliente_ruts = [row[0] for row in cursor.fetchall()]

        cursor.execute("""
            SELECT producto_id, precio_venta, stock
            FROM "Productos"
            WHERE stock > 0 AND eliminado = FALSE
            ORDER BY producto_id;
        """)
        productos_disponibles = cursor.fetchall()

        if not productos_disponibles:
            print("⚠️  No hay productos con stock para vender.")
            return

        # Configurar período
        end_date = datetime.date.today()
        start_date = end_date - relativedelta(years=3)

        total_ventas = 0
        total_productos_vendidos = 0
        current_month_start = datetime.date(start_date.year, start_date.month, 1)

        while current_month_start < end_date:
            # Más ventas en algunos meses (temporada alta)
            if current_month_start.month in [3, 4, 10, 11, 12]:  # Temporada alta
                num_ventas_mes = random.randint(45, 65)
            else:
                num_ventas_mes = random.randint(25, 45)

            print(f"  📅 Procesando {current_month_start.strftime('%Y-%m')}: {num_ventas_mes} ventas...")

            for _ in range(num_ventas_mes):
                try:
                    # Datos de la venta
                    cliente_rut = random.choice(cliente_ruts)
                    boleta = f"BOL-{random.randint(100000, 999999)}"

                    # Fecha aleatoria del mes
                    days_in_month = (current_month_start + relativedelta(months=1) - datetime.timedelta(days=1)).day
                    random_day = random.randint(1, days_in_month)
                    fecha = datetime.datetime(
                        current_month_start.year,
                        current_month_start.month,
                        random_day,
                        random.randint(8, 18),  # Horario comercial
                        random.randint(0, 59)
                    )

                    # Crear venta
                    cursor.execute("""
                        INSERT INTO "Ventas" (boleta_numero, fecha, cliente_rut)
                        VALUES (%s, %s, %s) RETURNING venta_id;
                    """, (boleta, fecha, cliente_rut))
                    venta_id = cursor.fetchone()[0]

                    # Productos en esta venta (1-4 productos por venta)
                    num_productos_en_venta = random.randint(1, 4)
                    productos_en_venta = random.sample(productos_disponibles,
                                                     min(num_productos_en_venta, len(productos_disponibles)))

                    for prod_id, precio, stock_actual in productos_en_venta:
                        cantidad = random.randint(1, min(3, stock_actual))

                        if cantidad <= 0:
                            continue

                        # Verificar stock actual en BD
                        cursor.execute('SELECT stock FROM "Productos" WHERE producto_id = %s;', (prod_id,))
                        stock_bd = cursor.fetchone()
                        if not stock_bd or stock_bd[0] < cantidad:
                            continue

                        subtotal = cantidad * precio

                        # Insertar detalle de venta
                        cursor.execute("""
                            INSERT INTO "DetallesVenta"
                            (venta_id, producto_id, cantidad, precio_unitario, subtotal)
                            VALUES (%s, %s, %s, %s, %s);
                        """, (venta_id, prod_id, cantidad, precio, subtotal))

                        # Actualizar stock
                        cursor.execute(
                            'UPDATE "Productos" SET stock = stock - %s WHERE producto_id = %s;',
                            (cantidad, prod_id)
                        )

                        # Registrar movimiento de inventario
                        cursor.execute("""
                            INSERT INTO "MovimientosInventario"
                            (tipo, cantidad, producto_id, fecha_movimiento)
                            VALUES ('venta_cliente', %s, %s, %s);
                        """, (cantidad, prod_id, fecha))

                        total_productos_vendidos += cantidad

                    total_ventas += 1

                except psycopg2.Error as e:
                    print(f"⚠️  Error en venta: {e}")
                    continue

            # Avanzar al siguiente mes
            current_month_start += relativedelta(months=1)

            # Commit cada mes para evitar transacciones muy largas
            conn.commit()

    print(f"✅ {total_ventas} ventas registradas, {total_productos_vendidos} productos vendidos.")

def registrar_movimientos_adicionales(conn):
    """Registra movimientos adicionales de inventario (compras, ajustes)"""
    with conn.cursor() as cursor:
        print("📋 Registrando movimientos adicionales de inventario...")

        cursor.execute('SELECT producto_id FROM "Productos" WHERE eliminado = FALSE;')
        productos = [row[0] for row in cursor.fetchall()]

        if not productos:
            print("⚠️  No hay productos para movimientos adicionales.")
            return

        movimientos_insertados = 0

        # Generar movimientos aleatorios en los últimos 2 años
        end_date = datetime.date.today()
        start_date = end_date - relativedelta(years=2)

        # Obtener ubicaciones válidas para asignar a compras y ajustes
        cursor.execute('SELECT ubicacion_id FROM "Ubicaciones";')
        ubicaciones = [row[0] for row in cursor.fetchall()]
        if not ubicaciones:
            raise Exception("No hay ubicaciones disponibles para asignar a movimientos.")

        # Compras a proveedores (restock)
        for _ in range(150):  # 150 compras en 2 años
            try:
                prod_id = random.choice(productos)
                cantidad = random.randint(5, 50)
                ubicacion_id = random.choice(ubicaciones)

                # Fecha aleatoria
                days_diff = (end_date - start_date).days
                random_days = random.randint(0, days_diff)
                fecha = start_date + datetime.timedelta(days=random_days)
                fecha_dt = datetime.datetime.combine(fecha, datetime.time(random.randint(8, 17), random.randint(0, 59)))

                cursor.execute("""
                    INSERT INTO "MovimientosInventario"
                    (tipo, cantidad, producto_id, fecha_movimiento, ubicacion_id)
                    VALUES ('compra_proveedor', %s, %s, %s, %s);
                """, (cantidad, prod_id, fecha_dt, ubicacion_id))

                # Actualizar stock
                cursor.execute(
                    'UPDATE "Productos" SET stock = stock + %s WHERE producto_id = %s;',
                    (cantidad, prod_id)
                )

                movimientos_insertados += 1

            except psycopg2.Error as e:
                print(f"⚠️  Error en compra: {e}")
                continue

        # Ajustes de inventario positivos
        for _ in range(30):
            try:
                prod_id = random.choice(productos)
                cantidad = random.randint(1, 10)
                ubicacion_id = random.choice(ubicaciones)

                days_diff = (end_date - start_date).days
                random_days = random.randint(0, days_diff)
                fecha = start_date + datetime.timedelta(days=random_days)
                fecha_dt = datetime.datetime.combine(fecha, datetime.time(random.randint(8, 17), random.randint(0, 59)))

                cursor.execute("""
                    INSERT INTO "MovimientosInventario"
                    (tipo, cantidad, producto_id, fecha_movimiento, ubicacion_id)
                    VALUES ('ajuste_positivo', %s, %s, %s, %s);
                """, (cantidad, prod_id, fecha_dt, ubicacion_id))

                cursor.execute(
                    'UPDATE "Productos" SET stock = stock + %s WHERE producto_id = %s;',
                    (cantidad, prod_id)
                )

                movimientos_insertados += 1

            except psycopg2.Error as e:
                print(f"⚠️  Error en ajuste positivo: {e}")
                continue

        # Ajustes de inventario negativos (pérdidas, daños)
        for _ in range(20):
            try:
                prod_id = random.choice(productos)

                # Verificar stock actual antes del ajuste negativo
                cursor.execute('SELECT stock FROM "Productos" WHERE producto_id = %s;', (prod_id,))
                stock_actual = cursor.fetchone()[0]

                if stock_actual <= 0:
                    continue

                cantidad = random.randint(1, min(5, stock_actual))
                ubicacion_id = random.choice(ubicaciones)

                days_diff = (end_date - start_date).days
                random_days = random.randint(0, days_diff)
                fecha = start_date + datetime.timedelta(days=random_days)
                fecha_dt = datetime.datetime.combine(fecha, datetime.time(random.randint(8, 17), random.randint(0, 59)))

                cursor.execute("""
                    INSERT INTO "MovimientosInventario"
                    (tipo, cantidad, producto_id, fecha_movimiento, ubicacion_id)
                    VALUES ('ajuste_negativo', %s, %s, %s, %s);
                """, (cantidad, prod_id, fecha_dt, ubicacion_id))

                cursor.execute(
                    'UPDATE "Productos" SET stock = stock - %s WHERE producto_id = %s;',
                    (cantidad, prod_id)
                )

                movimientos_insertados += 1

            except psycopg2.Error as e:
                print(f"⚠️  Error en ajuste negativo: {e}")
                continue

        conn.commit()
        print(f"✅ {movimientos_insertados} movimientos adicionales registrados.")

def simular_algunos_productos_eliminados(conn):
    """Simula soft delete en algunos productos para probar la funcionalidad"""
    with conn.cursor() as cursor:
        print("🗑️  Simulando eliminación de algunos productos...")

        # Obtener productos que no tienen ventas recientes
        cursor.execute("""
            SELECT p.producto_id, p.nombre
            FROM "Productos" p
            WHERE p.eliminado = FALSE
            AND p.producto_id NOT IN (
                SELECT DISTINCT dv.producto_id
                FROM "DetallesVenta" dv
                JOIN "Ventas" v ON dv.venta_id = v.venta_id
                WHERE v.fecha >= CURRENT_DATE - INTERVAL '6 months'
            )
            ORDER BY RANDOM()
            LIMIT 15;
        """)

        productos_a_eliminar = cursor.fetchall()
        productos_eliminados = 0

        for prod_id, nombre in productos_a_eliminar:
            try:
                cursor.execute("""
                    UPDATE "Productos"
                    SET eliminado = TRUE, fecha_eliminacion = CURRENT_TIMESTAMP
                    WHERE producto_id = %s;
                """, (prod_id,))
                productos_eliminados += 1

            except psycopg2.Error as e:
                print(f"⚠️  Error eliminando producto {prod_id}: {e}")
                continue

        conn.commit()
        print(f"✅ {productos_eliminados} productos marcados como eliminados.")

def validar_datos_insertados(conn):
    """Valida que los datos se insertaron correctamente"""
    with conn.cursor() as cursor:
        print("\n📊 RESUMEN DE DATOS INSERTADOS:")
        print("-" * 50)

        tablas_resumen = [
            ('Categorias', 'Categorías'),
            ('Fabricantes', 'Fabricantes'),
            ('Ubicaciones', 'Ubicaciones'),
            ('Clientes', 'Clientes'),
            ('Productos', 'Productos (Total)'),
            ('Ventas', 'Ventas'),
            ('DetallesVenta', 'Detalles de Venta'),
            ('MovimientosInventario', 'Movimientos de Inventario')
        ]

        for tabla, nombre in tablas_resumen:
            cursor.execute(f'SELECT COUNT(*) FROM "{tabla}";')
            count = cursor.fetchone()[0]
            print(f"{nombre:.<30} {count:>10,}")

        # Estadísticas adicionales
        cursor.execute('SELECT COUNT(*) FROM "Productos" WHERE eliminado = FALSE;')
        productos_activos = cursor.fetchone()[0]
        print(f"{'Productos Activos':.<30} {productos_activos:>10,}")

        cursor.execute('SELECT COUNT(*) FROM "Productos" WHERE eliminado = TRUE;')
        productos_eliminados = cursor.fetchone()[0]
        print(f"{'Productos Eliminados':.<30} {productos_eliminados:>10,}")

        cursor.execute('SELECT COALESCE(SUM(stock), 0) FROM "Productos" WHERE eliminado = FALSE;')
        stock_total = cursor.fetchone()[0]
        print(f"{'Stock Total':.<30} {stock_total:>10,}")

        # Validar tipos de movimiento
        print(f"\n📋 TIPOS DE MOVIMIENTO:")
        cursor.execute('SELECT tipo, COUNT(*) FROM "MovimientosInventario" GROUP BY tipo ORDER BY tipo;')
        for tipo, count in cursor.fetchall():
            print(f"  {tipo:.<25} {count:>10,}")

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🏪 POBLANDO BASE DE DATOS RELACIONAL - LUBRI-EXPRESS")
    print("="*60)

    conn = get_db_connection("transaccional")  # Conecta a la base transaccional
    if not conn:
        print("❌ No se pudo conectar a la base de datos")
        sys.exit(1)
    # Debug: mostrar DSN y search_path
    try:
        print("🔗 Conectado a:", conn.get_dsn_parameters())
        with conn.cursor() as cur:
            cur.execute("SHOW search_path;")
            print("🔎 search_path:", cur.fetchone())
    except Exception as e:
        print("⚠️ Error mostrando DSN/search_path:", e)

    try:
        print("🚀 Iniciando proceso de inserción de datos...")

        limpiar_tablas(conn)
        insertar_catalogos(conn)
        insertar_clientes(conn, 200)  # 200 clientes
        insertar_productos(conn, 350)  # 350 productos
        registrar_movimientos_stock_inicial(conn)
        registrar_ventas_periodo(conn)
        registrar_movimientos_adicionales(conn)
        simular_algunos_productos_eliminados(conn)
        validar_datos_insertados(conn)

        print("\n" + "="*60)
        print("✅ PROCESO COMPLETADO EXITOSAMENTE")
        print("💡 Ahora puedes ejecutar el ETL con: python src/etl.py")
        print("="*60)

    except psycopg2.Error as e:
        print(f"❌ Error de base de datos: {e}")
        conn.rollback()
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        conn.rollback()
    finally:
        conn.close()
        print("\n🔌 Conexión cerrada.")
