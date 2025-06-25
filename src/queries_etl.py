# src/queries_etl.py - VERSIÓN CORREGIDA
"""
Queries SQL para el proceso ETL de base relacional a dimensional
Versión corregida con validaciones y mejor manejo de errores
"""

# ============================================================================
# QUERIES DE LIMPIEZA
# ============================================================================

TRUNCATE_HECHOS_STOCK = 'TRUNCATE TABLE "hechos_stock" RESTART IDENTITY CASCADE;'
TRUNCATE_HECHOS_VENTAS = 'TRUNCATE TABLE "hechos_ventas" RESTART IDENTITY CASCADE;'
TRUNCATE_PRODUCTOS = 'TRUNCATE TABLE "productos" RESTART IDENTITY CASCADE;'
TRUNCATE_CLIENTE = 'TRUNCATE TABLE "cliente" RESTART IDENTITY CASCADE;'
TRUNCATE_UBICACIONES = 'TRUNCATE TABLE "ubicaciones" RESTART IDENTITY CASCADE;'
TRUNCATE_CATEGORIAS = 'TRUNCATE TABLE "categorias" RESTART IDENTITY CASCADE;'
TRUNCATE_FABRICANTES = 'TRUNCATE TABLE "fabricantes" RESTART IDENTITY CASCADE;'

# ============================================================================
# QUERIES DE LECTURA DESDE BASE ORIGEN (RELACIONAL)
# ============================================================================

GET_TIPOS_MOVIMIENTO_SQL = """
SELECT id, tipo_movimiento
FROM dim_movimiento
ORDER BY id;
"""

GET_FABRICANTES_ORIGEN_SQL = """
SELECT fabricante_id, nombre
FROM "Fabricantes"
ORDER BY fabricante_id;
"""

GET_CATEGORIAS_ORIGEN_SQL = """
SELECT categoria_id, nombre
FROM "Categorias"
ORDER BY categoria_id;
"""

GET_UBICACIONES_ORIGEN_SQL = """
SELECT ubicacion_id, descripcion
FROM "Ubicaciones"
ORDER BY ubicacion_id;
"""

GET_CLIENTES_ORIGEN_SQL = """
SELECT rut, nombre_completo
FROM "Clientes"
ORDER BY rut;
"""

GET_PRODUCTOS_ACTIVOS_ORIGEN_SQL = """
SELECT
    producto_id,
    nombre,
    fabricante_id,
    categoria_id,
    sku,
    COALESCE(costo_unitario, 0) as costo_unitario,
    precio_venta,
    COALESCE(stock, 0) as stock,
    ubicacion_id
FROM "Productos"
WHERE eliminado = FALSE
ORDER BY producto_id;
"""

GET_VENTAS_DETALLE_ORIGEN_SQL = """
SELECT
    v.venta_id,
    v.boleta_numero,
    v.fecha,
    v.cliente_rut,
    dv.producto_id,
    dv.cantidad,
    dv.precio_unitario,
    dv.subtotal
FROM "Ventas" v
JOIN "DetallesVenta" dv ON v.venta_id = dv.venta_id
JOIN "Productos" p ON dv.producto_id = p.producto_id
WHERE p.eliminado = FALSE  -- Solo productos activos
ORDER BY v.fecha, v.venta_id;
"""

GET_MOVIMIENTOS_STOCK_ORIGEN_SQL = """
SELECT
    mi.movimiento_id,
    mi.fecha_movimiento,
    mi.tipo,
    mi.cantidad,
    mi.producto_id,
    mi.ubicacion_id
FROM "MovimientosInventario" mi
JOIN "Productos" p ON mi.producto_id = p.producto_id
WHERE p.eliminado = FALSE  -- Solo productos activos
ORDER BY mi.fecha_movimiento;
"""

GET_COSTO_PRODUCTO_SQL = """
SELECT COALESCE(costo_unitario, 0)
FROM "Productos"
WHERE producto_id = %s;
"""

# ============================================================================
# QUERIES DE INSERCIÓN EN BASE DESTINO (DIMENSIONAL)
# ============================================================================

INSERT_FABRICANTE_DESTINO_SQL = """
INSERT INTO fabricantes (nombre_fabricante)
VALUES (%s)
RETURNING fabricante_id;
"""

INSERT_CATEGORIA_DESTINO_SQL = """
INSERT INTO categorias (nombre_categoria)
VALUES (%s)
RETURNING categoria_id;
"""

INSERT_UBICACION_DESTINO_SQL = """
INSERT INTO ubicaciones (codigo_ubicacion, descripcion_ubicacion)
VALUES (%s, %s)
RETURNING ubicacion_id;
"""

INSERT_CLIENTE_DESTINO_SQL = """
INSERT INTO cliente (cliente_id, rut, nombre_cliente)
VALUES (%s, %s, %s);
"""

INSERT_PRODUCTO_DESTINO_SQL = """
INSERT INTO productos
(producto_id, nombre_articulo, fabricante_fk, categoria_fk,
 sku, costo, precio, stock_actual, ubicacion_fk)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
"""

INSERT_VENTA_DESTINO_SQL = """
INSERT INTO hechos_ventas
(nro_boleta, producto_fk, fecha, cliente_fk, cantidad, costo_unitario, total_venta)
VALUES (%s, %s, %s, %s, %s, %s, %s);
"""

INSERT_MOVIMIENTO_STOCK_DESTINO_SQL = """
INSERT INTO hechos_stock
(producto_fk, fecha, ubicacion_fk, tipo_movimiento_fk, cantidad)
VALUES (%s, %s, %s, %s, %s);
"""

# ============================================================================
# QUERIES DE VALIDACIÓN
# ============================================================================

CHECK_PRODUCTO_EXISTS_SQL = """
SELECT 1 FROM productos WHERE producto_id = %s;
"""

CHECK_FABRICANTE_EXISTS_SQL = """
SELECT 1 FROM fabricantes WHERE fabricante_id = %s;
"""

CHECK_CATEGORIA_EXISTS_SQL = """
SELECT 1 FROM categorias WHERE categoria_id = %s;
"""

CHECK_CLIENTE_EXISTS_SQL = """
SELECT 1 FROM cliente WHERE cliente_id = %s;
"""

# ============================================================================
# QUERIES DE ACTUALIZACIÓN
# ============================================================================

UPDATE_STOCK_ACTUAL_SQL = """
WITH StockCalculado AS (
    SELECT
        producto_fk,
        SUM(cantidad) AS stock_calculado
    FROM hechos_stock
    GROUP BY producto_fk
)
UPDATE productos p
SET stock_actual = GREATEST(COALESCE(sc.stock_calculado, 0), 0)
FROM StockCalculado sc
WHERE p.producto_id = sc.producto_fk;
"""

UPDATE_STOCK_CERO_SQL = """
UPDATE productos
SET stock_actual = 0
WHERE producto_id NOT IN (
    SELECT DISTINCT producto_fk
    FROM hechos_stock
);
"""

# ============================================================================
# QUERIES DE CONTEO PARA VALIDACIÓN FINAL
# ============================================================================

COUNT_PRODUCTOS_SQL = "SELECT COUNT(*) FROM productos;"
COUNT_FABRICANTES_SQL = "SELECT COUNT(*) FROM fabricantes;"
COUNT_CATEGORIAS_SQL = "SELECT COUNT(*) FROM categorias;"
COUNT_UBICACIONES_SQL = "SELECT COUNT(*) FROM ubicaciones;"
COUNT_CLIENTES_SQL = "SELECT COUNT(*) FROM cliente;"
COUNT_VENTAS_SQL = "SELECT COUNT(*) FROM hechos_ventas;"
COUNT_MOVIMIENTOS_SQL = "SELECT COUNT(*) FROM hechos_stock;"

# ============================================================================
# QUERIES DE VALIDACIÓN DE INTEGRIDAD
# ============================================================================

VALIDAR_PRODUCTOS_SIN_FABRICANTE_SQL = """
SELECT COUNT(*)
FROM productos p
LEFT JOIN fabricantes f ON p.fabricante_fk = f.fabricante_id
WHERE f.fabricante_id IS NULL;
"""

VALIDAR_PRODUCTOS_SIN_CATEGORIA_SQL = """
SELECT COUNT(*)
FROM productos p
LEFT JOIN categorias c ON p.categoria_fk = c.categoria_id
WHERE c.categoria_id IS NULL;
"""

VALIDAR_VENTAS_SIN_PRODUCTO_SQL = """
SELECT COUNT(*)
FROM hechos_ventas v
LEFT JOIN productos p ON v.producto_fk = p.producto_id
WHERE p.producto_id IS NULL;
"""

VALIDAR_MOVIMIENTOS_SIN_PRODUCTO_SQL = """
SELECT COUNT(*)
FROM hechos_stock s
LEFT JOIN productos p ON s.producto_fk = p.producto_id
WHERE p.producto_id IS NULL;
"""

VALIDAR_MOVIMIENTOS_SIN_TIPO_SQL = """
SELECT COUNT(*)
FROM hechos_stock s
LEFT JOIN dim_movimiento d ON s.tipo_movimiento_fk = d.id
WHERE d.id IS NULL;
"""

# ============================================================================
# MAPEO DE TIPOS DE MOVIMIENTO
# ============================================================================

# Mapeo desde base relacional a base dimensional
TIPO_MOVIMIENTO_MAP = {
    'compra_inicial': 'ENTRADA_INI',
    'venta_cliente': 'SALIDA_VTA',
    'compra_proveedor': 'ENTRADA_COMPRA',
    'ajuste_positivo': 'AJUSTE_INV_POS',
    'ajuste_negativo': 'AJUSTE_INV_NEG'
}

# ============================================================================
# QUERIES ADICIONALES PARA DEBUGGING Y MONITOREO
# ============================================================================

GET_SAMPLE_PRODUCTOS_ORIGEN_SQL = """
SELECT producto_id, nombre, eliminado
FROM "Productos"
ORDER BY producto_id
LIMIT 5;
"""

GET_SAMPLE_VENTAS_ORIGEN_SQL = """
SELECT v.venta_id, v.fecha, dv.producto_id, dv.cantidad
FROM "Ventas" v
JOIN "DetallesVenta" dv ON v.venta_id = dv.venta_id
ORDER BY v.fecha DESC
LIMIT 5;
"""

GET_SAMPLE_MOVIMIENTOS_ORIGEN_SQL = """
SELECT movimiento_id, tipo, producto_id, cantidad, fecha_movimiento
FROM "MovimientosInventario"
ORDER BY fecha_movimiento DESC
LIMIT 5;
"""

# ============================================================================
# QUERIES PARA REPORTES POST-ETL
# ============================================================================

REPORTE_PRODUCTOS_MIGRADOS_SQL = """
SELECT
    COUNT(*) as total_productos,
    COUNT(CASE WHEN stock_actual > 0 THEN 1 END) as con_stock,
    COUNT(CASE WHEN stock_actual = 0 THEN 1 END) as sin_stock,
    AVG(stock_actual) as stock_promedio,
    SUM(stock_actual) as stock_total
FROM productos;
"""

REPORTE_VENTAS_POR_AÑO_SQL = """
SELECT
    EXTRACT(YEAR FROM fecha) as año,
    COUNT(*) as total_ventas,
    SUM(total_venta) as total_ingresos,
    AVG(total_venta) as venta_promedio
FROM hechos_ventas
GROUP BY EXTRACT(YEAR FROM fecha)
ORDER BY año;
"""

REPORTE_MOVIMIENTOS_POR_TIPO_SQL = """
SELECT
    dm.tipo_movimiento,
    dm.descripcion_movimiento,
    COUNT(*) as total_movimientos,
    SUM(hs.cantidad) as cantidad_total
FROM hechos_stock hs
JOIN dim_movimiento dm ON hs.tipo_movimiento_fk = dm.id
GROUP BY dm.tipo_movimiento, dm.descripcion_movimiento
ORDER BY total_movimientos DESC;
"""
